# Copyright 2024 Broadcom. All Rights Reserved.
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
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))
ID = "id"
NAME = "name"
ELEMENTS = "elements"
TYPE = "type"
ROLE = "role"
USERS_GROUPS_ROLES_INFO = "users_groups_roles_info"


class UsersGroupsRolesConfig(BaseController):
    """Class for UsersGroupsRolesSettings config with get and set methods.
    | ConfigId - 1605
    | ConfigTitle - Assign least privileges to users and service accounts in SDDC Manager.
    """

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

    def get(self, context: SDDCManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get UsersGroupsRolesSettings config for audit control.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext
        :return: Tuple of dict with key "users_groups_roles_info" and list of error messages.
        :rtype: tuple
        """
        logger.debug("Getting UsersGroupsRolesSettings control config for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        users_url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.USERS_URL
        roles_url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.ROLES_URL
        errors = []
        try:
            users_response = sddc_manager_rest_client.get_helper(users_url)
            roles_response = sddc_manager_rest_client.get_helper(roles_url)

            users_groups_roles_response = {
                USERS_GROUPS_ROLES_INFO: [
                    {
                        NAME: user.get(NAME),
                        TYPE: user.get(TYPE),
                        ROLE: next(
                            (
                                role[NAME]
                                for role in roles_response.get(ELEMENTS, {})
                                if role[ID] == user.get(ROLE).get(ID)
                            ),
                            None,
                        ),
                    }
                    for user in users_response.get(ELEMENTS, {})
                ]
            }
        except Exception as e:
            errors.append(str(e))
            users_groups_roles_response = {}
        return users_groups_roles_response, errors

    def set(self, context: SDDCManagerContext, desired_values: Dict) -> Tuple:
        """
        Set method is not implemented as this control requires user intervention to remediate.
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors
