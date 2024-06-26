from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.dv_pg_mac_address_change_policy import DESIRED_KEY
from config_modules_vmware.controllers.vcenter.dv_pg_mac_address_change_policy import DVPortGroupMacAddressChangePolicy
from config_modules_vmware.controllers.vcenter.utils.vc_port_group_utils import \
    get_non_compliant_security_policy_configs
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDVPortGroupMacAddressChangePolicy:
    def setup_method(self):
        self.controller = DVPortGroupMacAddressChangePolicy()
        self.compliant_dv_pgs = [
            {"switch_name": "SwitchB", "port_group_name": "dv_pg_PortGroup3", "allow_mac_address_change": False},
            {"switch_name": "SwitchC", "port_group_name": "dv_pg_PortGroup1", "allow_mac_address_change": False},
            {"switch_name": "SwitchA", "port_group_name": "dv_pg_PortGroup2", "allow_mac_address_change": False},
        ]
        self.non_compliant_dv_pgs = [
            {"switch_name": "SwitchB", "port_group_name": "dv_pg_PortGroup3", "allow_mac_address_change": True},
            {"switch_name": "SwitchC", "port_group_name": "dv_pg_PortGroup1", "allow_mac_address_change": True},
            {"switch_name": "SwitchA", "port_group_name": "dv_pg_PortGroup2", "allow_mac_address_change": False},
        ]
        self.nsx_back_dv_pg = [{"switch_name": "SwitchA", "port_group_name": "dv_pg_nsx", "allow_mac_address_change": False, "backing": "nsx"}]
        self.compliant_value = {
            "__GLOBAL__": {
                "allow_mac_address_change": False
            }
        }
        self.compliant_value_with_override = {
            "__GLOBAL__": {
                "allow_mac_address_change": False
            },
            "__OVERRIDES__": [
                {"switch_name": "SwitchA",
                 "port_group_name": "dv_pg_PortGroup2",
                 "allow_mac_address_change": True}
            ]
        }
        # Pyvmomi type MagicMock objects
        self.compliant_dv_pg_pyvmomi_mocks = [self.get_dv_port_group_mock_obj(pg_spec)
                                              for pg_spec in self.compliant_dv_pgs]
        self.compliant_dv_pg_pyvmomi_mocks.append(self.get_dv_port_group_mock_obj(self.nsx_back_dv_pg[0]))
        self.non_compliant_dv_pg_pyvmomi_mocks = [
            self.get_dv_port_group_mock_obj(pg_spec) for pg_spec in self.non_compliant_dv_pgs
        ]
        self.non_compliant_dv_pg_pyvmomi_mocks.append(self.get_dv_port_group_mock_obj(self.nsx_back_dv_pg[0]))
        # Bad mock to induce error
        self.dv_pg_mock_pyvmomi_bad_object = [
            self.get_dv_port_group_mock_obj(pg_spec, create_bad_mock=True) for pg_spec in self.non_compliant_dv_pgs
        ]

    def get_dv_port_group_mock_obj(self, pg_spec, create_bad_mock=False):
        """
        Create mock object for DV port group based on port group spec
        :param pg_spec:
        :param bad_mock:
        :return:
        """
        dv_pg_mock = MagicMock()
        dv_pg_mock.name = pg_spec.get("port_group_name")
        dv_pg_mock.config = MagicMock()
        dv_pg_mock.config.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
        dv_pg_mock.config.backingType = pg_spec.get("backing", "standard")
        dv_pg_mock.config.uplink = pg_spec.get("uplink", False)
        if not create_bad_mock:
            dv_pg_mock.config.configVersion = "24"
        dv_pg_mock.config.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()
        dv_pg_mock.config.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(
            value=pg_spec.get("allow_mac_address_change")
        )
        dv_pg_mock.config.distributedVirtualSwitch.name = pg_spec.get("switch_name")
        setattr(dv_pg_mock, "ReconfigureDVPortgroup_Task", MagicMock(return_value=True))
        return dv_pg_mock

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = self.compliant_dv_pg_pyvmomi_mocks
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_dv_pgs
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get DV PG config")

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dv_pg_pyvmomi_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success_with_override(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dv_pg_pyvmomi_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value_with_override)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to set MAC address change policy")

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dv_pg_pyvmomi_mocks
        mock_vc_vmomi_client.wait_for_task.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        expected_get_object_result = self.compliant_dv_pg_pyvmomi_mocks
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_get_object_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = get_non_compliant_security_policy_configs(
            self.non_compliant_dv_pgs,
            self.compliant_value,
            DESIRED_KEY
        )

        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: desired_configs,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dv_pg_pyvmomi_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant_overrides(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_items, desired_configs = get_non_compliant_security_policy_configs(
            self.non_compliant_dv_pgs,
            self.compliant_value_with_override,
            DESIRED_KEY
        )

        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_items,
            consts.DESIRED: desired_configs,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dv_pg_pyvmomi_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value_with_override)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_skipped_already_desired(self, mock_vc_vmomi_client, mock_vc_context):
        expected_get_object_result = self.compliant_dv_pg_pyvmomi_mocks
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ['Control already compliant']}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_get_object_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = get_non_compliant_security_policy_configs(
            self.non_compliant_dv_pgs,
            self.compliant_value,
            DESIRED_KEY
        )

        current_value = self.non_compliant_dv_pg_pyvmomi_mocks
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: desired_configs,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = current_value
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Get exception while remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception('For "configVersion" expected type str, but got MagicMock')
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.dv_pg_mock_pyvmomi_bad_object
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
