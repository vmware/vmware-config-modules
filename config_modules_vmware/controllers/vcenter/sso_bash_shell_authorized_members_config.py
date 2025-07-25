# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.vcenter.utils.sso_member_utils import filter_member_configs
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client import VcVmomiSSOClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))

BASH_SHELL_ADMINISTRATOR_GROUP_KEY = "SystemConfiguration.BashShellAdministrators"
ID_KEY = "id"
DOMAIN_KEY = "domain"
NAME_KEY = "name"
MEMBER_TYPE_KEY = "member_type"
MEMBER_TYPE_USER = "USER"
MEMBER_TYPE_GROUP = "GROUP"
TO_ADD = "+"
TO_REMOVE = "-"


class SSOBashShellAuthorizedMembersConfig(BaseController):
    """Manage authorized members in the SystemConfiguration.BashShellAdministrators group with get and set methods.

    | Config Id - 1216
    | Config Title - vCenter must limit membership to the SystemConfiguration.BashShellAdministrators SSO group.

    """

    metadata = ControllerMetadata(
        name="sso_bash_shell_authorized_members",  # controller name
        path_in_schema="compliance_config.vcenter.sso_bash_shell_authorized_members",
        # path in the schema to this controller's definition.
        configuration_id="1216",  # configuration id as defined in compliance kit.
        title="vCenter must limit membership to the SystemConfiguration.BashShellAdministrators SSO group.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List, List[Any]]:
        """Get authorized members in the SystemConfiguration.BashShellAdministrators group.

        | We limit our traversal to the first level of groups because a group can have subgroups, which in turn can
            contain groups with users. This approach is consistent with the behavior of the dir-cli command:

        .. code-block:: shell

            /usr/lib/vmware-vmafd/bin/dir-cli group list --name <group_name>

        | Sample get output

        .. code-block:: json

            [
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

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of List of dictionaries containing user and groups belonging to the BashShellAdministrators
         group and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        try:
            result = self.__get_all_members_of_bash_shell_administrator_group(vc_vmomi_sso_client)
        except Exception as e:
            logger.exception(f"An error occurred while retrieving members of bash shell admin group: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def __get_all_members_of_bash_shell_administrator_group(self, sso_client: VcVmomiSSOClient) -> List[Dict]:
        """Retrieve all members in SystemConfiguration.BashShellAdministrators group.

        :param sso_client: VcVmomiSSOClient instance
        :type sso_client: VcVmomiSSOClient
        :return: List of dictionaries containing user and groups belonging to the BashShellAdministrators group.
        :rtype: List[Dict]
        """
        members_in_bash_shell_administrators_group = []

        system_domain = sso_client.get_system_domain()
        logger.info(f"Retrieved system domain - {system_domain}")

        bash_shell_admin_group = sso_client._get_group(BASH_SHELL_ADMINISTRATOR_GROUP_KEY, system_domain)
        logger.info(f"Retrieved bash shell admin group - {bash_shell_admin_group}")

        if bash_shell_admin_group and hasattr(bash_shell_admin_group, ID_KEY):
            group_id = bash_shell_admin_group.id
            users_in_group = sso_client.find_users_in_group(group_id)
            logger.debug(f"Users in group - {users_in_group}")
            groups_in_group = sso_client.find_groups_in_group(group_id)
            logger.debug(f"Groups in group - {groups_in_group}")

            for user in users_in_group:
                if hasattr(user, ID_KEY):
                    user_principal_id = user.id
                    user_name = getattr(user_principal_id, NAME_KEY)
                    domain = getattr(user_principal_id, DOMAIN_KEY)

                    if user_name and domain:
                        user = {NAME_KEY: user_name, DOMAIN_KEY: domain, MEMBER_TYPE_KEY: MEMBER_TYPE_USER}
                        members_in_bash_shell_administrators_group.append(user)

            for group in groups_in_group:
                if hasattr(group, ID_KEY):
                    group_principal_id = group.id
                    group_name = getattr(group_principal_id, NAME_KEY)
                    domain = getattr(group_principal_id, DOMAIN_KEY)

                    if group_name and domain:
                        group = {NAME_KEY: group_name, DOMAIN_KEY: domain, MEMBER_TYPE_KEY: MEMBER_TYPE_GROUP}
                        members_in_bash_shell_administrators_group.append(group)

        logger.info(
            f"Retrieved all members in SystemConfiguration.BashShellAdministrators"
            f" group {members_in_bash_shell_administrators_group}"
        )
        return members_in_bash_shell_administrators_group

    def _normalize(self, item: Dict) -> Dict:
        """Name and domain are case insensitive, ignore case when do comparison.
        :param item: dict item of a bash shell authorized member.
        :type item: Dict
        :return: dict of normalized item.
        :rtype: Dict
        """
        return {
            NAME_KEY: item[NAME_KEY].lower(),
            MEMBER_TYPE_KEY: item[MEMBER_TYPE_KEY],
            DOMAIN_KEY: item[DOMAIN_KEY].lower(),
        }

    def _gen_remediate_configs(self, current: List, desired: List) -> Dict:
        """Compare current and desired bash shell authorized members to generate remediate configs.

        :param current: Current list of bash shell authorized members.
        :type current: List
        :param desired: Desired list of bash shell authorized members.
        :type desired: list
        :return: Dict of "+"/"-" items for remediation, {} if nothing to add or remove
        :rtype: Dict
        """

        logger.debug(f"Current members - {current}, desired members: {desired}")
        current_set = {tuple(self._normalize(item).values()): item for item in current}
        desired_set = {tuple(self._normalize(item).values()): item for item in desired}
        current_keys = set(current_set.keys())
        desired_keys = set(desired_set.keys())
        # if item in current but not in desired, to remove.
        to_remove = [current_set[key] for key in current_keys - desired_keys]
        # if item in desired but not in current, to add.
        to_add = [desired_set[key] for key in desired_keys - current_keys]
        # group operations based on type (user or group).
        operations = defaultdict(lambda: {TO_ADD: [], TO_REMOVE: []})
        for item in to_remove:
            operations[item[MEMBER_TYPE_KEY]][TO_REMOVE].append(item)
        for item in to_add:
            operations[item[MEMBER_TYPE_KEY]][TO_ADD].append(item)
        # return empty if no operation needed.
        result = {k: v for k, v in operations.items() if v[TO_ADD] or v[TO_REMOVE]}
        logger.debug(f"Remediate configs - {result}")

        return result

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """Remediation has not been implemented for this control. It's possible that a customer may legitimately add
         a new user and forget to update the control accordingly. Remediating the control could lead to the removal
         of these users, with potential unknown implications.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Dict of objects containing users and groups details with name, domain and member_type
                               and operaions to "add" or "remove".
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """

        status = RemediateStatus.SUCCESS
        errors = []

        try:
            logger.debug(f"Remediation - {desired_values}")
            vc_vmomi_sso_client = context.vc_vmomi_sso_client()

            # Remediate group members.
            group_opers = desired_values.get("GROUP", [])
            if group_opers:
                logger.debug(f"Group operations - {group_opers}")
                # Handle remove
                groups_to_remove = group_opers.get(TO_REMOVE, [])
                for group_to_remove in groups_to_remove:
                    logger.debug(f"Removing user - {group_to_remove}")
                    vc_vmomi_sso_client.remove_from_group(
                        BASH_SHELL_ADMINISTRATOR_GROUP_KEY, group_to_remove[NAME_KEY], group_to_remove[DOMAIN_KEY]
                    )
                # Handle add
                groups_to_add = group_opers.get(TO_ADD, [])
                for group_to_add in groups_to_add:
                    logger.debug(f"Adding group - {group_to_add}")
                    vc_vmomi_sso_client.add_group_to_group(
                        BASH_SHELL_ADMINISTRATOR_GROUP_KEY, group_to_add[NAME_KEY], group_to_add[DOMAIN_KEY]
                    )
            # Remediate user members.
            user_opers = desired_values.get("USER", [])
            if user_opers:
                logger.debug(f"User operations - {user_opers}")
                # Handle remove
                users_to_remove = user_opers.get(TO_REMOVE, [])
                for user_to_remove in users_to_remove:
                    logger.debug(f"Removing user - {user_to_remove}")
                    vc_vmomi_sso_client.remove_from_group(
                        BASH_SHELL_ADMINISTRATOR_GROUP_KEY, user_to_remove[NAME_KEY], user_to_remove[DOMAIN_KEY]
                    )
                # Handle add
                users_to_add = user_opers.get(TO_ADD, [])
                for user_to_add in users_to_add:
                    logger.debug(f"Adding user - {user_to_add}")
                    vc_vmomi_sso_client.add_user_to_group(
                        BASH_SHELL_ADMINISTRATOR_GROUP_KEY, user_to_add[NAME_KEY], user_to_add[DOMAIN_KEY]
                    )
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED

        return status, errors

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Check compliance of authorized members.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for authorized members.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance for sso bash shell authorized member config")
        all_member_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # check if need to exclude any members.
        exclude_user_patterns = desired_values.get("exclude_user_patterns", [])
        if exclude_user_patterns:
            logger.debug(f"User input name patterns to be excluded from compliance check: {exclude_user_patterns}")
            all_member_configs = filter_member_configs(all_member_configs, exclude_user_patterns)

        desired_members = desired_values.get("members", [])
        non_compliant_configs, _ = Comparator.get_non_compliant_configs(
            [self._normalize(item) for item in all_member_configs], [self._normalize(item) for item in desired_members]
        )

        if non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: all_member_configs,
                consts.DESIRED: desired_members,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Remediate configuration drifts by applying desired values.

        | Sample desired state

        .. code-block:: json

            {
              "members": [
                {
                  "name": "test-group",
                  "domain": "vsphere.local",
                  "member_type": "GROUP",
                },
                {
                  "name": "test-user",
                  "domain": "vsphere.local",
                  "member_type": "USER",
                },
                {
                  "name": "ad-ldap-user",
                  "domain": "adldap.com",
                  "member_type": "USER",
                }
              ],
              "exclude_user_patterns": [
                "vmware-applmgmtservice-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for sso bash shell authorized members
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running remediation for SSO bash shell authorized members")
        all_member_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        # check if need to exclude any members.
        exclude_user_patterns = desired_values.get("exclude_user_patterns", [])
        if exclude_user_patterns:
            logger.debug(f"User input name patterns to be excluded from remediation: {exclude_user_patterns}")
            all_member_configs = filter_member_configs(all_member_configs, exclude_user_patterns)

        remediate_configs = self._gen_remediate_configs(all_member_configs, desired_values.get("members", []))
        if not remediate_configs:
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        status, errors = self.set(context, remediate_configs)
        if not errors:
            return {
                consts.STATUS: status,
                consts.OLD: all_member_configs,
                consts.NEW: desired_values.get("members", []),
            }
        return {consts.STATUS: status, consts.ERRORS: errors}
