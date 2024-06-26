# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client import VcVmomiSSOClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

TRUSTED_ADMINS_GROUP_KEY = "TrustedAdmins"
ID_KEY = "id"
DOMAIN_KEY = "domain"
NAME_KEY = "name"
MEMBER_TYPE_KEY = "member_type"
MEMBER_TYPE_USER = "USER"
MEMBER_TYPE_GROUP = "GROUP"


class SSOTrustedAdminsAuthorizedMembersConfig(BaseController):
    """Manage authorized members in the TrustedAdmins group with get and set methods.

    | Config Id - 1217
    | Config Title - vCenter must limit membership to the TrustedAdmins SSO group.

    """

    metadata = ControllerMetadata(
        name="sso_trusted_admin_authorized_members",  # controller name
        path_in_schema="compliance_config.vcenter.sso_trusted_admin_authorized_members",
        # path in the schema to this controller's definition.
        configuration_id="1217",  # configuration id as defined in compliance kit.
        title="vCenter must limit membership to the TrustedAdmins SSO group.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,
        # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List, List[Any]]:
        """Get authorized members (users and groups) in the TrustedAdmins group.

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
        :return: Tuple of List of dictionaries containing user and groups belonging to the TrustedAdmins group and a
            list of error messages.
        :rtype: tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        try:
            result = self.__get_all_members_of_trusted_admins_group(vc_vmomi_sso_client)
        except Exception as e:
            logger.exception(f"An error occurred whole retrieving members from SSO TrustedAdmins group: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def __get_all_members_of_trusted_admins_group(self, sso_client: VcVmomiSSOClient) -> List[Dict]:
        """Retrieve all members in TrustedAdmins group.

        :param sso_client: VcVmomiSSOClient instance
        :type sso_client: VcVmomiSSOClient
        :return: List of dictionaries containing user and groups belonging to the TrustedAdmins group.
        :rtype: List[Dict]
        """
        members_in_trusted_admins_group = []

        system_domain = sso_client.get_system_domain()
        logger.info(f"Retrieved system domain - {system_domain}")

        trusted_admins_group = sso_client._get_group(TRUSTED_ADMINS_GROUP_KEY, system_domain)
        logger.info(f"Retrieved TrustedAdmins group - {trusted_admins_group}")

        if trusted_admins_group and hasattr(trusted_admins_group, ID_KEY):
            group_id = trusted_admins_group.id
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
                        members_in_trusted_admins_group.append(user)

            for group in groups_in_group:
                if hasattr(group, ID_KEY):
                    group_principal_id = group.id
                    group_name = getattr(group_principal_id, NAME_KEY)
                    domain = getattr(group_principal_id, DOMAIN_KEY)

                    if group_name and domain:
                        group = {NAME_KEY: group_name, DOMAIN_KEY: domain, MEMBER_TYPE_KEY: MEMBER_TYPE_GROUP}
                        members_in_trusted_admins_group.append(group)

        logger.info(f"Retrieved all members in TrustedAdmins group {members_in_trusted_admins_group}")
        return members_in_trusted_admins_group

    def set(self, context: VcenterContext, desired_values: List) -> Tuple[str, List[Any]]:
        """Remediation has not been implemented for this control. It's possible that a customer may legitimately add
         a new user and forget to update the control accordingly. Remediating the control could lead to the removal of
         these users, with potential unknown implications.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: List of objects containing users and groups details with name, domain and member_type.
        :type desired_values: List
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors
