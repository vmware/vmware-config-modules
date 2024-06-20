from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.vsan_iscsi_targets_mchap_config import VsanIscsiTargetsMchapConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestVsanIscsiTargetsMchapConfig:
    def setup_method(self):
        self.controller = VsanIscsiTargetsMchapConfig()
        self.get_output = [
            {
                'SDDC-Datacenter/test_cluster_02': 'CHAP_Mutual',
            },
            {
                'SDDC-Datacenter/test_cluster_02/target_01': 'CHAP_Mutual',
            },
            {
                'SDDC-Datacenter/test_cluster_03': 'CHAP_Mutual',
            },
            {
                'SDDC-Datacenter/test_cluster_03/target_01': 'CHAP_Mutual',
            },
        ]
        self.control_desired_value = {
            'global': 'CHAP_Mutual',
            'SDDC-Datacenter/test_cluster_02': 'CHAP_Mutual',
        }
        self.compliant_value = self.control_desired_value
        self.non_compliant_value = {
            'SDDC-Datacenter/test_cluster_02': 'CHAP'
        }
        self.non_compliant_cluster_configs = [
            {
                "datacenter_name": "SDDC-Datacenter",
                "cluster_name": "test_cluster_01",
                "auth_type": "CHAP",
            },
        ]
        self.compliant_cluster_configs = [
            {
                "datacenter_name": "SDDC-Datacenter",
                "cluster_name": "test_cluster_02",
                "auth_type": "CHAP_Mutual",
            },
            {
                "datacenter_name": "SDDC-Datacenter",
                "cluster_name": "test_cluster_03",
                "auth_type": "CHAP_Mutual",
            },
        ]
        self.all_vsan_enabled_mock_cluster_refs = \
            self.create_mock_objs_all_vsan_clusters(self.compliant_cluster_configs)

    def create_mock_objs_all_vsan_clusters(self, cluster_iscsi_configs):
        """
        Create pyvmomi like mock object for all clusters
        :param cluster_iscsi_configs:
        :return:
        """
        all_vsan_cluster_refs = []
        for cluster_iscsi_config in cluster_iscsi_configs:
            cluster_ref = MagicMock()
            cluster_ref.name = cluster_iscsi_config.get("cluster_name")
            cluster_ref.parent.parent.name = cluster_iscsi_config.get("datacenter_name")
            all_vsan_cluster_refs.append(cluster_ref)
        return all_vsan_cluster_refs

    def get_mock_targets_obj(self):
        mock_vsan_iscsi_targets = MagicMock(spec=vim.cluster.VsanIscsiTargetSystem)
        mock_vsan_iscsi_target = MagicMock(spec=vim.cluster.VsanIscsiTarget)
        mock_vsan_iscsi_target.authSpec = MagicMock(spec=vim.cluster.VsanIscsiTargetAuthSpec)
        mock_vsan_iscsi_target.authSpec.authType = "CHAP_Mutual"
        mock_vsan_iscsi_target.alias = "target_01"
        mock_vsan_iscsi_targets.GetIscsiTargets.return_value = [mock_vsan_iscsi_target]
        return mock_vsan_iscsi_targets

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_get_success(self, mock_vc_vsan_vmomi_client, mock_vc_context):

        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_auth_type_for_cluster.return_value = "CHAP_Mutual"
        mock_vc_vsan_vmomi_client.is_vsan_iscsi_targets_enabled_for_cluster.return_value = True
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster.return_value = self.get_mock_targets_obj()

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.get_output
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_get_failed(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        # Setup Mock objects to raise an exception.
        expected_error = "test exception"
        expected_errors = [expected_error]

        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = Exception(expected_error)

        # Call Controller.
        result, errors = self.controller.get(mock_vc_context)

        # Assert expected results.
        assert result == []
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_get_no_datat(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        # Setup Mock objects to raise an exception.
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = []
        mock_vc_vsan_vmomi_client.is_vsan_iscsi_targets_enabled_for_cluster.return_value = False
        #mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster.return_value = self.get_mock_targets_obj()

        # Call Controller.
        result, errors = self.controller.get(mock_vc_context)

        # Assert expected results.
        assert result == []
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_set_skipped(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        # Setup Mock objects for successfully changing the value.
        expected_result = RemediateStatus.SKIPPED, [consts.REMEDIATION_SKIPPED_MESSAGE]

        # Call Controller.
        result = self.controller.set(mock_vc_context, self.compliant_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_remediate_skipped(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        # Setup Mock objects for successfully changing the value.
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_auth_type_for_cluster.return_value = "CHAP"
        mock_vc_vsan_vmomi_client.is_vsan_iscsi_targets_enabled_for_cluster.return_value = True
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster.return_value = self.get_mock_targets_obj()

        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE],
                           consts.DESIRED: self.control_desired_value,
                           consts.CURRENT: [{'SDDC-Datacenter/test_cluster_02': 'CHAP'}, \
                                        {'SDDC-Datacenter/test_cluster_02/target_01': 'CHAP_Mutual'}, \
                                        {'SDDC-Datacenter/test_cluster_03': 'CHAP'}, \
                                        {'SDDC-Datacenter/test_cluster_03/target_01': 'CHAP_Mutual'}]}

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_error = "test exception"
        expected_errors = [expected_error]
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = Exception(expected_error)

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_auth_type_for_cluster.return_value = "CHAP_Mutual"
        mock_vc_vsan_vmomi_client.is_vsan_iscsi_targets_enabled_for_cluster.return_value = True
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster.return_value = self.get_mock_targets_obj()

        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: expected_errors}

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_check_compliance_compliant_01(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = []

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_check_compliance_compliant_02(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_auth_type_for_cluster.return_value = "CHAP_Mutual"
        mock_vc_vsan_vmomi_client.is_vsan_iscsi_targets_enabled_for_cluster.return_value = True
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster.return_value = self.get_mock_targets_obj()

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_auth_type_for_cluster.return_value = "CHAP"
        mock_vc_vsan_vmomi_client.is_vsan_iscsi_targets_enabled_for_cluster.return_value = True
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster.return_value = self.get_mock_targets_obj()
        expected_result = {consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                           'current': [{'SDDC-Datacenter/test_cluster_02': 'CHAP'},\
                                       {'SDDC-Datacenter/test_cluster_02/target_01': 'CHAP_Mutual'},\
                                       {'SDDC-Datacenter/test_cluster_03': 'CHAP'},\
                                       {'SDDC-Datacenter/test_cluster_03/target_01': 'CHAP_Mutual'}],
                           'desired': self.control_desired_value}

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result
