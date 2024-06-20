from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.datastore_transit_encryption_config import DatastoreTransitEncryptionPolicy
from config_modules_vmware.controllers.vcenter.datastore_transit_encryption_config import REKEY_INTERVAL_KEY
from config_modules_vmware.controllers.vcenter.datastore_transit_encryption_config import TRANSIT_ENCRYPTION_ENABLED
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDatastoreTransitEncryptionPolicy:
    def setup_method(self):
        self.controller = DatastoreTransitEncryptionPolicy()
        self.compliant_cluster_configs = [
            {
                "datacenter_name": "SDDC-Datacenter",
                "cluster_name": "SDDC-Cluster-1",
                "transit_encryption_enabled": True,
                "rekey_interval": 30
            },
            {
                "datacenter_name": "test-Datacenter",
                "cluster_name": "SDDC-Cluster-1",
                "transit_encryption_enabled": True,
                "rekey_interval": 30
            },
            {
                "datacenter_name": "test-Datacenter",
                "cluster_name": "SDDC-Cluster-2",
                "transit_encryption_enabled": True,
                "rekey_interval": 30
            }
        ]
        self.non_compliant_cluster_configs = [
            {
                "datacenter_name": "SDDC-Datacenter",
                "cluster_name": "SDDC-Cluster-1",
                "transit_encryption_enabled": False,
                "rekey_interval": 30
            },
            {
                "datacenter_name": "test-Datacenter",
                "cluster_name": "SDDC-Cluster-1",
                "transit_encryption_enabled": True,
                "rekey_interval": 1000
            },
            {
                "datacenter_name": "test-Datacenter",
                "cluster_name": "SDDC-Cluster-2",
                "transit_encryption_enabled": True,
                "rekey_interval": 3000
            }
        ]
        self.desired_value = {
            "rekey_interval": 30,
            "transit_encryption_enabled": True
        }

        self.compliant_mocked_vsan_ccs = [
            self.get_ccs_mock_cluster(cluster_spec) for cluster_spec in self.compliant_cluster_configs
        ]
        self.non_compliant_mocked_vsan_ccs = [
            self.get_ccs_mock_cluster(cluster_spec) for cluster_spec in self.non_compliant_cluster_configs
        ]

        self.all_vsan_enabled_mock_cluster_refs = \
            self.create_mock_objs_all_vsan_clusters(self.compliant_cluster_configs)
        self.all_vsan_enabled_mock_cluster_refs_non_compliant = \
            self.create_mock_objs_all_vsan_clusters(self.compliant_cluster_configs)

    def get_ccs_mock_cluster(self, cluster_spec):
        ccs_config = MagicMock()
        # Encryption config
        ccs_config.dataEncryptionConfig = MagicMock()
        ccs_config.dataEncryptionConfig.encryptionEnabled = True
        # Data in transit encryption configs
        ccs_config.dataInTransitEncryptionConfig = MagicMock()
        ccs_config.dataInTransitEncryptionConfig.enabled = cluster_spec.get("transit_encryption_enabled")
        ccs_config.dataInTransitEncryptionConfig.rekeyInterval = cluster_spec.get("rekey_interval")
        return ccs_config

    def create_mock_objs_all_vsan_clusters(self, cluster_specs):
        """
        Create pyvmomi like mock object for all clusters
        :param cluster_specs:
        :return:
        """
        all_vsan_cluster_refs = []
        for cluster_spec in cluster_specs:
            cluster_ref = MagicMock()
            cluster_ref.name = cluster_spec.get("cluster_name")
            cluster_ref.parent.parent.name = cluster_spec.get("datacenter_name")
            all_vsan_cluster_refs.append(cluster_ref)
        return all_vsan_cluster_refs

    def create_datacenter_mock(self, name):
        datacenter_mock = MagicMock()
        datacenter_mock.name = name
        return datacenter_mock

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.compliant_mocked_vsan_ccs
        mock_vc_vmomi_client.find_datacenter_for_obj.side_effect = [self.create_datacenter_mock(cluster_config["datacenter_name"]) for cluster_config in self.compliant_cluster_configs]
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_cluster_configs
        assert errors == []

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_error = Exception("Failed to get datastore config")

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = expected_error

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.non_compliant_mocked_vsan_ccs
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.desired_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_already_desired(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.compliant_mocked_vsan_ccs
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.desired_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []


    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failure(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_error = Exception("Failed to set transit encryption config")

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = expected_error

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.desired_value)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.compliant_mocked_vsan_ccs
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        non_compliant_configs = [
            config
            for config in self.non_compliant_cluster_configs
            if config.get(REKEY_INTERVAL_KEY) != self.desired_value.get(REKEY_INTERVAL_KEY)
               or config.get(TRANSIT_ENCRYPTION_ENABLED) != self.desired_value.get(TRANSIT_ENCRYPTION_ENABLED)
        ]
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: self.desired_value,
        }

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vmomi_client.find_datacenter_for_obj.side_effect = [self.create_datacenter_mock(cluster_config["datacenter_name"]) for cluster_config in self.non_compliant_cluster_configs]

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.non_compliant_mocked_vsan_ccs
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = expected_error

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_errors = []
        non_compliant_configs = [
            config
            for config in self.non_compliant_cluster_configs
            if config.get(REKEY_INTERVAL_KEY) != self.desired_value.get(REKEY_INTERVAL_KEY)
               or config.get(TRANSIT_ENCRYPTION_ENABLED) != self.desired_value.get(TRANSIT_ENCRYPTION_ENABLED)
        ]
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: self.desired_value,
        }

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.non_compliant_mocked_vsan_ccs + self.non_compliant_mocked_vsan_ccs
        mock_vc_vmomi_client.find_datacenter_for_obj.side_effect = [self.create_datacenter_mock(cluster_config["datacenter_name"]) for cluster_config in self.compliant_cluster_configs]
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_already_desired(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.compliant_mocked_vsan_ccs
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_get_failed(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_error = Exception("Exception occuring during get call")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = expected_error

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.desired_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_set_failed(self, mock_vc_vmomi_client, mock_vc_context, mock_vc_vsan_vmomi_client):
        expected_errors = Exception("Error occured while setting value")
        non_compliant_configs = [
            config
            for config in self.non_compliant_cluster_configs
            if config.get(REKEY_INTERVAL_KEY) != self.desired_value.get(REKEY_INTERVAL_KEY)
               or config.get(TRANSIT_ENCRYPTION_ENABLED) != self.desired_value.get(TRANSIT_ENCRYPTION_ENABLED)
        ]
        expected_result = {
            consts.STATUS: RemediateStatus.FAILED,
            consts.ERRORS: [str(expected_errors)]
        }

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs

        mock_vsan_ccs = MagicMock()
        mock_vsan_ccs.VsanClusterGetConfig.side_effect = self.non_compliant_mocked_vsan_ccs + [expected_errors]
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = mock_vsan_ccs

        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.desired_value)
        assert result == expected_result
