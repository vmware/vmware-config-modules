from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.sso_active_directory_authentication_policy \
    import SSOActiveDirectoryAuthPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSSOActiveDirectoryAuthPolicy:
    def setup_method(self):
        self.controller = SSOActiveDirectoryAuthPolicy()
        self.compliant_value = True
        self.non_compliant_value = False
        self.compliant_domain_mock_obj = self.__create_mock_sso_domain_object(is_compliant=True)
        self.non_compliant_domain_mock_obj = [self.__create_mock_sso_domain_object(is_compliant=False)]

    @staticmethod
    def __create_mock_sso_domain_object(is_compliant=True):
        """
        Create mock object for sso domain of type sso.admin.Domains
        :return:
        """
        all_domains = MagicMock()
        if is_compliant:
            all_domains.externalDomains = []
            mock_external_domain = MagicMock()
            mock_external_domain.type = 'ActiveDirectory'
            mock_external_domain.name = 'vmware.com'
            mock_external_domain.alias = 'vmware.com'

            # mock details
            mock_external_domain.details = MagicMock()
            mock_external_domain.details.friendlyName = 'vmware.com'
            mock_external_domain.details.userBaseDn = 'OU=SITES,OU=Engineering,DC=vmware,DC=com'
            mock_external_domain.details.groupBaseDn = 'OU=Generic,OU=Groups,OU=Corp,OU=Common,DC=vmware,DC=com'
            mock_external_domain.details.primaryUrl = 'ldaps://renewed-dccert-vip.vmware.com'
            mock_external_domain.details.searchTimeoutSeconds = 0

            # Mock authentication details
            mock_external_domain.authenticationDetails = MagicMock()
            mock_external_domain.authenticationDetails.authenticationType = 'password'
            mock_external_domain.authenticationDetails.username = 'garun@vmware.com'
            all_domains.externalDomains.append(mock_external_domain)

        all_domains.systemDomainName = 'vsphere.local'
        all_domains.localOSDomainName = 'localos'
        return all_domains

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_get_success(self, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.compliant_domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_value
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_get_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Failed to get active directory configuration from vcenter")

        mock_vc_vmomi_sso_client.get_all_domains.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.get(mock_vc_context)
        assert result is None
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_set_success(self, mock_vc_context):
        expected_error = [consts.REMEDIATION_SKIPPED_MESSAGE]
        expected_status = RemediateStatus.SKIPPED

        status, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert status == expected_status
        assert errors == expected_error

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.compliant_domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value,
        }
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.non_compliant_domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_sso_client.get_all_domains.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_remediate_success_already_desired(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.compliant_domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_remediate_success(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE],
            consts.DESIRED: self.compliant_value,
            consts.CURRENT: self.non_compliant_value
        }

        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.non_compliant_domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
