# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.lockdown_mode_config import LockdownModeConfig
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestLockdownModeConfig:
    def setup_method(self):
        self.controller = LockdownModeConfig()
        self.desired_value = "NORMAL"
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'

    def test_get_success(self):
        self.mock_host_ref.configManager.hostAccessManager.lockdownMode = "lockdownNormal"
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == "NORMAL"
        assert errors == []

    def test_get_failed(self):
        self.mock_host_ref.configManager.hostAccessManager.lockdownMode = "unknown"
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert errors == ["Unable to fetch lockdown mode"]

    def test_set_success(self):
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        self.mock_host_ref.configManager.hostAccessManager.ChangeLockdownMode.side_effect = Exception("Test exception")
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        assert status == RemediateStatus.FAILED
        assert errors == ["Test exception"]

    def test_check_compliance_compliant(self):
        self.mock_host_ref.configManager.hostAccessManager.lockdownMode = "lockdownNormal"
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    def test_check_compliance_non_compliant1(self):
        self.mock_host_ref.configManager.hostAccessManager.lockdownMode = "lockdownDisabled"
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: "DISABLED",
            consts.DESIRED: self.desired_value
        }
        assert result == expected_result

    def test_remediate(self):
        self.mock_host_ref.configManager.hostAccessManager.lockdownMode = "lockdownDisabled"
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.desired_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: "DISABLED",
            consts.NEW: self.desired_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        self.mock_host_ref.configManager.hostAccessManager.lockdownMode = "lockdownNormal"
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result
