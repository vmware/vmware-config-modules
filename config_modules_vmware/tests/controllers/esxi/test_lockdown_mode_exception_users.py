# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.lockdown_mode_exception_users import LockdownModeExceptionUsers
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestLockdownModeExceptionUsers:
    def setup_method(self):
        self.controller = LockdownModeExceptionUsers()
        self.desired_value = ["test", "mux_user"]
        self.filtered_desired_value = ["test"]
        self.non_compliant_value = ["invalid", "mux_user"]
        self.filtered_non_compliant_value = ["invalid"]
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'

    def test_get_success(self):
        self.mock_host_ref.configManager.hostAccessManager.QueryLockdownExceptions.return_value = \
            self.non_compliant_value
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == self.non_compliant_value
        assert errors == []

    def test_get_failed(self):
        self.mock_host_ref.configManager.hostAccessManager.QueryLockdownExceptions.side_effect = \
            Exception("Test exception")
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert errors == ["Test exception"]

    def test_set_success(self):
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.filtered_desired_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        self.mock_host_ref.configManager.hostAccessManager.UpdateLockdownExceptions.side_effect = \
            Exception("Test exception")
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        assert status == RemediateStatus.FAILED
        assert errors == ["Test exception"]

    def test_check_compliance_compliant(self):
        self.mock_host_ref.configManager.hostAccessManager.QueryLockdownExceptions.return_value = \
            self.filtered_desired_value
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        self.mock_host_ref.configManager.hostAccessManager.QueryLockdownExceptions.return_value = \
            self.non_compliant_value
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.filtered_non_compliant_value,
            consts.DESIRED: self.filtered_desired_value
        }
        assert result == expected_result

    def test_check_compliance_failed1(self):
        self.mock_host_ref.configManager.hostAccessManager.QueryLockdownExceptions.side_effect = \
            Exception("Test exception")
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ['Test exception']
        }
        assert result == expected_result

    def test_remediate(self):
        self.mock_host_ref.configManager.hostAccessManager.QueryLockdownExceptions.return_value = \
            self.non_compliant_value
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.desired_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.filtered_non_compliant_value,
            consts.NEW: self.filtered_desired_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        self.mock_host_ref.configManager.hostAccessManager.QueryLockdownExceptions.return_value = \
            self.filtered_desired_value
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.desired_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: ['Control already compliant']
        }
        assert result == expected_result
