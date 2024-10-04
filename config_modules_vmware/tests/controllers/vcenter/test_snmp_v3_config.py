from mock import call
from mock import patch

from config_modules_vmware.controllers.vcenter.snmp_v3_config import APPLIANCE_SHELL_CMD_PREFIX
from config_modules_vmware.controllers.vcenter.snmp_v3_config import AUTHENTICATION
from config_modules_vmware.controllers.vcenter.snmp_v3_config import DISABLE_SNMP_CMD
from config_modules_vmware.controllers.vcenter.snmp_v3_config import ENABLE_SNMP_CMD
from config_modules_vmware.controllers.vcenter.snmp_v3_config import PRIVACY
from config_modules_vmware.controllers.vcenter.snmp_v3_config import SNMP_SET_CMD
from config_modules_vmware.controllers.vcenter.snmp_v3_config import SNMPv3SecurityPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSNMPv3SecurityPolicy:
    def setup_method(self):
        self.controller = SNMPv3SecurityPolicy()

        # Compliant
        self.compliant_snmp_std_out = """
                                        Config: 
                                           Authentication: SHA1
                                           Communities: ''
                                           Enable: True
                                           Processlist: False
                                           Engineid: 80001f88800d4378296589ba6500000000
                                           Loglevel: warning
                                           Notraps: ''
                                           Port: 161
                                           Privacy: AES128
                                           Syscontact: ''
                                           Syslocation: ''
                                           Targets: 
                                           Users: 
                                           Remoteusers: 
                                           V3targets: 
                                           Pid: 25741
                                      """
        self.compliant_std_err = ""
        self.compliant_ret_code = 0
        self.compliant_shell_cmd_return_val = (
            self.compliant_snmp_std_out,
            self.compliant_std_err,
            self.compliant_ret_code,
        )
        self.compliant_snmp_value = {"authentication": "SHA1", "enable": True, "privacy": "AES128"}
        self.compliant_snmp_disabled = {"authentication": "SHA1", "enable": False, "privacy": "AES256"}

        self.shell_cmd_set_return_success = ("", "", 0)

        self.shell_cmd_set_return_failure = ("", "", 1)

        # Non-Compliant
        self.non_compliant_snmp_value = {"authentication": "none", "enable": True, "privacy": "none"}
        self.failed_result = {}
        self.non_compliant_snmp_std_out = """
                                        Config: 
                                           Authentication: none
                                           Communities: ''
                                           Enable: True
                                           Processlist: False
                                           Engineid: 80001f88800d4378296589ba6500000000
                                           Loglevel: warning
                                           Notraps: ''
                                           Port: 161
                                           Privacy: none
                                           Syscontact: ''
                                           Syslocation: ''
                                           Targets: 
                                           Users: 
                                           Remoteusers: 
                                           V3targets: 
                                           Pid: 25741
                                      """

        self.non_compliant_shell_cmd_return_val = (self.non_compliant_snmp_std_out, "", 0)
        self.get_failure_msg = "Unable to fetch SNMP config"
        self.failed_get_shell_cmd_ret_val = ("", self.get_failure_msg, 2)

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_success(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_snmp_value
        assert not errors

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_failed(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = [self.failed_get_shell_cmd_ret_val]

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.failed_result
        assert errors == [str(Exception(self.get_failure_msg))]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = [
            self.shell_cmd_set_return_success,
            self.shell_cmd_set_return_success,
            self.shell_cmd_set_return_success,
        ]

        result, errors = self.controller.set(mock_vc_context, self.compliant_snmp_value)

        assert result == RemediateStatus.SUCCESS
        assert not errors

        # Assert if commands were called in right order and with correct parameters
        appliancesh_cmd_prefix = APPLIANCE_SHELL_CMD_PREFIX.format(mock_vc_context._username, mock_vc_context._password)
        set_snmp_cmd = appliancesh_cmd_prefix + f'"{ENABLE_SNMP_CMD}"'
        authentication_cmd = (
            appliancesh_cmd_prefix
            + f'"{SNMP_SET_CMD.format(AUTHENTICATION, self.compliant_snmp_value.get(AUTHENTICATION))}"'
        )
        privacy_cmd = (
            appliancesh_cmd_prefix + f'"{SNMP_SET_CMD.format(PRIVACY,self.compliant_snmp_value.get(PRIVACY))}"'
        )
        expected_set_snmp_calls = [
            call(command=set_snmp_cmd, timeout=10),
            call(command=authentication_cmd, timeout=10),
            call(command=privacy_cmd, timeout=10),
        ]

        mock_execute_shell_cmd.assert_has_calls(expected_set_snmp_calls, any_order=False)

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success_with_disabled_snmp_config(self, mock_execute_shell_cmd, mock_vc_context):
        mock_execute_shell_cmd.side_effect = [self.shell_cmd_set_return_success]

        result, errors = self.controller.set(mock_vc_context, self.compliant_snmp_disabled)

        assert result == RemediateStatus.SUCCESS
        assert not errors

        # Assert if only one disable command was called in case of disable
        appliancesh_cmd_prefix = APPLIANCE_SHELL_CMD_PREFIX.format(mock_vc_context._username, mock_vc_context._password)
        set_snmp_cmd = appliancesh_cmd_prefix + f'"{DISABLE_SNMP_CMD}"'

        expected_set_snmp_calls = [
            call(command=set_snmp_cmd, timeout=10)
        ]

        mock_execute_shell_cmd.assert_has_calls(expected_set_snmp_calls, any_order=False)

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_errors = [str(Exception("Error while setting Privacy algorithm"))]

        mock_execute_shell_cmd.side_effect = [
            self.shell_cmd_set_return_success,
            self.shell_cmd_set_return_success,
            Exception("Error while setting Privacy algorithm"),
        ]

        result, errors = self.controller.set(mock_vc_context, self.compliant_snmp_value)

        assert result == RemediateStatus.FAILED
        assert errors == expected_errors

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val

        result = self.controller.check_compliance(mock_vc_context, self.compliant_snmp_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_non_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: {"authentication": "none", "privacy": "none"},
            consts.DESIRED: {"authentication": "SHA1", "privacy": "AES128"},
        }
        mock_execute_shell_cmd.side_effect = [self.non_compliant_shell_cmd_return_val]

        result = self.controller.check_compliance(mock_vc_context, self.compliant_snmp_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_error = Exception("Compliance check failed while fetching SNMP Config")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_execute_shell_cmd.side_effect = [expected_error]

        result = self.controller.check_compliance(mock_vc_context, self.compliant_snmp_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_skipped_already_desired(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val

        result = self.controller.remediate(mock_vc_context, self.compliant_snmp_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_success(self, mock_execute_shell_cmd, mock_vc_context):
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: {"authentication": "none", "privacy": "none"},
            consts.NEW: {"authentication": "SHA1", "privacy": "AES128"},
        }

        mock_execute_shell_cmd.return_value = self.non_compliant_shell_cmd_return_val

        result = self.controller.remediate(mock_vc_context, self.compliant_snmp_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_get_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_error = Exception("Exception while getting SNMP config during remediation")

        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_execute_shell_cmd.side_effect = [expected_error]

        result = self.controller.remediate(mock_vc_context, self.compliant_snmp_value)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_set_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_error = Exception("Remediation failed while setting SNMP Authentication Algorithm")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_execute_shell_cmd.side_effect = [
            self.non_compliant_shell_cmd_return_val,
            self.shell_cmd_set_return_success,
            Exception("Remediation failed while setting SNMP Authentication Algorithm"),
            self.shell_cmd_set_return_success,
        ]

        result = self.controller.remediate(mock_vc_context, self.compliant_snmp_value)

        assert result == expected_result
