# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import MagicMock

from config_modules_vmware.controllers.esxi.shell_service_policy import ShellServicePolicy
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

ESXI_SERVICE_SHELL = "TSM"

class TestShellServicePolicy:
    def setup_method(self):
        self.controller = ShellServicePolicy()
        self.compliant_value = {"service_running": False, "service_policy": "off"}
        self.compliant_value2 = {"service_running": True, "service_policy": "off"}
        self.non_compliant_value = {"service_running": True, "service_policy": "on"}
        self.non_compliant_value2 = {"service_running": False, "service_policy": "on"}
        self.host_service = MagicMock()
        self.host_service.serviceInfo.service = [MagicMock(key=ESXI_SERVICE_SHELL, running=False, policy="off")]
        mock_host_ref = MagicMock()
        mock_host_ref.name = 'host-1'
        mock_host_ref.configManager.serviceSystem = self.host_service
        self.mock_host_context = HostContext(host_ref=mock_host_ref)

    def test_get_success(self):
        result, errors = self.controller.get(self.mock_host_context)
        assert result == self.compliant_value
        assert errors == []

    def test_get_failed(self):
        expected_error = ["service not found"]
        self.host_service.serviceInfo.service = [MagicMock(key="nobody", running=False)]
        result, errors = self.controller.get(self.mock_host_context)
        assert errors == expected_error
        assert result == {}

    def test_set_success(self):
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        expected_error = "service not found"
        self.host_service.StopService.side_effect = Exception(expected_error)
        self.host_service.serviceInfo.service = [MagicMock(key="nobody", running=False)]
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.FAILED
        assert errors == [expected_error]

    def test_check_compliance_compliant(self):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value)
        assert result == expected_result

    def test_check_compliance_compliant2(self):
        self.host_service.serviceInfo.service = [MagicMock(key=ESXI_SERVICE_SHELL, running=True, policy="off")]
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value2)
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        self.host_service.serviceInfo.service = [MagicMock(key=ESXI_SERVICE_SHELL, running=True, policy="on")]
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value
        }
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value)
        assert result == expected_result

    def test_check_compliance_non_compliant2(self):
        self.host_service.serviceInfo.service = [MagicMock(key=ESXI_SERVICE_SHELL, running=False, policy="on")]
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value2,
            consts.DESIRED: self.compliant_value2
        }
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value2)
        assert result == expected_result

    def test_remediate(self):
        self.host_service.serviceInfo.service = [MagicMock(key=ESXI_SERVICE_SHELL, running=True, policy="on")]
        result = self.controller.remediate(self.mock_host_context, self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_value,
            consts.NEW: self.compliant_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        self.host_service.serviceInfo.service = [MagicMock(key=ESXI_SERVICE_SHELL, running=False, policy="off")]
        result = self.controller.remediate(self.mock_host_context, self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: ['Control already compliant']
        }
        assert result == expected_result
