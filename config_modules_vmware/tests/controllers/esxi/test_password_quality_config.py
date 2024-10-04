# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.password_quality_config import PasswordQualityConfig
from config_modules_vmware.controllers.esxi.password_quality_config import SETTINGS_NAME
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestPasswordQualityConfig:
    def setup_method(self):
        self.controller = PasswordQualityConfig()
        self.compliant_value1 = {
                                    "retry": 3,
                                    "similar": "deny",
                                    "min": "disabled,disabled,disabled,disabled,15",
                                    "passphrase": 3
                                }
        self.desired_configs = {
                                   "min": "disabled,disabled,disabled,disabled,15",
                                   "passphrase": 3
                               }
        self.current_configs = {
                                   "min": "disabled,disabled,disabled,7,7",
                                   "passphrase": 10
                               }
        self.compliant_value2 = {
                                    "retry": 3,
                                    "similar": "deny",
                                    "min": "disabled,disabled,disabled,disabled,15",
                                }
        self.non_compliant_value = {
                                       "retry": 3,
                                       "min": "disabled,disabled,disabled,7,7",
                                       "max": 40,
                                       "passphrase": 10
                                   }
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.option_string = SETTINGS_NAME

    def test_get_success(self):
        password_quality_control = self.controller._create_config_string(self.compliant_value1)
        option_values = [vim.option.OptionValue(key=self.option_string, value=password_quality_control)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == self.compliant_value1
        assert errors == []

    def test_get_success2(self):
        password_quality_control = self.controller._create_config_string(self.compliant_value2)
        option_values = [vim.option.OptionValue(key=self.option_string, value=password_quality_control)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == self.compliant_value2
        assert errors == []

    def test_get_failed(self):
        self.mock_host_ref.configManager.advancedOption.QueryOptions.side_effect = Exception("Test exception")
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == {}
        assert errors == [f"Exception on querying advanced options: {self.option_string} for "
                          f"host: {self.mock_host_ref.name} with error msg: Test exception"]

    def test_get_failed_invalid_name(self):
        self.mock_host_ref.configManager.advancedOption.QueryOptions.side_effect = vim.fault.InvalidName
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == {}
        assert errors == [f"Invalid query param: {self.option_string} for advanced options "
                          f"for host: {self.mock_host_ref.name}"]

    def test_get_failed_empty_options(self):
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = None
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == {}
        assert errors == [f"Exception on querying advanced options: {self.option_string} for "
                          f"host: {self.mock_host_ref.name} with error msg: Invalid returned options"]

    def test_set_success(self):
        self.mock_host_ref.configManager.advancedOption.UpdateOptions.return_value = None
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_success2(self):
        self.mock_host_ref.configManager.advancedOption.UpdateOptions.return_value = None
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.compliant_value2)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        self.mock_host_ref.configManager.advancedOption.UpdateOptions.side_effect = Exception("Test exception")
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        assert status == RemediateStatus.FAILED
        assert errors == [f"Exception on updating advanced options "
                          f"for host: {self.mock_host_ref.name} with error msg: Test exception"]

    def test_check_compliance_compliant(self):
        password_quality_control = self.controller._create_config_string(self.compliant_value1)
        option_values = [vim.option.OptionValue(key=self.option_string, value=password_quality_control)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        password_quality_control = self.controller._create_config_string(self.non_compliant_value)
        option_values = [vim.option.OptionValue(key=self.option_string, value=password_quality_control)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.current_configs,
            consts.DESIRED: self.desired_configs
        }
        assert result == expected_result

    def test_check_compliance_failed(self):
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = None
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: [f"Exception on querying advanced options: {self.option_string} for "
                          f"host: {self.mock_host_ref.name} with error msg: Invalid returned options"]
        }
        assert result == expected_result

    def test_remediate(self):
        password_quality_control = self.controller._create_config_string(self.non_compliant_value)
        option_values = [vim.option.OptionValue(key=self.option_string, value=password_quality_control)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.compliant_value1)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.current_configs,
            consts.NEW: self.desired_configs
        }
        assert result == expected_result

    def test_remediate2(self):
        password_quality_control = self.controller._create_config_string(self.non_compliant_value)
        option_values = [vim.option.OptionValue(key=self.option_string, value=password_quality_control)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.compliant_value2)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.current_configs,
            consts.NEW: self.desired_configs
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        password_quality_control = self.controller._create_config_string(self.compliant_value1)
        option_values = [vim.option.OptionValue(key=self.option_string, value=password_quality_control)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result
