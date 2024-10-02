# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.ntp_config import NtpConfig
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestNtpConfig:
    def setup_method(self):
        self.controller = NtpConfig()
        self.compliant_value = {"protocol": "ntp", "servers": ["10.0.0.250", "10.0.0.251"]}
        self.compliant_return_value = {"servers": ["10.0.0.250", "10.0.0.251"]}
        self.non_compliant_value = {"protocol": "ntp", "servers": ["10.0.0.253"]}
        self.non_compliant_return_value = {"servers": ["10.0.0.253"]}
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.dateTimeInfo = MagicMock(vim.HostDateTimeInfo)
        self.dateTimeInfo.systemClockProtocol = "ntp"
        self.dateTimeInfo.ntpConfig = MagicMock(vim.HostNtpConfig)
        self.dateTimeInfo.ntpConfig.server = [ip for ip in self.compliant_value.get("servers")]
        self.mock_host_ref.config.dateTimeInfo = self.dateTimeInfo

    def test_get_success(self):
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == self.compliant_value
        assert errors == []

    def test_get_failed(self):
        self.mock_host_ref = -1
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == {}
        assert errors == ["'int' object has no attribute 'config'"]

    def test_set_success(self):
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        self.mock_host_ref.configManager.dateTimeSystem.UpdateDateTimeConfig.side_effect = Exception("Test exception")
        self.dateTimeInfo.ntpConfig.server = [ip for ip in self.non_compliant_value.get("servers")]
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        assert status == RemediateStatus.FAILED
        assert errors == ["Test exception"]

    def test_check_compliance_compliant(self):
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        self.dateTimeInfo.ntpConfig.server = [ip for ip in self.non_compliant_value.get("servers")]
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_return_value,
            consts.DESIRED: self.compliant_return_value
        }
        assert result == expected_result

    def test_remediate(self):
        self.dateTimeInfo.ntpConfig.server = [ip for ip in self.non_compliant_value.get("servers")]
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_return_value,
            consts.NEW: self.compliant_return_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result
