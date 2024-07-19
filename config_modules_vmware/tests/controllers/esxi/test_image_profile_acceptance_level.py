# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import MagicMock

from config_modules_vmware.controllers.esxi.image_profile_acceptance_level import ImageProfileAcceptanceLevel
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

ACCEPTANCE_LEVEL = "acceptance_level"

class TestImageProfileAcceptanceLevel:
    def setup_method(self):
        self.controller = ImageProfileAcceptanceLevel()
        self.compliant_value = {"acceptance_level": "partner"}
        self.compliant_value2 = {"acceptance_level": "vmware_certified"}
        self.non_compliant_value = {"acceptance_level": "community"}
        mock_host_ref = MagicMock()
        mock_host_ref.name = 'host-1'
        mock_host_ref.configManager.imageConfigManager.HostImageConfigGetAcceptance.return_value = "partner"
        self.mock_host_context = HostContext(host_ref=mock_host_ref)
        self.mock_host_ref = mock_host_ref

    def test_get_success(self):
        result, errors = self.controller.get(self.mock_host_context)
        assert result == self.compliant_value
        assert errors == []

    def test_get_failed(self):
        expected_error = "test exception"
        self.mock_host_ref.configManager.imageConfigManager.HostImageConfigGetAcceptance.side_effect = Exception(expected_error)
        result, errors = self.controller.get(self.mock_host_context)
        assert errors == [expected_error]
        assert result == {}

    def test_set_success(self):
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        expected_error = "test exception"
        self.mock_host_ref.configManager.imageConfigManager.UpdateHostImageAcceptanceLevel.side_effect = Exception(expected_error)
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.FAILED
        assert errors == [expected_error]

    def test_check_compliance_compliant(self):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value)
        assert result == expected_result

    def test_check_compliance_compliant2(self):
        acceptance_level = self.compliant_value2.get(ACCEPTANCE_LEVEL)
        self.mock_host_ref.configManager.imageConfigManager.HostImageConfigGetAcceptance.return_value = acceptance_level
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value2)
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        acceptance_level = self.non_compliant_value.get(ACCEPTANCE_LEVEL)
        self.mock_host_ref.configManager.imageConfigManager.HostImageConfigGetAcceptance.return_value = acceptance_level
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value
        }
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value)
        assert result == expected_result

    def test_remediate(self):
        acceptance_level = self.non_compliant_value.get(ACCEPTANCE_LEVEL)
        self.mock_host_ref.configManager.imageConfigManager.HostImageConfigGetAcceptance.return_value = acceptance_level
        result = self.controller.remediate(self.mock_host_context, self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_value,
            consts.NEW: self.compliant_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        result = self.controller.remediate(self.mock_host_context, self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: ['Control already compliant']
        }
        assert result == expected_result
