# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.tls_version import SETTINGS_NAME
from config_modules_vmware.controllers.esxi.tls_version import SUPPORTED_PROTOCOLS_SET
from config_modules_vmware.controllers.esxi.tls_version import TlsVersion
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestTlsVersion:
    def setup_method(self):
        self.controller = TlsVersion()
        self.desired_configs = ["tlsv1.2"]
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.option_string = SETTINGS_NAME

    def test_get_success(self):
        current_disabled_protocols = "sslv3,tlsv1,tlsv1.1"
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_disabled_protocols)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        disabled_protocols = [protocol.strip() for protocol in current_disabled_protocols.split(',')]
        expected = sorted(list(SUPPORTED_PROTOCOLS_SET - set(disabled_protocols)))
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
        current_disabled_protocols_compliant = "sslv3,tlsv1,tlsv1.1"
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_disabled_protocols_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        current_disabled_protocols_non_compliant = "sslv3, tlsv1.2"
        non_compliant_configs = ["tlsv1.1", "tlsv1"]
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_disabled_protocols_non_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: sorted(non_compliant_configs),
            consts.DESIRED: self.desired_configs
        }
        assert result == expected_result

    def test_remediate(self):
        current_disabled_protocols_non_compliant = "sslv3, tlsv1.2"
        non_compliant_configs = ["tlsv1.1", "tlsv1"]
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_disabled_protocols_non_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: sorted(non_compliant_configs),
            consts.NEW: self.desired_configs
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        current_disabled_protocols_compliant = "sslv3,tlsv1,tlsv1.1"
        option_values = [vim.option.OptionValue(key=self.option_string, value=current_disabled_protocols_compliant)]
        self.mock_host_ref.configManager.advancedOption.QueryOptions.return_value = option_values
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.desired_configs)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
        }
        assert result == expected_result
