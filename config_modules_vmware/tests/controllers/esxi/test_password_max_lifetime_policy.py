# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.password_max_lifetime_policy import PasswordMaxLifetimePolicy
from config_modules_vmware.controllers.esxi.password_max_lifetime_policy import SETTINGS_NAME
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class HelperTestEsxAdvControls:

    @staticmethod
    def get_default_failed_value(desired_configs):
        if isinstance(desired_configs, bool):
            return False
        elif isinstance(desired_configs, int):
            return -1
        elif isinstance(desired_configs, str):
            return ""
        elif isinstance(desired_configs, list):
            return []
        else:
            return None

    @staticmethod
    def helper_test_get_success(controller, mock_host_ref, option_string, desired_configs):
        option_values = [vim.option.OptionValue(key=option_string, value=desired_configs)]
        mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result, errors = controller.get(HostContext(host_ref=mock_host_ref))
        assert result == desired_configs
        assert errors == []

    @staticmethod
    def helper_test_get_failed(controller, mock_host_ref, option_string, desired_configs):
        mock_host_ref.configManager.advancedOption.QueryOptions.side_effect = Exception("Test exception")
        result, errors = controller.get(HostContext(host_ref=mock_host_ref))
        assert result == HelperTestEsxAdvControls.get_default_failed_value(desired_configs)
        assert errors == [f"Exception on querying advanced options: {option_string} for "
                          f"host: {mock_host_ref.name} with error msg: Test exception"]

    @staticmethod
    def helper_test_get_failed_invalid_name(controller, mock_host_ref, option_string, desired_configs):
        mock_host_ref.configManager.advancedOption.QueryOptions.side_effect = vim.fault.InvalidName
        result, errors = controller.get(HostContext(host_ref=mock_host_ref))
        assert result == HelperTestEsxAdvControls.get_default_failed_value(desired_configs)
        assert errors == [f"Invalid query param: {option_string} for advanced options "
                          f"for host: {mock_host_ref.name}"]

    @staticmethod
    def helper_test_get_failed_empty_options(controller, mock_host_ref, option_string, desired_configs):
        mock_host_ref.configManager.advancedOption.QueryOptions.return_value = None
        result, errors = controller.get(HostContext(host_ref=mock_host_ref))
        assert result == HelperTestEsxAdvControls.get_default_failed_value(desired_configs)
        assert errors == [f"Exception on querying advanced options: {option_string} for "
                          f"host: {mock_host_ref.name} with error msg: Invalid returned options"]

    @staticmethod
    def helper_test_set_success(controller, mock_host_ref, desired_configs):
        mock_host_ref.configManager.advancedOption.UpdateOptions.return_value = None
        status, errors = controller.set(HostContext(host_ref=mock_host_ref), desired_configs)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    @staticmethod
    def helper_test_set_failed(controller, mock_host_ref, desired_configs):
        mock_host_ref.configManager.advancedOption.UpdateOptions.side_effect = Exception("Test exception")
        status, errors = controller.set(HostContext(host_ref=mock_host_ref), desired_configs)
        assert status == RemediateStatus.FAILED
        assert errors == [f"Exception on updating advanced options "
                          f"for host: {mock_host_ref.name} with error msg: Test exception"]

    @staticmethod
    def helper_test_check_compliance_compliant(controller, mock_host_ref, option_string, desired_configs):
        option_values = [vim.option.OptionValue(key=option_string, value=desired_configs)]
        mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = controller.check_compliance(HostContext(host_ref=mock_host_ref), desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    @staticmethod
    def helper_test_check_compliance_non_compliant(controller, mock_host_ref, option_string,
                                                   desired_configs, non_compliant_configs):
        option_values = [vim.option.OptionValue(key=option_string, value=non_compliant_configs)]
        mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = controller.check_compliance(HostContext(host_ref=mock_host_ref), desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: desired_configs
        }
        assert result == expected_result

    @staticmethod
    def helper_test_remediate_success(controller, mock_host_ref, option_string,
                                      desired_configs, non_compliant_configs):
        option_values = [vim.option.OptionValue(key=option_string, value=non_compliant_configs)]
        mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = controller.remediate(HostContext(host_ref=mock_host_ref), desired_configs)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: desired_configs
        }
        assert result == expected_result

    @staticmethod
    def helper_test_remediate_on_already_compliant_system(controller, mock_host_ref, option_string, desired_configs):
        option_values = [vim.option.OptionValue(key=option_string, value=desired_configs)]
        mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = controller.remediate(HostContext(host_ref=mock_host_ref), desired_configs)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: ['Control already compliant']
        }
        assert result == expected_result


class TestPasswordMaxLifetimePolicy:
    def setup_method(self):
        self.controller = PasswordMaxLifetimePolicy()
        self.desired_configs = 90
        self.non_compliant_configs = 10
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.option_string = SETTINGS_NAME

    def test_get_success(self):
        HelperTestEsxAdvControls.helper_test_get_success(self.controller, self.mock_host_ref,
                                                         self.option_string, self.desired_configs)

    def test_get_failed(self):
        HelperTestEsxAdvControls.helper_test_get_failed(self.controller, self.mock_host_ref,
                                                        self.option_string, self.desired_configs)

    def test_get_failed_invalid_name(self):
        HelperTestEsxAdvControls.helper_test_get_failed_invalid_name(self.controller, self.mock_host_ref,
                                                                     self.option_string, self.desired_configs)

    def test_get_failed_empty_options(self):
        HelperTestEsxAdvControls.helper_test_get_failed_empty_options(self.controller, self.mock_host_ref,
                                                                      self.option_string, self.desired_configs)

    def test_set_success(self):
        HelperTestEsxAdvControls.helper_test_set_success(self.controller, self.mock_host_ref, self.desired_configs)

    def test_set_failed(self):
        HelperTestEsxAdvControls.helper_test_set_failed(self.controller, self.mock_host_ref, self.desired_configs)

    def test_check_compliance_compliant(self):
        HelperTestEsxAdvControls.helper_test_check_compliance_compliant(self.controller, self.mock_host_ref,
                                                                        self.option_string, self.desired_configs)

    def test_check_compliance_non_compliant(self):
        HelperTestEsxAdvControls.helper_test_check_compliance_non_compliant(self.controller, self.mock_host_ref,
                                                                            self.option_string, self.desired_configs,
                                                                            self.non_compliant_configs)

    def test_remediate(self):
        HelperTestEsxAdvControls.helper_test_remediate_success(self.controller, self.mock_host_ref,
                                                               self.option_string, self.desired_configs,
                                                               self.non_compliant_configs)

    def test_remediate_with_already_compliant(self):
        HelperTestEsxAdvControls.helper_test_remediate_on_already_compliant_system(self.controller,
                                                                                   self.mock_host_ref,
                                                                                   self.option_string,
                                                                                   self.desired_configs)
