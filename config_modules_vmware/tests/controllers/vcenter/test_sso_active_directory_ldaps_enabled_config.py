from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.sso_active_directory_ldaps_enabled_config \
    import SSOActiveDirectoryLdapsEnabledPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSSOActiveDirectoryLdapsEnabledPolicy:
    def setup_method(self):
        self.controller = SSOActiveDirectoryLdapsEnabledPolicy()
        self.ad_specs = [
            {
                "domain_name": "rainpole.io",
                "domain_alias": "RAINPOLE",
                "user_base_dn": "dc=rainpole,dc=io",
                "group_base_dn": "dc=rainpole,dc=io",
                "primary_server_url": "ldap://rainpole.io",
                "failover_server_url": None
            },
            {
                "domain_name": "sfo.rainpole.io",
                "domain_alias": "SFO",
                "user_base_dn": "dc=rainpole,dc=io",
                "group_base_dn": "dc=rainpole,dc=io",
                "primary_server_url": "ldap://rainpole.io",
                "failover_server_url": "ldaps://rainpole.io"
            },
            {
                "domain_name": "vmware.com",
                "domain_alias": "vmware",
                "user_base_dn": "dc=vmware,dc=com",
                "group_base_dn": "dc=vmware,dc=com",
                "primary_server_url": "ldaps://eng.ldap.vmware.com",
                "failover_server_url": None
            }
        ]
        self.non_compliant_get_output = [{'domain_alias': 'RAINPOLE',
                                          'domain_name': 'rainpole.io',
                                          'failover_server_url': None,
                                          'group_base_dn': 'dc=rainpole,dc=io',
                                          'primary_server_url': 'ldap://rainpole.io',
                                          'use_ldaps': False,
                                          'user_base_dn': 'dc=rainpole,dc=io'},
                                         {'domain_alias': 'SFO',
                                          'domain_name': 'sfo.rainpole.io',
                                          'failover_server_url': 'ldaps://rainpole.io',
                                          'group_base_dn': 'dc=rainpole,dc=io',
                                          'primary_server_url': 'ldap://rainpole.io',
                                          'use_ldaps': False,
                                          'user_base_dn': 'dc=rainpole,dc=io'}]
        self.compliant_get_output = {
            "domain_name": "vmware.com",
            "domain_alias": "vmware",
            "user_base_dn": "dc=vmware,dc=com",
            "group_base_dn": "dc=vmware,dc=com",
            "primary_server_url": "ldaps://eng.ldap.vmware.com",
            "failover_server_url": None,
            "use_ldaps": True
        }
        self.compliant_value = {
            "user_ldaps": True
        }
        self.non_compliant_domain_mock_obj = self.__create_mock_sso_domain_object(self.ad_specs)
        self.compliant_domain_mock_obj = self.__create_mock_sso_domain_object([self.ad_specs[2]])

    @staticmethod
    def __create_mock_sso_domain_object(sso_specs, is_compliant=True):
        """
        Create mock object for sso domain of type sso.admin.Domains
        """
        all_domains = MagicMock()
        all_domains.externalDomains = []
        mock_domains = []
        for sso_spec in sso_specs:
            mock_external_domain = MagicMock()
            mock_external_domain.type = 'ActiveDirectory'
            mock_external_domain.name = sso_spec.get("domain_name")
            mock_external_domain.alias = sso_spec.get("domain_alias")

            # Create a MagicMock object for details
            details_mock = MagicMock()

            # Set return values for properties within the details object
            details_mock.userBaseDn = sso_spec.get("user_base_dn")
            details_mock.groupBaseDn = sso_spec.get("group_base_dn")
            details_mock.primaryUrl = sso_spec.get("primary_server_url")
            details_mock.failoverUrl = sso_spec.get("failover_server_url")

            # Assign the MagicMock object to the details property of the external domain
            mock_external_domain.details = details_mock

            mock_domains.append(mock_external_domain)
        all_domains.externalDomains = mock_domains
        all_domains.systemDomainName = 'vsphere.local'
        all_domains.localOSDomainName = 'localos'
        return all_domains

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_get_success(self, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.compliant_domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
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
            consts.CURRENT: self.non_compliant_get_output,
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
    def test_remediate_skipped_already_desired(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

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
            consts.CURRENT: self.non_compliant_get_output
        }

        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.non_compliant_domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
