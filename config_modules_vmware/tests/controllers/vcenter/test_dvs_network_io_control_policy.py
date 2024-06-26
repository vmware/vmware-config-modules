from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.dvs_network_io_control_policy import DESIRED_KEY
from config_modules_vmware.controllers.vcenter.dvs_network_io_control_policy import DVSNetworkIOControlPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDVSNetworkIOControlPolicy:
    def setup_method(self):
        self.controller = DVSNetworkIOControlPolicy()
        self.compliant_value = {
            "__GLOBAL__": {
               "network_io_control_status": False
            }
        }

        self.compliant_value_with_overrides = {
            "__GLOBAL__": {
                "network_io_control_status": False
            },
            "__OVERRIDES__": [
                {
                    "switch_name": "SwitchC",
                    "network_io_control_status": True
                }
            ]
        }

        self.compliant_switch_configs = [
            {"switch_name": "SwitchB", "network_io_control_status": False},
            {"switch_name": "SwitchC", "network_io_control_status": False},
            {"switch_name": "SwitchA", "network_io_control_status": False},
        ]
        self.non_compliant_switch_configs = [
            {"switch_name": "SwitchB", "network_io_control_status": True},
            {"switch_name": "SwitchC", "network_io_control_status": False},
            {"switch_name": "SwitchA", "network_io_control_status": True},
        ]
        # Pyvmomi type MagicMock objects
        self.compliant_dvs_mocks = [self.create_dv_switch_mock_obj(pg_spec)
                                    for pg_spec in self.compliant_switch_configs]
        self.non_compliant_dvs_mocks = [
            self.create_dv_switch_mock_obj(pg_spec) for pg_spec in self.non_compliant_switch_configs
        ]
        # Bad mock to induce error
        self.dvs_mock_pyvmomi_bad_object = [
            self.create_dv_switch_mock_obj(pg_spec, bad_mock=True) for pg_spec in self.non_compliant_switch_configs
        ]

    def create_dv_switch_mock_obj(self, dv_spec, bad_mock=False):
        dvs_mock = MagicMock()
        dvs_mock.name = dv_spec.get("switch_name")
        dvs_mock.config = MagicMock()
        dvs_mock.config.healthCheckConfig = MagicMock()
        dvs_mock.config.networkResourceManagementEnabled = dv_spec.get("network_io_control_status")
        if not bad_mock:
            setattr(dvs_mock, "EnableNetworkResourceManagement", MagicMock(return_value=True))
        return dvs_mock

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_switch_configs
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get DV switch config")

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to set network I/O control policy")

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs = [
            config for config in self.non_compliant_switch_configs
            if config.get(DESIRED_KEY) != self.compliant_value.get("__GLOBAL__", {}).get(DESIRED_KEY)
        ]

        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: self.compliant_value,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
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
    def test_remediate_success_already_desired(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs = [
            config for config in self.non_compliant_switch_configs
            if config.get(DESIRED_KEY) != self.compliant_value.get("__GLOBAL__", {}).get(DESIRED_KEY)
        ]
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: self.compliant_value,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant_overrides(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_items = self.controller._DVSNetworkIOControlPolicy__get_non_compliant_configs(
            self.non_compliant_switch_configs,
            self.compliant_value_with_overrides)

        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_items,
            consts.DESIRED: self.compliant_value_with_overrides,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value_with_overrides)
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
    def test_remediate_success_with_overrides(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_items = self.controller._DVSNetworkIOControlPolicy__get_non_compliant_configs(
            self.non_compliant_switch_configs,
            self.compliant_value_with_overrides)

        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_items,
            consts.NEW: self.compliant_value_with_overrides,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value_with_overrides)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception('For "configVersion" expected type str, but got MagicMock')
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dvs_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        # Mocking the set method to simulate failure and return the desired errors
        with patch.object(DVSNetworkIOControlPolicy, "set", return_value=(RemediateStatus.FAILED,
                                                                          [str(expected_error)])):
            result = self.controller.remediate(mock_vc_context, self.compliant_value)
            assert result == expected_result
