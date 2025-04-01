from mock import patch

from config_modules_vmware.controllers.vcenter.ldap_identity_source_config import LdapIdentitySourceConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestLdapIdentitySourceConfig:
    def setup_method(self):
        self.controller = LdapIdentitySourceConfig()
        self.control_desired_value = [
            { 'username': 'test_user2@vmware.com', 'domain': 'sc2-10-186-58-234.eng.vmware.com' }
        ]
        self.compliant_value = self.control_desired_value
        self.non_compliant_value = [
            { 'username': 'administrator@vmware.com', 'domain': 'sc2-10-186-58-234.eng.vmware.com'}
        ]
        self.shell_cmd_output_compliant = \
            "********** IDENTITY SOURCE INFORMATION **********\n\
             IdentitySourceName        :  vsphere.local\n\
             DomainType                :  SYSTEM_DOMAIN\n\n\
             ********** IDENTITY SOURCE INFORMATION **********\n\
             IdentitySourceName        :  localos\n\
             DomainType                :  LOCAL_OS_DOMAIN\n\n\
             ********** IDENTITY SOURCE INFORMATION **********\n\
             IdentitySourceName        :  sc2-10-186-58-234.eng.vmware.com\n\
             DomainType                :  EXTERNAL_DOMAIN\n\
             Identity Settings:\n\
               alias                   :  DOMAIN\n\
               authenticationType      :  PASSWORD\n\
               userBaseDN              :  ou=Dev,dc=sc2-10-186-58-234.eng.vmware,dc=com\n\
               groupBaseDN             :  ou=Groups,dc=sc2-10-186-58-234.eng.vmware,dc=com\n\
               username                :  test_user2@vmware.com\n\
               providerType            :  IDENTITY_STORE_TYPE_LDAP_WITH_AD_MAPPING\n\
               servicePrincipalName    :  placeholder\n\
               useMachineAccount       :  false\n\
               FriendlyName            :  sc2-10-186-58-234.eng.vmware.com\n\
               SearchTimeoutInSeconds  :  0\n\
             Connection Settings:\n\
             URLs:\n\
                 0:  ldap://sc2-10-186-58-234.eng.vmware.com:389\n\
             Certificates:\n\
             Attributes:\n\
               http://schemas.xmlsoap.org/claims/UPN                           :  userPrincipalName\n\
               http://rsa.com/schemas/attr-names/2009/01/GroupIdentity         :  memberof\n\
               http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname :  givenName\n\
               http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname   :  sn\n\
               http://vmware.com/schemas/attr-names/2011/07/isSolution         :  subjectType\n\
             Flags::\n\
               Flags=0; [Default: recursively computing nested groups, no site affinity is enabled for AD over Ldap identity providers.]"
        self.shell_cmd_output_non_compliant = \
            "********** IDENTITY SOURCE INFORMATION **********\n\
             IdentitySourceName        :  vsphere.local\n\
             DomainType                :  SYSTEM_DOMAIN\n\n\
             ********** IDENTITY SOURCE INFORMATION **********\n\
             IdentitySourceName        :  localos\n\
             DomainType                :  LOCAL_OS_DOMAIN\n\n\
             ********** IDENTITY SOURCE INFORMATION **********\n\
             IdentitySourceName        :  sc2-10-186-58-234.eng.vmware.com\n\
             DomainType                :  EXTERNAL_DOMAIN\n\
             Identity Settings:\n\
               alias                   :  DOMAIN\n\
               authenticationType      :  PASSWORD\n\
               userBaseDN              :  ou=Dev,dc=sc2-10-186-58-234.eng.vmware,dc=com\n\
               groupBaseDN             :  ou=Groups,dc=sc2-10-186-58-234.eng.vmware,dc=com\n\
               username                :  administrator@vmware.com\n\
               providerType            :  IDENTITY_STORE_TYPE_LDAP_WITH_AD_MAPPING\n\
               servicePrincipalName    :  placeholder\n\
               useMachineAccount       :  false\n\
               FriendlyName            :  sc2-10-186-58-234.eng.vmware.com\n\
               SearchTimeoutInSeconds  :  0\n\
             Connection Settings:\n\
             URLs:\n\
                 0:  ldap://sc2-10-186-58-234.eng.vmware.com:389\n\
             Certificates:\n\
             Attributes:\n\
               http://schemas.xmlsoap.org/claims/UPN                           :  userPrincipalName\n\
               http://rsa.com/schemas/attr-names/2009/01/GroupIdentity         :  memberof\n\
               http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname :  givenName\n\
               http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname   :  sn\n\
               http://vmware.com/schemas/attr-names/2011/07/isSolution         :  subjectType\n\
             Flags::\n\
               Flags=0; [Default: recursively computing nested groups, no site affinity is enabled for AD over Ldap identity providers.]"
        self.shell_cmd_set_return_failure = ("", "run shell cmd errors", 1)
        self.shell_cmd_set_return_success = (self.shell_cmd_output_compliant, "", 0)
        self.shell_cmd_set_return_non_compliant = (self.shell_cmd_output_non_compliant, "", 0)

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
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
        assert result == []
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_no_binding_account(self, mock_execute_shell_cmd, mock_vc_context):
        # Setup Mock objects to raise an exception.
        expected_error = Exception("not enough values to unpack (expected 3, got 0)")

        mock_execute_shell_cmd.return_value = ""

        # Call Controller.
        result, errors = self.controller.get(mock_vc_context)

        # Assert expected results.
        assert result == []
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_skipped(self, mock_execute_shell_cmd, mock_vc_context):
        # Setup Mock objects for successfully changing the value.
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ["Set is not implemented as modifying config would impact existing auth."]}
        mock_execute_shell_cmd.return_value = self.shell_cmd_output_compliant

        # Call Controller.
        result, errors = self.controller.set(mock_vc_context, self.compliant_value)

        # Assert expected results.
        assert result == expected_result[consts.STATUS]
        assert errors == expected_result[consts.ERRORS]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_skipped(self, mock_execute_shell_cmd, mock_vc_context):
        # Setup Mock objects for successfully changing the value.

        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ["Set is not implemented as modifying config would impact existing auth."],
                           consts.DESIRED: self.control_desired_value, consts.CURRENT: self.non_compliant_value}

        mock_execute_shell_cmd.return_value = self.shell_cmd_set_return_non_compliant

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_failed(self, mock_execute_shell_cmd, mock_vc_context):
        expected_error = "test exception"
        expected_errors = [expected_error]
        mock_execute_shell_cmd.side_effect = Exception(expected_error)
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: expected_errors}
        mock_execute_shell_cmd.return_value = self.shell_cmd_output_compliant

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

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
