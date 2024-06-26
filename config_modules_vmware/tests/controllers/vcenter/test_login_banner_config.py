from mock import patch

from config_modules_vmware.controllers.vcenter.logon_banner_config import LogonBannerConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestLogonBannerConfig:
    def setup_method(self):
        self.controller = LogonBannerConfig()
        self.control_desired_value = {
            "logon_banner_title":
                "vCenter Server Managed by SDDC Manager",
            "logon_banner_content":
                "This vCenter Server is managed by SDDC Manager (sddc-manager.vrack.vsphere.local).\nMaking modifications directly in vCenter Server may break SDDC Manager workflows.\nPlease consult the product documentation before making changes through the vSphere Client.",
            "checkbox_enabled": True
        }
        self.compliant_value = {
            "logon_banner_content":
                "This vCenter Server is managed by SDDC Manager (sddc-manager.vrack.vsphere.local).\nMaking modifications directly in vCenter Server may break SDDC Manager workflows.\nPlease consult the product documentation before making changes through the vSphere Client."
        }
        self.non_compliant_value = {
            "logon_banner_content":
                "This vCenter Server is NOT managed by SDDC Manager (sddc-manager.vrack.vsphere.local).\nMaking modifications directly in vCenter Server may break SDDC Manager workflows.\nPlease consult the product documentation before making changes through the vSphere Client."
        }
        self.shell_cmd_output_compliant = \
            "Logon Banner Title: vCenter Server Managed by SDDC Manager\n\
             Logon Banner Content: \"This vCenter Server is managed by SDDC Manager (sddc-manager.vrack.vsphere.local).\nMaking modifications directly in vCenter Server may break SDDC Manager workflows.\nPlease consult the product documentation before making changes through the vSphere Client.\"\n\
             Checkbox enabled : true"
        self.shell_cmd_output_non_compliant = \
            "Logon Banner Title: vCenter Server Managed by SDDC Manager\n\
             Logon Banner Content: \"This vCenter Server is NOT managed by SDDC Manager (sddc-manager.vrack.vsphere.local).\nMaking modifications directly in vCenter Server may break SDDC Manager workflows.\nPlease consult the product documentation before making changes through the vSphere Client.\"\n\
             Checkbox enabled : true"
        self.shell_cmd_set_return_failure = ("", "run shell cmd errors", 1)
        self.shell_cmd_set_return_success = (self.shell_cmd_output_compliant, "", 0)
        self.shell_cmd_set_return_non_compliant = (self.shell_cmd_output_non_compliant, "", 0)

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_success(self, mock_execute_shell_cmd, mock_vc_context):

        mock_execute_shell_cmd.return_value = self.shell_cmd_set_return_success

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.control_desired_value
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_failed(self, mock_execute_shell_cmd, mock_vc_context):
        # Setup Mock objects to raise an exception.
        expected_error = "test exception"
        expected_errors = [expected_error]

        mock_execute_shell_cmd.side_effect = Exception(expected_error)

        # Call Controller.
        result, errors = self.controller.get(mock_vc_context)

        # Assert expected results.
        assert result == {}
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_failed(self, mock_execute_shell_cmd, mock_vc_context):
        # Setup Mock objects for successfully changing the value.

        expected_error = "test exception"
        expected_errors = [expected_error]
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: expected_errors}

        mock_execute_shell_cmd.side_effect = Exception(expected_error)

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_skipped_already_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        # Setup Mock objects for successfully changing the value.

        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ['Control already compliant']}

        mock_execute_shell_cmd.return_value = self.shell_cmd_set_return_success

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_success_non_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        # Setup Mock objects for successfully changing the value.

        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS, consts.OLD: self.non_compliant_value, consts.NEW: self.compliant_value}

        mock_execute_shell_cmd.return_value = self.shell_cmd_set_return_non_compliant

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_compliant(self, mock_execute_shell_cmd, mock_vc_context):

        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_execute_shell_cmd.return_value = self.shell_cmd_set_return_success

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_non_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value
        }

        mock_execute_shell_cmd.return_value = self.shell_cmd_set_return_non_compliant

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result
