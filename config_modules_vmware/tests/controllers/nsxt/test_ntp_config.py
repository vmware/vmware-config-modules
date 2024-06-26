from mock import patch

from config_modules_vmware.controllers.nsxt_manager.ntp_config import NtpConfig
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestNtpConfig:

    def setup_method(self):
        self.context = BaseContext(BaseContext.ProductEnum.NSXT_EDGE)
        self.config = NtpConfig()

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_get_compliance(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.google.com"]}
        mock_run_shell_cmd.return_value = ("time.google.com", "")

        result, errors = self.config.get(self.context)
        assert result == desired_value
        assert not errors

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_check_compliance(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.google.com"]}
        mock_run_shell_cmd.return_value = ("time.google.com", "")

        result = self.config.check_compliance(context=self.context, desired_values=desired_value)
        assert result.get(consts.STATUS) == ComplianceStatus.COMPLIANT

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_get_non_compliance(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.google.com"]}
        mock_run_shell_cmd.return_value = ("time.vmware.com", "")

        result, errors = self.config.get(self.context)
        assert result != desired_value
        assert not errors

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_get_failed(self, mock_run_shell_cmd):
        expected_error = "test exception"
        expected_errors = [expected_error]
        mock_run_shell_cmd.side_effect = Exception(expected_error)

        result, errors = self.config.get(self.context)

        assert not result["servers"]
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_set_success(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.google.com"]}
        mock_run_shell_cmd.side_effect = [("time.vmware.com", ""), ("", ""), ("", ""), ("time.google.com", "")]
        status, errors = self.config.set(self.context, desired_value)

        assert status == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_set_current_value(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.vmware.com"]}
        mock_run_shell_cmd.return_value = ("time.vmware.com", "")
        status, errors = self.config.set(self.context, desired_value)

        assert status == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_set_get_call_failed(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.error.com"]}
        mock_run_shell_cmd.side_effect = Exception("exception")
        status, errors = self.config.set(self.context, desired_value)

        assert status == RemediateStatus.FAILED
        assert len(errors) == 1
        assert "Exception getting current NTP servers" in errors[0]

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_set_command_failed(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.error.com"]}
        mock_run_shell_cmd.side_effect = [("time.google.com", ""), Exception("exception")]
        status, errors = self.config.set(self.context, desired_value)

        assert status == RemediateStatus.FAILED
        assert errors == ["exception"]

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_set_validate_failed(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.google.com"]}
        mock_run_shell_cmd.side_effect = [("time.vmware.com", ""), ("", ""), ("", ""), ("time.vmware.com", "")]
        status, errors = self.config.set(self.context, desired_value)

        assert status == RemediateStatus.FAILED
        assert len(errors) == 1
        assert "Failed to update NTP servers" in errors[0]

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_remediate(self, mock_run_shell_cmd):
        desired_value = {"servers": ["time.google.com"]}
        mock_run_shell_cmd.side_effect = [("time.vmware.com", ""), ("time.vmware.com", ""), ("", ""), ("", ""),
                                          ("time.google.com", "")]
        status = self.config.remediate(self.context, desired_value)

        assert status.get(consts.STATUS) == RemediateStatus.SUCCESS
