from mock import call
from mock import patch

from config_modules_vmware.controllers.vcenter.h5_client_session_timeout_config import GREP_GET_PROPERTY_CMD
from config_modules_vmware.controllers.vcenter.h5_client_session_timeout_config import H5ClientSessionTimeoutConfig
from config_modules_vmware.controllers.vcenter.h5_client_session_timeout_config import PROPERTY_FILE_PATH
from config_modules_vmware.controllers.vcenter.h5_client_session_timeout_config import SED_ADD_CMD
from config_modules_vmware.controllers.vcenter.h5_client_session_timeout_config import SED_CMD
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestH5ClientSessionTimeoutConfig:
    def setup_method(self):
        self.controller = H5ClientSessionTimeoutConfig()

        # Compliant
        self.compliant_session_timeout_std_out = """\n
                                                    session.timeout = 10\n
                                                    """
        self.non_compliant_session_timeout_std_out = """\n
                                                    session.timeout = 120\n
                                                    """

        self.compliant_shell_cmd_return_val = (self.compliant_session_timeout_std_out, "", 0)
        self.non_compliant_shell_cmd_return_val = (self.non_compliant_session_timeout_std_out, "", 0)
        self.compliant_session_timeout_value = 10
        self.non_compliant_session_timeout_value = 120

        self.shell_cmd_set_return_success = ("", "", 0)

        self.failed_result = None
        self.missing_property_std_out = """
                                        """
        self.get_failure_msg = "Unable to fetch Session.timeout config"
        self.shell_cmd_set_return_failure = ("", self.get_failure_msg, 1)

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_success(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_session_timeout_value
        assert not errors

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_missing_property(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.return_value = self.shell_cmd_set_return_failure

        result, errors = self.controller.get(mock_vc_context)

        assert result is None
        assert not errors

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_failed(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = Exception(self.get_failure_msg)

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.failed_result
        assert errors == [str(Exception(self.get_failure_msg))]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success_with_replace(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = [
            (self.non_compliant_session_timeout_std_out, "", 0),
            ("", "", 0),
            (self.compliant_session_timeout_std_out, "", 0),
        ]

        result, errors = self.controller.set(mock_vc_context, self.compliant_session_timeout_value)

        assert result == RemediateStatus.SUCCESS
        assert not errors

        sed_replace_command = (
            rf"{SED_CMD} -i '/^session\.timeout/s/=[[:space:]]*[^[:space:]]*/= {self.compliant_session_timeout_value}/'"
            f" {PROPERTY_FILE_PATH}"
        )
        # Assert if commands were called in right order and with correct parameters
        expected_set_timeout_calls = [
            # Read property, which is non-compliant
            call(command=GREP_GET_PROPERTY_CMD, timeout=10, raise_on_non_zero=False),
            # Replace property with compliant value
            call(command=sed_replace_command, timeout=10),
            # Read property again to assert value == desired
            call(command=GREP_GET_PROPERTY_CMD, timeout=10, raise_on_non_zero=False),
        ]

        mock_execute_shell_cmd.assert_has_calls(expected_set_timeout_calls, any_order=False)

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_already_desired(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = [(self.compliant_session_timeout_std_out, "", 0)]

        result, errors = self.controller.set(mock_vc_context, self.compliant_session_timeout_value)

        assert result == RemediateStatus.SUCCESS
        assert not errors

        # Assert if only get was called if property is already compliant
        mock_execute_shell_cmd.assert_called_with(
            command=GREP_GET_PROPERTY_CMD, timeout=10, raise_on_non_zero=False
        )

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success_with_missing_property(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = [
            (self.missing_property_std_out, "", 0),
            ("", "", 0),
            (self.compliant_session_timeout_std_out, "", 0),
        ]

        result, errors = self.controller.set(mock_vc_context, self.compliant_session_timeout_value)

        assert result == RemediateStatus.SUCCESS
        assert not errors

        # Assert if commands were called in right order and with correct parameters
        expected_set_timeout_calls = [
            # Read property, in this case its missing in prop file
            call(command=GREP_GET_PROPERTY_CMD, timeout=10, raise_on_non_zero=False),
            # Add new property with compliant value
            call(command=SED_ADD_CMD.format(self.compliant_session_timeout_value), timeout=10),
            # Read property again to assert value == desired
            call(command=GREP_GET_PROPERTY_CMD, timeout=10, raise_on_non_zero=False),
        ]

        mock_execute_shell_cmd.assert_has_calls(expected_set_timeout_calls, any_order=False)

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_failed(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = [
            self.non_compliant_shell_cmd_return_val,
            self.shell_cmd_set_return_success,
            self.non_compliant_shell_cmd_return_val
        ]
        result, errors = self.controller.set(mock_vc_context, self.compliant_session_timeout_value)

        assert result == RemediateStatus.FAILED
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val

        result = self.controller.check_compliance(mock_vc_context, self.compliant_session_timeout_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_non_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_session_timeout_value,
            consts.DESIRED: self.compliant_session_timeout_value,
        }
        mock_execute_shell_cmd.side_effect = [self.non_compliant_shell_cmd_return_val]

        result = self.controller.check_compliance(mock_vc_context, self.compliant_session_timeout_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_error = Exception("Compliance check failed while fetching session timeout")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_execute_shell_cmd.side_effect = [expected_error]

        result = self.controller.check_compliance(mock_vc_context, self.compliant_session_timeout_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_skipped_already_desired(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val

        result = self.controller.remediate(mock_vc_context, self.compliant_session_timeout_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_success(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_session_timeout_value,
            consts.NEW: self.compliant_session_timeout_value,
        }

        mock_execute_shell_cmd.side_effect = [
            self.non_compliant_shell_cmd_return_val,
            self.non_compliant_shell_cmd_return_val,
            self.shell_cmd_set_return_success,
            self.compliant_shell_cmd_return_val,
        ]

        result = self.controller.remediate(mock_vc_context, self.compliant_session_timeout_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_get_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_error = Exception("Exception while getting session timeout config during remediation")

        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_execute_shell_cmd.side_effect = [expected_error]

        result = self.controller.remediate(mock_vc_context, self.compliant_session_timeout_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_set_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_error = Exception("Remediation failed while setting session timeout")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_execute_shell_cmd.side_effect = [
            self.non_compliant_shell_cmd_return_val,
            expected_error,
            self.shell_cmd_set_return_success,
        ]

        result = self.controller.remediate(mock_vc_context, self.compliant_session_timeout_value)

        assert result == expected_result
