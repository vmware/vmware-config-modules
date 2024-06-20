from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.datastore_unique_name_policy import DATASTORE_NAME_KEY
from config_modules_vmware.controllers.vcenter.datastore_unique_name_policy import DatastoreUniqueNamePolicy
from config_modules_vmware.controllers.vcenter.datastore_unique_name_policy import NON_COMPLIANT_DATASTORE_NAME
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDatastoreUniqueNamePolicy:
    def setup_method(self):
        self.controller = DatastoreUniqueNamePolicy()
        self.compliant_datastore_configs = [
            {
                "datacenter_name": "Datacenter1",
                "cluster_name": "Cluster-1",
                "datastore_name": "DatastoreX",
            },
            {
                "datacenter_name": "Datacenter2",
                "cluster_name": "Cluster-2",
                "datastore_name": "DatastoreY",
            },
            {
                "datacenter_name": "Datacenter3",
                "cluster_name": "ClusterC",
                "datastore_name": "DatastoreZ",
            },
        ]
        self.non_compliant_datastore_configs = [
            {
                "datacenter_name": "Datacenter1",
                "cluster_name": "Cluster-1",
                "datastore_name": "vsanDatastore",
            },
            {
                "datacenter_name": "Datacenter2",
                "cluster_name": "Cluster-2",
                "datastore_name": "vsanDatastore (1)",
            },
            {
                "datacenter_name": "Datacenter3",
                "cluster_name": "ClusterC",
                "datastore_name": "DatastoreZ",
            },
        ]
        self.desired_value = True
        # Pyvmomi type MagicMock objects
        self.compliant_datastore_mocks = [
            self.get_datacenter_pyvmomi_mock(ds_spec) for ds_spec in self.compliant_datastore_configs
        ]
        self.non_compliant_datastore_mocks = [
            self.get_datacenter_pyvmomi_mock(ds_spec) for ds_spec in self.non_compliant_datastore_configs
        ]

    def get_datacenter_pyvmomi_mock(self, datastore_spec):
        """
            Create mock object for Datacenter.
        :param datastore_spec:
        :return:
        """
        datacenter_mock = MagicMock()
        datacenter_mock.name = datastore_spec.get("datacenter_name")
        datastore = MagicMock()
        datastore.summary.type = "vsan"
        datastore.name = datastore_spec.get("datastore_name")
        host = MagicMock()
        host.key.parent.name = datastore_spec.get("cluster_name")
        datastore.host = [host]
        datacenter_mock.datastore = [datastore]
        return datacenter_mock

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_datastore_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_datastore_configs
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get datastore config")

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_datastore_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.desired_value)
        assert result == RemediateStatus.SKIPPED
        assert errors == [consts.REMEDIATION_SKIPPED_MESSAGE]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_datastore_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs = [
            config
            for config in self.non_compliant_datastore_configs if
            config.get(DATASTORE_NAME_KEY) == NON_COMPLIANT_DATASTORE_NAME
        ]
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: self.desired_value,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_datastore_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs = [
            config
            for config in self.non_compliant_datastore_configs if
            config.get(DATASTORE_NAME_KEY) == NON_COMPLIANT_DATASTORE_NAME
        ]
        expected_errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: expected_errors, consts.DESIRED: self.desired_value, consts.CURRENT: non_compliant_configs}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_datastore_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_already_desired(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_datastore_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.desired_value)
        assert result == expected_result
