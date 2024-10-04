# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.lockdown_dcui_access_users import LockdownDcuiAccessUsers
from config_modules_vmware.controllers.esxi.lockdown_dcui_access_users import SETTINGS_NAME
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestLockdownDcuiAccessUsers:
    def setup_method(self):
        self.controller = LockdownDcuiAccessUsers()
        self.desired_configs = ["root"]
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.option_string = SETTINGS_NAME

    def test_get_success(self):
        current_users = "root, extra"
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_users)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        dcui_access_users = [user.strip() for user in current_users.split(',')]
        expected = dcui_access_users
        assert result == expected

        assert errors == []

    def test_get_failed(self):
        self.mock_host_ref.configManager.advancedOption.QueryOptions.side_effect = Exception("Test exception")
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == []
        assert errors == [f"Exception on querying advanced options: {self.option_string} for "
                          f"host: {self.mock_host_ref.name} with error msg: Test exception"]

    def test_get_failed_invalid_name(self):
        self.mock_host_ref.configManager.advancedOption.QueryOptions.side_effect = Exception("Test exception")
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == []
        assert errors == [f"Exception on querying advanced options: {self.option_string} for "
                          f"host: {self.mock_host_ref.name} with error msg: Test exception"]

    def test_get_failed_empty_options(self):
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = None
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == []
        assert errors == [f"Exception on querying advanced options: {self.option_string} for "
                          f"host: {self.mock_host_ref.name} with error msg: Invalid returned options"]

    def test_set_success(self):
        self.mock_host_ref.configManager.advancedOption.UpdateOptions.return_value = None
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        self.mock_host_ref.configManager.advancedOption.UpdateOptions.side_effect = Exception("Test exception")
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        assert status == RemediateStatus.FAILED
        assert errors == [f"Exception on updating advanced options "
                          f"for host: {self.mock_host_ref.name} with error msg: Test exception"]

    def test_check_compliance_compliant(self):
        current_users_compliant = "root"
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_users_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        current_users_non_compliant = "root, extra"
        non_compliant_configs = ["root", "extra"]
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_users_non_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: self.desired_configs
        }
        assert result == expected_result

    def test_remediate(self):
        current_users_non_compliant = "root, extra"
        non_compliant_configs = ["root", "extra"]
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_users_non_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: self.desired_configs
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        current_users_compliant = "root"
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_users_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result
