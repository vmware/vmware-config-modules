# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.pg_vss_allow_promiscuous_mode import PgVssAllowPromiscuousMode
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestPgVssAllowPromiscuousMode:
    def setup_method(self):
        self.controller = PgVssAllowPromiscuousMode()
        self.compliant_value = False
        self.compliant_return_value = [{"vss_name": "vswitch-1", "allow_promiscuous_mode": False}]
        self.non_compliant_return_value = [{"vss_name": "vswitch-1", "allow_promiscuous_mode": True}]
        self.non_compliant_value = True
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.vss = MagicMock()
        self.vss.name = "vswitch-1"
        self.vss.spec.policy.security.allowPromiscuous = self.compliant_value
        self.mock_host_ref.config.network.vswitch = [self.vss]

    def test_get_success(self):
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == self.compliant_return_value
        assert errors == []

    def test_get_failed(self):
        self.mock_host_ref = -1
        result, errors = self.controller.get(HostContext(host_ref=self.mock_host_ref))
        assert result == []
        assert errors == ["'int' object has no attribute 'config'"]

    def test_set_success(self):
        status, errors = self.controller.set(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        self.mock_host_ref.configManager.networkSystem.UpdateVirtualSwitch.side_effect = Exception("Test exception")
        self.vss.spec.policy.security.allowPromiscuous = self.non_compliant_value
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
        self.vss.spec.policy.security.allowPromiscuous = self.non_compliant_value
        result = self.controller.check_compliance(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_return_value,
            consts.DESIRED: self.compliant_value
        }
        assert result == expected_result

    def test_remediate(self):
        self.vss.spec.policy.security.allowPromiscuous = self.non_compliant_value
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref),  self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_return_value,
            consts.NEW: self.compliant_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        result = self.controller.remediate(HostContext(host_ref=self.mock_host_ref), self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: ['Control already compliant']
        }
        assert result == expected_result
