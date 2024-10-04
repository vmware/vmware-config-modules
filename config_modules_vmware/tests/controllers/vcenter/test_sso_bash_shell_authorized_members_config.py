from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.sso_bash_shell_authorized_members_config \
    import SSOBashShellAuthorizedMembersConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSSOBashShellAuthorizedMembersConfig:
    def setup_method(self):
        self.controller = SSOBashShellAuthorizedMembersConfig()
        self.compliant_value = [
            {
                "name": "user-1",
                "domain": "vmware.com",
                "member_type": "USER"
            },
            {
                "name": "user-2",
                "domain": "vmware.com",
                "member_type": "USER"
            },
            {
                "name": "devops",
                "domain": "vsphere.local",
                "member_type": "GROUP"
            }
        ]
        self.non_compliant_value = [
            {
                "domain": "hellfire.net",
                "member_type": "USER",
                "name": "DiabolicDerek"
            },
            {
                "domain": "mischiefguild.com",
                "member_type": "GROUP",
                "name": "GoblinGang"
            }
        ]
        self.system_domain = "vsphere.local"
        self.group_mock = MagicMock()
        self.group_mock.name = "SystemConfiguration.BashShellAdministrators"
        self.group_mock.domain = "vsphere.local"

        self.compliant_user_mock = self.__create_user_mock_obj(self.compliant_value)
        self.non_compliant_user_mock = self.__create_user_mock_obj(self.non_compliant_value)

        self.compliant_group_mock = self.__create_group_mock_obj(self.compliant_value)
        self.non_compliant_group_mock = self.__create_group_mock_obj(self.non_compliant_value)

    @staticmethod
    def __create_group_mock_obj(member_configs):
        mock_groups = []
        for member_config in member_configs:
            if member_config["member_type"] == "GROUP":
                mock_group = MagicMock()
                mock_group.id.name = member_config["name"]
                mock_group.id.domain = member_config["domain"]
                mock_groups.append(mock_group)

        return mock_groups

    @staticmethod
    def __create_user_mock_obj(member_configs):
        mock_users = []
        for member_config in member_configs:
            if member_config["member_type"] == "USER":
                mock_user = MagicMock()
                mock_user.id.name = member_config["name"]
                mock_user.id.domain = member_config["domain"]
                mock_users.append(mock_user)
        return mock_users

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_get_success(self, mock_vc_vmomi_sso_client, mock_vc_context):

        mock_vc_vmomi_sso_client.get_system_domain.return_value = self.system_domain
        mock_vc_vmomi_sso_client._get_group.return_value = self.group_mock

        mock_vc_vmomi_sso_client.find_users_in_group.return_value = self.compliant_user_mock
        mock_vc_vmomi_sso_client.find_groups_in_group.return_value = self.compliant_group_mock

        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_value
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_get_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Failed to get user details from group")

        mock_vc_vmomi_sso_client.get_system_domain.return_value = self.system_domain
        mock_vc_vmomi_sso_client._get_group.return_value = self.group_mock
        mock_vc_vmomi_sso_client.find_users_in_group.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
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

        mock_vc_vmomi_sso_client.get_system_domain.return_value = self.system_domain
        mock_vc_vmomi_sso_client._get_group.return_value = self.group_mock

        mock_vc_vmomi_sso_client.find_users_in_group.return_value = self.compliant_user_mock
        mock_vc_vmomi_sso_client.find_groups_in_group.return_value = self.compliant_group_mock
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

        mock_vc_vmomi_sso_client.get_system_domain.return_value = self.system_domain
        mock_vc_vmomi_sso_client._get_group.return_value = self.group_mock

        mock_vc_vmomi_sso_client.find_users_in_group.return_value = self.non_compliant_user_mock
        mock_vc_vmomi_sso_client.find_groups_in_group.return_value = self.non_compliant_group_mock
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_sso_client.get_system_domain.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_remediate_skipped_already_desired(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_vc_vmomi_sso_client.get_system_domain.return_value = self.system_domain
        mock_vc_vmomi_sso_client._get_group.return_value = self.group_mock

        mock_vc_vmomi_sso_client.find_users_in_group.return_value = self.compliant_user_mock
        mock_vc_vmomi_sso_client.find_groups_in_group.return_value = self.compliant_group_mock
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

        mock_vc_vmomi_sso_client.get_system_domain.return_value = self.system_domain
        mock_vc_vmomi_sso_client._get_group.return_value = self.group_mock
        mock_vc_vmomi_sso_client.find_users_in_group.return_value = self.non_compliant_user_mock
        mock_vc_vmomi_sso_client.find_groups_in_group.return_value = self.non_compliant_group_mock
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
