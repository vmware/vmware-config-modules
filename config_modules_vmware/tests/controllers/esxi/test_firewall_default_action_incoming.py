# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.firewall_default_action_incoming import FirewallDefaultActionIncoming
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestFirewallDefaultActionIncoming:
    def setup_method(self):
        self.controller = FirewallDefaultActionIncoming()
        self.compliant_value = 'DROP'
        self.non_compliant_value = 'PASS'
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.firewallSystem = MagicMock()
        self.mock_host_context = MagicMock()
        self.firewallSystem.firewallInfo.defaultPolicy.incomingBlocked = False
        self.firewallSystem.firewallInfo.defaultPolicy.outgoingBlocked = False
        self.mock_host_context.host_ref.configManager.firewallSystem = self.firewallSystem

    def test_get_success(self):
        result, errors = self.controller.get(self.mock_host_context)
        assert result == self.non_compliant_value
        assert errors == []

    def test_get_failed(self):
        expected_error = "'NoneType' object has no attribute 'firewallInfo'"
        self.mock_host_context.host_ref.configManager.firewallSystem = None
        result, errors = self.controller.get(self.mock_host_context)
        assert result is None
        assert errors == [expected_error]

    def test_set_success(self):
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        expected_error = "Test exception"
        self.mock_host_context.host_ref.configManager.firewallSystem.UpdateDefaultPolicy.side_effect = Exception(expected_error)
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.FAILED
        assert errors == [expected_error]

    def test_check_compliance_compliant(self):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        result = self.controller.check_compliance(self.mock_host_context, 'PASS')
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value
        }
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value)
        assert result == expected_result

    def test_remediate(self):
        result = self.controller.remediate(self.mock_host_context, self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_value,
            consts.NEW: self.compliant_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        result = self.controller.remediate(self.mock_host_context, 'PASS')
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result
