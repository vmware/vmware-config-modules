from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.users_groups_roles_config import GROUP
from config_modules_vmware.controllers.vcenter.users_groups_roles_config import USER
from config_modules_vmware.controllers.vcenter.users_groups_roles_config import UsersGroupsRolesConfig
from config_modules_vmware.controllers.vcenter.utils import vc_users_groups_roles_utils
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestUsersGroupsRolesConfig:
    def setup_method(self):
        self.controller = UsersGroupsRolesConfig()
        self.mock_roles = [
            MagicMock(name="TestRole1", roleId=0),
            MagicMock(name="TestRole2", roleId=1),
            MagicMock(name="TestRole3", roleId=2),
            MagicMock(name="TestRole4", roleId=3)
        ]
        self.mock_permission_user = MagicMock()
        self.mock_permission_user.group = False
        self.mock_permission_user.propagate = True
        self.mock_permission_user.principal = "abc.com\\user1"
        self.mock_permission_user.entity = "group-d1"

        self.mock_permission_user2 = MagicMock()
        self.mock_permission_user2.group = False
        self.mock_permission_user2.propagate = False
        self.mock_permission_user2.principal = "test_domain_alias\\user2"
        self.mock_permission_user2.entity = "group-d1"

        self.mock_permission_user3 = MagicMock()
        self.mock_permission_user3.group = False
        self.mock_permission_user3.propagate = True
        self.mock_permission_user3.principal = "test_domain_name2\\user3"
        self.mock_permission_user3.entity = "group-d1"

        self.mock_permission_user4 = MagicMock()
        self.mock_permission_user4.group = False
        self.mock_permission_user4.propagate = False
        self.mock_permission_user4.principal = "Test.com\\user4"
        self.mock_permission_user4.entity = "group-d1"

        self.mock_permission_group = MagicMock()
        self.mock_permission_group.group = True
        self.mock_permission_group.propagate = True
        self.mock_permission_group.principal = "test_domain_name\\group1"
        self.mock_permission_group.entity = "group-d1"

        self.mock_permission_group2 = MagicMock()
        self.mock_permission_group2.group = True
        self.mock_permission_group2.propagate = False
        self.mock_permission_group2.principal = "test_domain_alias2\\group2"
        self.mock_permission_group2.entity = "group-d1"

        self.mock_permission_group3 = MagicMock()
        self.mock_permission_group3.group = True
        self.mock_permission_group3.propagate = True
        self.mock_permission_group3.principal = "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4"
        self.mock_permission_group3.entity = "group-d1"

        self.mock_permission_group4 = MagicMock()
        self.mock_permission_group4.group = True
        self.mock_permission_group4.propagate = False
        self.mock_permission_group4.principal = "Test.com\\group4"
        self.mock_permission_group4.entity = "group-d1"

        self.mock_permission_group5 = MagicMock()
        self.mock_permission_group5.group = True
        self.mock_permission_group5.propagate = True
        self.mock_permission_group5.principal = "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4"
        self.mock_permission_group5.entity = "vm-01"

        self.mock_role_permissions = [
            [self.mock_permission_user, self.mock_permission_user],
            [self.mock_permission_user2, self.mock_permission_group, self.mock_permission_group2],
            [self.mock_permission_user3, self.mock_permission_user4, self.mock_permission_group3],
            [self.mock_permission_group4, self.mock_permission_group5]
        ]

        self.mock_global_permissions = [
            {"name": "abc.com\\user1", "role_id": self.mock_roles[0].roleId, "type": USER, "propagate": True},
            {"name": "test_domain_name2\\user3", "role_id": self.mock_roles[2].roleId, "type": USER, "propagate": True},
            {"name": "test_domain_name\\group1", "role_id": self.mock_roles[0].roleId, "type": GROUP, "propagate": True},
            {"name": "test_domain_alias2\\group2", "role_id": self.mock_roles[1].roleId, "type": GROUP, "propagate": False},
            {"name": "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4", "role_id": self.mock_roles[3].roleId, "type": GROUP, "propagate": False},
            {"name": "Test.com\\group4", "role_id": self.mock_roles[2].roleId, "type": GROUP, "propagate": False},
        ]

        self.desired_values = {
            "global":
                [
                    {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": False},
                    {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                ],
            "vcenter":
                [
                    {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                    {"role": self.mock_roles[3].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
                ],
            "exclude_user_patterns":
                [
                    "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4"
                ]
        }
        self.mock_content = MagicMock()
        self.mock_content.rootFolder = "group-d1"
        self.mock_content.authorizationManager.roleList = self.mock_roles
        self.mock_content.authorizationManager.RetrieveRolePermissions.side_effect = \
            self._retrieve_permissions_side_effect
        self.ad_specs = [
            {
                "domain_name": "test_domain_name",
                "domain_alias": "test_domain_alias",
                "user_base_dn": "dc=test,dc=io",
                "group_base_dn": "dc=test,dc=io",
                "primary_server_url": "ldap://test.io",
                "failover_server_url": None
            },
            {
                "domain_name": "test_domain_name2",
                "domain_alias": "test_domain_alias2",
                "user_base_dn": "dc=test2,dc=io",
                "group_base_dn": "dc=test2,dc=io",
                "primary_server_url": "ldap://test2.io",
                "failover_server_url": "ldaps://test2.io"
            },
        ]
        self.domain_mock_obj = self.__create_mock_sso_domain_object(self.ad_specs)

    def _retrieve_permissions_side_effect(self, role_id):
        if role_id < 4:
            return self.mock_role_permissions[role_id]
        else:
            return ValueError("Unknown Role Id.")

    @staticmethod
    def __create_mock_sso_domain_object(sso_specs):
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
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.get_global_permissions")
    def test_get_success(self, mock_get_global_permissions, mock_vc_context):
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content
        mock_get_global_permissions.return_value = self.mock_global_permissions
        self.controller._create_alias_domain_name_mapping(mock_vc_context)

        result, errors = self.controller.get(mock_vc_context)
        expected_result = {
            "global": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[2].name, "name": "test_domain_name2\\user3", "type": USER, "propagate": True},
                {"role": self.mock_roles[0].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[3].name, "name": "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "vcenter": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias\\user2", "type": USER, "propagate": False},
                {"role": self.mock_roles[1].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\user4", "type": USER, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[3].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ]
        }
        assert result == expected_result
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_get_failed(self, mock_vc_context):
        mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")

        result, errors = self.controller.get(mock_vc_context)
        assert result == {}
        assert errors == ["Test exception"]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.get_global_permissions")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.add_global_permission")
    def test_set_success(self, mock_add_global_permission, mock_get_global_permissions, mock_vc_context):
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content
        #mock_vc_context.vc_invsvc_mob3_client.return_value = mock_vc_invsvc_mob3_client
        #mock_vc_invsvc_mob3_client.get_global_permissions.return_value = self.mock_global_permissions
        mock_get_global_permissions.return_value = self.mock_global_permissions
        mock_add_global_permission.return_value = None
        remediate_drifts = {
            "global":
                [
                    ("+", {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": False})
                ],
            "vcenter":
                [
                    ("-", {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True})
                ]
        }

        status, errors = self.controller.set(mock_vc_context, remediate_drifts)

        # Assert expected results.
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.get_global_permissions")
    def test_check_compliance_compliant(self, mock_get_global_permissions, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content
        mock_get_global_permissions.return_value = self.mock_global_permissions
        desired_values = {
            "global": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[2].name, "name": "test_domain_name2\\user3", "type": USER, "propagate": True},
                {"role": self.mock_roles[0].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "vcenter": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias\\user2", "type": USER, "propagate": False},
                {"role": self.mock_roles[1].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\user4", "type": USER, "propagate": False},
                {"role": self.mock_roles[3].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "exclude_user_patterns": [
                "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4"
            ]
        }
        result = self.controller.check_compliance(mock_vc_context, desired_values)

        # Assert expected results.
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT,
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.get_global_permissions")
    def test_check_compliance_compliant_with_alias(self, mock_get_global_permissions, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content
        mock_get_global_permissions.return_value = self.mock_global_permissions
        desired_values = {
            "global": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[2].name, "name": "test_domain_alias2\\user3", "type": USER, "propagate": True},
                {"role": self.mock_roles[0].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "vcenter": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias\\user2", "type": USER, "propagate": False},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_name2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\user4", "type": USER, "propagate": False},
                {"role": self.mock_roles[3].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "exclude_user_patterns": [
                "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4"
            ]
        }
        result = self.controller.check_compliance(mock_vc_context, desired_values)

        # Assert expected results.
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT,
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.get_global_permissions")
    def test_check_compliance_non_compliant(self, mock_get_global_permissions, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content
        mock_get_global_permissions.return_value = self.mock_global_permissions

        result = self.controller.check_compliance(mock_vc_context, self.desired_values)

        expected_current = {
            "global": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[2].name, "name": "test_domain_name2\\user3", "type": USER, "propagate": True},
                {"role": self.mock_roles[0].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "vcenter": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias\\user2", "type": USER, "propagate": False},
                {"role": self.mock_roles[1].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\user4", "type": USER, "propagate": False},
                {"role": self.mock_roles[3].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ]
        }

        assert result[consts.STATUS] == ComplianceStatus.NON_COMPLIANT
        assert result[consts.DESIRED] == self.desired_values
        assert result[consts.CURRENT] == expected_current

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_with_get_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")
        result = self.controller.check_compliance(mock_vc_context, self.desired_values)
        # Assert expected results.
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ["Test exception"]
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.get_global_permissions")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.remove_global_permission")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.add_global_permission")
    def test_remediation_success(self, mock_add_global_permission, mock_remove_global_permission, mock_get_global_permissions, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content
        mock_get_global_permissions.return_value = self.mock_global_permissions
        mock_remove_global_permission.return_value = None
        mock_add_global_permission.return_value = None

        result = self.controller.remediate(mock_vc_context, self.desired_values)

        expected_current = {
            "global": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[2].name, "name": "test_domain_name2\\user3", "type": USER, "propagate": True},
                {"role": self.mock_roles[0].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "vcenter": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias\\user2", "type": USER, "propagate": False},
                {"role": self.mock_roles[1].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\user4", "type": USER, "propagate": False},
                {"role": self.mock_roles[3].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ]
        }

        # Assert expected results.
        assert result[consts.STATUS] == RemediateStatus.SUCCESS
        assert result[consts.NEW] == self.desired_values
        assert result[consts.OLD] == expected_current

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    @patch("config_modules_vmware.controllers.vcenter.utils.vc_users_groups_roles_utils.get_global_permissions")
    def test_remediation_skipped(self, mock_get_global_permissions, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_all_domains.return_value = self.domain_mock_obj
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content
        mock_get_global_permissions.return_value = self.mock_global_permissions

        desired_values = {
            "global": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[2].name, "name": "test_domain_name2\\user3", "type": USER, "propagate": True},
                {"role": self.mock_roles[0].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "vcenter": [
                {"role": self.mock_roles[0].name, "name": "abc.com\\user1", "type": USER, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias\\user2", "type": USER, "propagate": False},
                {"role": self.mock_roles[1].name, "name": "test_domain_name\\group1", "type": GROUP, "propagate": True},
                {"role": self.mock_roles[1].name, "name": "test_domain_alias2\\group2", "type": GROUP, "propagate": False},
                {"role": self.mock_roles[2].name, "name": "Test.com\\user4", "type": USER, "propagate": False},
                {"role": self.mock_roles[3].name, "name": "Test.com\\group4", "type": GROUP, "propagate": False},
            ],
            "exclude_user_patterns": [
                "vsphere.local\\vpxd-ed126b8a-0c50-4451-9b48-c03778b71dd4"
            ]
        }
        result = self.controller.remediate(mock_vc_context, desired_values)

        # Assert expected results.
        assert result[consts.STATUS] == RemediateStatus.SKIPPED
        assert result[consts.ERRORS] == [consts.CONTROL_ALREADY_COMPLIANT]
