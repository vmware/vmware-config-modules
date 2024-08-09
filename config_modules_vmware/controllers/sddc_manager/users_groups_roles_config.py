# Copyright 2024 Broadcom. All Rights Reserved.
import copy
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client import SDDCManagerRestClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList

logger = LoggerAdapter(logging.getLogger(__name__))
ID = "id"
NAME = "name"
ELEMENTS = "elements"
TYPE = "type"
ROLE = "role"
DOMAIN = "domain"
USERID = "user_id"

# Dictionary of users/groups which are to be ignored for compliance and remediation operation.
USERS_GROUPS_IGNORE_DICT = {
    "administrator@vsphere.local": {TYPE: "USER", ROLE: "ADMIN"},
    "vsphere.local\\sddcadmins": {TYPE: "GROUP", ROLE: "ADMIN"},
}


class UsersGroupsRolesConfig(BaseController):
    """Class for UsersGroupsRolesSettings config with get and set methods.
    | ConfigId - 1605
    | ConfigTitle - Assign least privileges to users and service accounts in SDDC Manager.
    """

    def __init__(self):
        # Initialize instance key with "name" and comparator option with Identifier based comparison.
        super().__init__()
        self.comparator_option = ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON
        self.instance_key = NAME
        self.current_users_groups_roles_list = None
        self.role_name_to_role_id_dict = None
        self.role_id_to_role_name_dict = None

    metadata = ControllerMetadata(
        name="users_groups_roles",  # controller name
        path_in_schema="compliance_config.sddc_manager.users_groups_roles",  # path in the schema to this controller's definition.
        configuration_id="1605",  # configuration id as defined in compliance kit.
        title="Assign least privileges to users and service accounts in SDDC Manager.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.SDDC_MANAGER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def _populate_role_id_name_mapping(self, rest_client: SDDCManagerRestClient):
        """Create role name to role id dict and role id to role name dict.

        :param rest_client: SDDCManagerRestClient.
        :type rest_client: SDDCManagerRestClient
        """
        if self.role_name_to_role_id_dict is None or self.role_id_to_role_name_dict is None:
            roles_url = rest_client.get_base_url() + sddc_manager_consts.ROLES_URL
            roles_response = rest_client.get_helper(roles_url)
            self.role_name_to_role_id_dict = {}
            self.role_id_to_role_name_dict = {}
            for role in roles_response.get(ELEMENTS, {}):
                self.role_name_to_role_id_dict[role.get(NAME)] = role.get(ID)
                self.role_id_to_role_name_dict[role.get(ID)] = role.get(NAME)
            logger.debug(f"role name to id mapping {self.role_name_to_role_id_dict}")

    def _get_current_users_groups_roles(self, rest_client: SDDCManagerRestClient) -> List[Dict]:
        """Helper method to get current users/groups roles

        :param rest_client: SDDCManagerRestClient.
        :type rest_client: SDDCManagerRestClient
        :return: List of elements with current users/groups and roles info.
        :rtype: List[dict]
        """
        if self.current_users_groups_roles_list is None:
            self._populate_role_id_name_mapping(rest_client)
            self.current_users_groups_roles_list = []
            users_url = rest_client.get_base_url() + sddc_manager_consts.USERS_URL
            users_response = rest_client.get_helper(users_url)
            for user in users_response.get(ELEMENTS, {}):
                if user.get(NAME).lower() in USERS_GROUPS_IGNORE_DICT:
                    logger.debug(f"Ignoring {user.get(NAME).lower()}")
                    continue
                if user.get(TYPE) == "GROUP" or user.get(TYPE) == "USER":
                    self.current_users_groups_roles_list.append(
                        {
                            NAME: user.get(NAME).lower(),
                            TYPE: user.get(TYPE),
                            ROLE: self.role_id_to_role_name_dict[user.get(ROLE).get(ID)],
                            DOMAIN: user.get(DOMAIN),
                            USERID: user.get(ID),
                        }
                    )
            logger.debug(f"List of current users  {self.current_users_groups_roles_list}")
        return self.current_users_groups_roles_list

    def _create_names_to_attributes_mapping(self, users_groups_roles_list: List) -> Dict:
        """Create a dictionary with key as name and values as dictionary with keys-role, userid, domain, type.

        :param users_groups_roles_list: List of elements with users/groups and roles info.
        :return: Dict with name as key and values as dict attributes (role, userid, domain , type)
        :rtype: Dict
        """
        users_groups_roles_dict = {}
        for user_group_role in users_groups_roles_list:
            entity_type = user_group_role.get(TYPE)
            key = user_group_role.get(NAME).lower()
            users_groups_roles_dict[key] = {
                ROLE: user_group_role.get(ROLE),
                USERID: user_group_role.get(USERID),
                DOMAIN: user_group_role.get(DOMAIN),
                TYPE: entity_type,
            }
        return users_groups_roles_dict

    def _get_domain_from_name(self, name: str, entity_type: str) -> str:
        """Return domain from the user/group name.

        :param name: user/group name
        :type name: str
        :param entity_type: 'USER' or 'GROUP'
        :type entity_type: str
        :return: domain the user/groups belongs to
        :rtype: str
        """
        if entity_type == "GROUP":
            name_parts = name.split("\\")
            domain = name_parts[0].lower()
        else:
            domain = name.split("@")[1].lower()
        return domain

    def _get_all_sso_users_groups(self, rest_client: SDDCManagerRestClient) -> Dict:
        """Get dictionary of user/group name to entity type['USER' or 'GROUP'] for all sso users/groups in the system.

        :param rest_client: SDDCManagerRestClient.
        :type rest_client: SDDCManagerRestClient
        :return: Dictionary of sso user/group name as key and type as value
        """
        sso_domain_url = rest_client.get_base_url() + sddc_manager_consts.SSO_DOMAINS_URL
        sso_domains_response = rest_client.get_helper(sso_domain_url)
        logger.debug(f"Response for sso_domains:  {sso_domains_response}")
        all_sso_users = {}
        for sso_domain in sso_domains_response.get(ELEMENTS, []):
            sso_domain_entities_url = (
                f"{rest_client.get_base_url()}{sddc_manager_consts.SSO_DOMAINS_URL}/{sso_domain}/entities"
            )
            sso_domain_entities_response = rest_client.get_helper(sso_domain_entities_url)
            logger.debug(f"Response for sso_domains_entities: {sso_domain_entities_response}")
            for entity in sso_domain_entities_response.get(ELEMENTS, []):
                key = entity.get(ID).lower()
                if entity.get(TYPE) == "GROUP" or entity.get(TYPE) == "USER":
                    key = entity.get(ID).lower()
                else:
                    continue
                all_sso_users[key] = entity.get(TYPE)
        logger.debug(f"List of all sso users and groups in system: {all_sso_users}")
        return all_sso_users

    def _sanitize_desired_values(self, desired_values: List) -> Tuple[Dict, List[Any]]:
        """Parse desired values and remove the elements if part of ignore list and,
        remove extra "\" characters from the group name.

        :param desired_values: Desired list of elements with keys - name, type, role.
        :type desired_values: List[dict]
        :return: sanitized desired values
        :rtype: Tuple[dict, List]
        """
        errors = []
        for element in desired_values:
            element[NAME] = element[NAME].lower()
            name = element.get(NAME)
            entity_type = element.get(TYPE)
            role_name = element.get(ROLE)
            if name in USERS_GROUPS_IGNORE_DICT:
                if (
                    entity_type != USERS_GROUPS_IGNORE_DICT[name][TYPE]
                    or role_name != USERS_GROUPS_IGNORE_DICT[name][ROLE]
                ):
                    errors.append(
                        f"Role/type can not be modified for user/group '{name}'."
                        f"Expected type: {USERS_GROUPS_IGNORE_DICT[name][TYPE]} "
                        f"and role: {USERS_GROUPS_IGNORE_DICT[name][ROLE]}"
                    )

            if entity_type == "GROUP" and name.count("\\") != 1:
                errors.append(f"Group '{name}' should be in expected format <DOMAIN>\\<GROUP_NAME>")
            if entity_type == "USER" and "@" not in name:
                errors.append(f"User '{name}' should be in expected format <USER_NAME>@<DOMAIN>")

        if not errors:
            desired_values = [
                element for element in desired_values if element.get(NAME).lower() not in USERS_GROUPS_IGNORE_DICT
            ]

        return desired_values, errors

    def get(self, context: SDDCManagerContext) -> Tuple[List[Dict], List[Any]]:
        """Get UsersGroupsRolesSettings config for audit control.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext
        :return: Tuple of list of "users_groups_roles" and list of error messages.
        :rtype: tuple [list, list]
        """
        logger.debug("Getting UsersGroupsRolesSettings control config for audit.")
        errors = []
        users_groups_roles = []
        try:
            sddc_manager_rest_client = context.sddc_manager_rest_client()
            self._get_current_users_groups_roles(sddc_manager_rest_client)
            users_groups_roles = copy.deepcopy(self.current_users_groups_roles_list)
            for element in users_groups_roles:
                del element[DOMAIN]
                del element[USERID]

        except Exception as e:
            errors.append(str(e))
        return users_groups_roles, errors

    def set(self, context: SDDCManagerContext, desired_values: List[Dict]) -> Tuple[RemediateStatus, List[Any]]:
        """Set UsersGroupsRolesSettings config for audit control.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext
        :param desired_values: Desired values of the users, groups and roles
        :type desired_values: list[dict]
        :return: Tuple of remediation status and list of error messages.
        :rtype: tuple[str, list]
        """
        logger.debug("Setting UsersGroupsRolesSettings control config for audit.")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            sddc_manager_rest_client = context.sddc_manager_rest_client()
            self._populate_role_id_name_mapping(sddc_manager_rest_client)
            self._get_current_users_groups_roles(sddc_manager_rest_client)

            all_sso_users = self._get_all_sso_users_groups(sddc_manager_rest_client)
            current_users_role_map = self._create_names_to_attributes_mapping(self.current_users_groups_roles_list)
            desired_users_role_map = self._create_names_to_attributes_mapping(desired_values)

            # Modification of any mapping is deletion of the existing mapping and creation of new mapping.
            # To be deleted
            delete_users_list = []
            for key, value in current_users_role_map.items():
                if key in desired_users_role_map and desired_users_role_map[key].get(ROLE) == value.get(ROLE):
                    continue
                delete_users_list.append(value.get(USERID))

            # To be created
            create_users_list = []
            for key, value in desired_users_role_map.items():
                if (
                    key in current_users_role_map
                    and value.get(ROLE) == current_users_role_map[key].get(ROLE)
                    and value.get(TYPE) == current_users_role_map[key].get(TYPE)
                ):
                    continue
                if key not in all_sso_users or all_sso_users[key] != value.get(TYPE):
                    errors.append(
                        f"Could not find '{value.get(TYPE)}: {key}' in existing SSO users or groups on system."
                    )
                else:
                    create_users_list.append(
                        {
                            NAME: key,
                            DOMAIN: self._get_domain_from_name(key, value.get(TYPE)),
                            TYPE: value.get(TYPE),
                            ROLE: {ID: self.role_name_to_role_id_dict[value.get(ROLE)]},
                        }
                    )
            if errors:
                status = RemediateStatus.FAILED
            else:
                # All the users/groups are present in the system, continue with remediation,
                # Delete the unwanted users/groups - roles mapping
                logger.debug(f"List of users to be deleted: {delete_users_list}")
                users_url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.USERS_URL
                for user_id in delete_users_list:
                    delete_user_url = users_url + f"/{user_id}"
                    sddc_manager_rest_client.delete_helper(delete_user_url)

                # Create the required users/groups - roles mapping
                logger.debug(f"List of users to be created: {create_users_list}")
                create_users_url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.USERS_URL
                payload = create_users_list
                sddc_manager_rest_client.post_helper(url=create_users_url, body=payload)
        except Exception as e:
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def check_compliance(self, context: SDDCManagerContext, desired_values: List) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: List
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        sanitized_desired_values, errors = self._sanitize_desired_values(desired_values)
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}
        return super().check_compliance(context, desired_values=sanitized_desired_values)

    def remediate(self, context: BaseContext, desired_values: List) -> Dict:
        """Remediation with provided desired values.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: List
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        sanitized_desired_values, errors = self._sanitize_desired_values(desired_values)
        if errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return super().remediate(context, desired_values=sanitized_desired_values)
