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
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


logger = LoggerAdapter(logging.getLogger(__name__))

NAME = "name"
TYPE = "type"
ROLE = "role"
USER = "USER"
GROUP = "GROUP"


class UsersGroupsRolesConfig(BaseController):
    """Class for UsersGroupsRolesSettings config with get and set methods.
    | ConfigId - 415
    | ConfigTitle - The vCenter Server users must have the correct roles assigned.
    """

    metadata = ControllerMetadata(
        name="users_groups_roles",  # controller name
        path_in_schema="compliance_config.vcenter.users_groups_roles",
        # path in the schema to this controller's definition.
        configuration_id="415",  # configuration id as defined in compliance kit.
        title="The vCenter Server users must have the correct roles assigned.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List[Dict[str, str]], List[Any]]:
        """Get roles for users and groups.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of dictionary (with keys-'role', 'name', 'type') objects and a list of error messages.
        :rtype: Tuple
        """
        errors = []
        result = []
        try:
            content = context.vc_vmomi_client().content
            authorization_manager = content.authorizationManager
            role_collection = authorization_manager.roleList
            for role in role_collection:
                permissions = authorization_manager.RetrieveRolePermissions(role.roleId)
                for permission in permissions:
                    if permission.group is False:
                        result.append({ROLE: role.name, NAME: permission.principal, TYPE: USER})
                    else:
                        result.append({ROLE: role.name, NAME: permission.principal, TYPE: GROUP})

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """
        Set method is not implemented as this control requires user intervention to remediate.
        This needs to be reviewed manually before remediation as it could have potential impact on vCenter access.
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors
