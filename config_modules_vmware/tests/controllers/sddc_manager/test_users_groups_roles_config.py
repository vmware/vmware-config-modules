from mock import patch

from config_modules_vmware.controllers.sddc_manager.users_groups_roles_config import NAME
from config_modules_vmware.controllers.sddc_manager.users_groups_roles_config import USERS_GROUPS_IGNORE_DICT
from config_modules_vmware.controllers.sddc_manager.users_groups_roles_config import UsersGroupsRolesConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import SDDC_MANAGER_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestUsersGroupsRolesConfig:
    def setup_method(self):
        # SDDC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.sddc_base_url = SDDC_MANAGER_API_BASE.format(self.mock_vc_host_name)

        # Initialize control
        self.controller = UsersGroupsRolesConfig()
        self.desired_value = [
            {'name': 'administrator@vsphere.local', 'role': 'ADMIN', 'type': 'USER'},
            {'name': 'vsphere.local\\Administrators', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'VSPHERE.LOCAL\\CAAdmins', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'VSPHERE.LOCAL\\SDDCAdmins', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'test_user@vsphere.local', 'role': 'OPERATOR', 'type': 'USER'}
        ]
        self.sso_domain_response = {'elements': ['vsphere.local']}
        self.sso_domain_entities_response = {
            'elements': [
                {'id': 'administrator@vsphere.local', 'name': 'administrator', 'type': 'USER'},
                {'id': 'vsphere.local\\Administrators', 'name': 'Administrators', 'type': 'GROUP'},
                {'id': 'vsphere.local\\CAAdmins', 'name': 'CAAdmins', 'type': 'GROUP'},
                {'id': 'vsphere.local\\SDDCAdmins', 'name': 'SDDCAdmins', 'type': 'GROUP'},
                {'id': 'test_user@vsphere.local', 'name': 'test_user', 'type': 'USER'},
                {'id': 'service_account1@vsphere.local', 'name': 'service_account1', 'type': 'SERVICE'}
            ]
        }
        self.users_response = {
            "elements": [
                            {
                                "id": "f6f19391-87d4-4ae1-835e-a1ce96356718",
                                "name": "administrator@VSPHERE.LOCAL",
                                "domain": "VSPHERE.LOCAL",
                                "type": "USER",
                                "role": {
                                    "id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78"
                                },
                                "creationTimestamp": "2024-02-15T22:44:19.734Z"
                            },
                            {
                                "id": "2081933b-5397-4f8c-b31d-d3c6b125495e",
                                "name": "VSPHERE.LOCAL\\Administrators",
                                "domain": "VSPHERE.LOCAL",
                                "type": "GROUP",
                                "role": {
                                    "id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78"
                                },
                                "creationTimestamp": "2024-02-15T22:44:19.800Z"
                            },
                            {
                                "id": "149cfd49-1460-43a3-a529-8f464edd2367",
                                "name": "VSPHERE.LOCAL\\CAAdmins",
                                "domain": "VSPHERE.LOCAL",
                                "type": "GROUP",
                                "role": {
                                    "id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78"
                                },
                                "creationTimestamp": "2024-02-15T22:44:19.825Z"
                            },
                            {
                                "id": "bbcecec2-27b9-41d4-9aca-82bae2b4a68e",
                                "name": "VSPHERE.LOCAL\\SDDCAdmins",
                                "domain": "VSPHERE.LOCAL",
                                "type": "GROUP",
                                "role": {
                                    "id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78"
                                },
                                "creationTimestamp": "2024-02-15T22:44:19.841Z"
                            },
                            {
                                "id": "abc12334ecec-27b9-41d4-9aca-82bae2b4a68e",
                                "name": "test_user@vsphere.local",
                                "domain": "VSPHERE.LOCAL",
                                "type": "USER",
                                "role": {
                                    "id": "3f7aee03-76a4-5d9d-3e46-9fa6a996e2ae"
                                },
                                "creationTimestamp": "2024-02-15T22:44:19.841Z"
                            }
                        ]
        }
        self.roles_response = {
            "elements": [
                {"id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78", "name": "ADMIN", "description": "Administrator"},
                {"id": "3f7aee03-76a4-5d9d-3e46-9fa6a996e2ae", "name": "OPERATOR", "description": "Operator"},
                {"id": "5ceac395-f960-461d-b3e6-c1d9b63103f1", "name": "VIEWER", "description": "Viewer"}
            ]
        }
        self.non_compliant_value = [{'name': 'administrator@VSPHERE.LOCAL', 'role': 'ADMIN', 'type': 'GROUP'},
                                    {'name': 'VSPHERE.LOCAL\\Administrators', 'role': 'ADMIN', 'type': 'GROUP'},
                                    {'name': 'VSPHERE.LOCAL\\CAAdmins', 'role': 'ADMIN', 'type': 'GROUP'},
                                    {'name': 'VSPHERE.LOCAL\\SDDCAdmins', 'role': 'ADMIN', 'type': 'GROUP'}
        ]
        self.non_compliant_users_response = {
            "elements": [
                {
                    "id": "f6f19391-87d4-4ae1-835e-a1ce96356718",
                    "name": "administrator@VSPHERE.LOCAL",
                    "domain": "VSPHERE.LOCAL",
                    "type": "USER",
                    "role": {
                        "id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78"
                    },
                    "creationTimestamp": "2024-02-15T22:44:19.734Z"
                },
                {
                    "id": "2081933b-5397-4f8c-b31d-d3c6b125495e",
                    "name": "VSPHERE.LOCAL\\Administrators",
                    "domain": "VSPHERE.LOCAL",
                    "type": "GROUP",
                    "role": {
                        "id": "3f7aee03-76a4-5d9d-3e46-9fa6a996e2ae"
                    },
                    "creationTimestamp": "2024-02-15T22:44:19.800Z"
                },
                {
                    "id": "149cfd49-1460-43a3-a529-8f464edd2367",
                    "name": "VSPHERE.LOCAL\\CAAdmins",
                    "domain": "VSPHERE.LOCAL",
                    "type": "GROUP",
                    "role": {
                        "id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78"
                    },
                    "creationTimestamp": "2024-02-15T22:44:19.825Z"
                },
                {
                    "id": "bbcecec2-27b9-41d4-9aca-82bae2b4a68e",
                    "name": "VSPHERE.LOCAL\\SDDCAdmins",
                    "domain": "VSPHERE.LOCAL",
                    "type": "GROUP",
                    "role": {
                        "id": "0f9844e7-097b-ebe1-71b0-0dfcd2d92e78"
                    },
                    "creationTimestamp": "2024-02-15T22:44:19.841Z"
                }
            ]
        }
        self.output_during_exception = []

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.roles_response, self.users_response]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result, errors = self.controller.get(mock_sddc_manager_context)

        expected_value = [{**element, NAME: element[NAME].lower()}
                          for element in self.desired_value
                          if element.get(NAME).lower() not in USERS_GROUPS_IGNORE_DICT]
        assert result == expected_value
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Test Exception")
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result, errors = self.controller.get(mock_sddc_manager_context)
        assert result == self.output_during_exception
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = (RemediateStatus.SUCCESS, [])
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.roles_response,
                                                                self.non_compliant_users_response,
                                                                self.sso_domain_response,
                                                                self.sso_domain_entities_response]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.set(mock_sddc_manager_context, self.desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Test Exception")
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        status, errors = self.controller.set(mock_sddc_manager_context, self.desired_value)
        assert status == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.roles_response, self.users_response]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.check_compliance(mock_sddc_manager_context, self.desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_non_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: [None,
                             {'name': 'vsphere.local\\administrators', 'role': 'OPERATOR'}],
            consts.DESIRED: [{'name': 'test_user@vsphere.local', 'role': 'OPERATOR', 'type': 'USER'},
                             {'name': 'vsphere.local\\administrators', 'role': 'ADMIN'}]
        }
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.roles_response, self.non_compliant_users_response]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.check_compliance(mock_sddc_manager_context, self.desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Test Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.check_compliance(mock_sddc_manager_context, self.desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed_incorrect_desired_value(self, mock_sddc_manager_rest_client,
                                                             mock_sddc_manager_context):
        errors = ["Role/type can not be modified for user/group 'administrator@vsphere.local'."
                  "Expected type: USER and role: ADMIN",
                  "Group 'vsphere.local\\\\caadmins' should be in expected format <DOMAIN>\\<GROUP_NAME>",
                  "User 'test_user_vsphere.local' should be in expected format <USER_NAME>@<DOMAIN>"]
        desired_value = [
            {'name': 'administrator@vsphere.local', 'role': 'OPERATOR', 'type': 'USER'},
            {'name': 'vsphere.local\\Administrators', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'VSPHERE.LOCAL\\\\CAAdmins', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'VSPHERE.LOCAL\\SDDCAdmins', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'test_user_vsphere.local', 'role': 'OPERATOR', 'type': 'USER'}
        ]
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.check_compliance(mock_sddc_manager_context, desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success(self, mock_sddc_manager_context, mock_sddc_manager_rest_client):
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: [None, {'name': 'vsphere.local\\administrators', 'role': 'OPERATOR'}],
            consts.NEW: [{'name': 'test_user@vsphere.local', 'role': 'OPERATOR', 'type': 'USER'},
                         {'name': 'vsphere.local\\administrators', 'role': 'ADMIN'}]
        }
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.roles_response,
                                                                self.non_compliant_users_response,
                                                                self.sso_domain_response,
                                                                self.sso_domain_entities_response]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediation_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Test Exception")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediation_failed_invalid_user(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: RemediateStatus.FAILED,
            consts.ERRORS: ["Could not find 'USER: test_user@vsphere.local' in existing SSO users or groups on system."]
        }
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        sso_domain_entities_response = {
            'elements': [
                {'id': 'administrator@vsphere.local', 'name': 'administrator', 'type': 'USER'},
                {'id': 'vsphere.local\\Administrators', 'name': 'Administrators', 'type': 'GROUP'},
                {'id': 'vsphere.local\\CAAdmins', 'name': 'CAAdmins', 'type': 'GROUP'},
                {'id': 'vsphere.local\\SDDCAdmins', 'name': 'SDDCAdmins', 'type': 'GROUP'}
            ]
        }
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.roles_response,
                                                                self.non_compliant_users_response,
                                                                self.sso_domain_response,
                                                                sso_domain_entities_response]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_failed_incorrect_desired_value(self, mock_sddc_manager_rest_client,
                                                             mock_sddc_manager_context):
        errors = ["Role/type can not be modified for user/group 'administrator@vsphere.local'."
                  "Expected type: USER and role: ADMIN",
                  "Group 'vsphere.local\\\\caadmins' should be in expected format <DOMAIN>\\<GROUP_NAME>",
                  "User 'test_user_vsphere.local' should be in expected format <USER_NAME>@<DOMAIN>"]
        desired_value = [
            {'name': 'administrator@vsphere.local', 'role': 'OPERATOR', 'type': 'USER'},
            {'name': 'vsphere.local\\Administrators', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'VSPHERE.LOCAL\\\\CAAdmins', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'VSPHERE.LOCAL\\SDDCAdmins', 'role': 'ADMIN', 'type': 'GROUP'},
            {'name': 'test_user_vsphere.local', 'role': 'OPERATOR', 'type': 'USER'}
        ]
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result = self.controller.remediate(mock_sddc_manager_context, desired_value)
        assert result == expected_result
