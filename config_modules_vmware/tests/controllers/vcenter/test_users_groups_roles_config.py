from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.users_groups_roles_config import GROUP
from config_modules_vmware.controllers.vcenter.users_groups_roles_config import USER
from config_modules_vmware.controllers.vcenter.users_groups_roles_config import UsersGroupsRolesConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestUsersGroupsRolesConfig:
    def setup_method(self):
        self.controller = UsersGroupsRolesConfig()
        self.mock_roles = [
            MagicMock(name="TestRole1", roleId="role1"),
            MagicMock(name="TestRole2", roleId="role2")
        ]
        self.mock_permission_user = MagicMock()
        self.mock_permission_user.group = False
        self.mock_permission_user.principal = "user1"

        self.mock_permission_group = MagicMock()
        self.mock_permission_group.group = True
        self.mock_permission_group.principal = "group1"

        self.mock_role_permissions = [
            [self.mock_permission_user, self.mock_permission_group],
            [self.mock_permission_group]
        ]
        self.desired_values = [
            {"role": "TestRole1", "name": "user1", "type": USER }
        ]
        self.mock_content = MagicMock()
        self.mock_content.authorizationManager.roleList = self.mock_roles
        self.mock_content.authorizationManager.RetrieveRolePermissions.side_effect =\
            self._retrieve_permissions_side_effect

    def _retrieve_permissions_side_effect(self, role_id):
        if role_id == "role1":
            return self.mock_role_permissions[0]
        elif role_id == "role2":
            return self.mock_role_permissions[1]
        else:
            return ValueError("Unknown Role Id.")

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_get_success(self, mock_vc_context):
        mock_vc_context.vc_vmomi_client.return_value.content = self.mock_content

        result, errors = self.controller.get(mock_vc_context)
        expected_result = [
            {"role": self.mock_roles[0].name, "name": "user1", "type": USER},
            {"role": self.mock_roles[0].name, "name": "group1", "type": GROUP},
            {"role": self.mock_roles[1].name, "name": "group1", "type": GROUP}
        ]
        assert result == expected_result
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_get_failed(self, mock_vc_context):
        mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == ["Test exception"]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_set_skipped(self, mock_vc_context):
        status, errors = self.controller.set(mock_vc_context, self.desired_values)

        # Assert expected results.
        assert status == RemediateStatus.SKIPPED
        assert errors == [consts.REMEDIATION_SKIPPED_MESSAGE]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_remediation_skipped(self, mock_vc_context):
        result = self.controller.remediate(mock_vc_context, self.desired_values)

        # Assert expected results.
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE],
            consts.DESIRED: self.desired_values,
            consts.CURRENT: []
        }
        assert result == expected_result
