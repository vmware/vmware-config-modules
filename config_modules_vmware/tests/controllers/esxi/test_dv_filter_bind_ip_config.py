# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.dv_filter_bind_ip_config import DV_FILTER_BIND_IP
from config_modules_vmware.controllers.esxi.dv_filter_bind_ip_config import DvFilterBindIpConfig
from config_modules_vmware.controllers.esxi.dv_filter_bind_ip_config import SETTINGS_NAME
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestDvFilterBindIpConfig:
    def setup_method(self):
        self.controller = DvFilterBindIpConfig()
        self.compliant_value1 = {DV_FILTER_BIND_IP: ""}
        self.compliant_value2 = {DV_FILTER_BIND_IP: "10.0.0.100"}
        self.non_compliant_value = {DV_FILTER_BIND_IP: "10.0.0.1"}
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.option_string = SETTINGS_NAME

    def test_get_success(self):
        security_appliance_ip = self.compliant_value1.get(DV_FILTER_BIND_IP)
        option_values = [vim.option.OptionValue(key=self.option_string, value=security_appliance_ip)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == self.compliant_value1
        assert errors == []

    def test_get_success2(self):
        security_appliance_ip = self.compliant_value2.get(DV_FILTER_BIND_IP)
        option_values = [vim.option.OptionValue(key=self.option_string, value=security_appliance_ip)]
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
        security_appliance_ip = self.compliant_value1.get(DV_FILTER_BIND_IP)
        option_values = [vim.option.OptionValue(key=self.option_string, value=security_appliance_ip)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        security_appliance_ip = self.non_compliant_value.get(DV_FILTER_BIND_IP)
        option_values = [vim.option.OptionValue(key=self.option_string, value=security_appliance_ip)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value1
        }
        assert result == expected_result

    def test_remediate(self):
        security_appliance_ip = self.non_compliant_value.get(DV_FILTER_BIND_IP)
        option_values = [vim.option.OptionValue(key=self.option_string, value=security_appliance_ip)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.compliant_value1)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_value,
            consts.NEW: self.compliant_value1
        }
        assert result == expected_result

    def test_remediate2(self):
        security_appliance_ip = self.non_compliant_value.get(DV_FILTER_BIND_IP)
        option_values = [vim.option.OptionValue(key=self.option_string, value=security_appliance_ip)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.compliant_value2)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_value,
            consts.NEW: self.compliant_value2
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        security_appliance_ip = self.compliant_value1.get(DV_FILTER_BIND_IP)
        option_values = [vim.option.OptionValue(key=self.option_string, value=security_appliance_ip)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.compliant_value1)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result
