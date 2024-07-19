# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils import esxi_advanced_settings_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

SETTINGS_NAME = "DCUI.Access"


class LockdownDcuiAccessUsers(BaseController):
    """ESXi controller class to get/set/check compliance/remediate dcui access users(with unconditional access).

    | Config Id - 163
    | Config Title - The ESXi host must verify the DCUI.Access list.
    """

    metadata = ControllerMetadata(
        name="lockdown_dcui_access_users",  # controller name
        path_in_schema="compliance_config.esxi.lockdown_dcui_access_users",
        # path in the schema to this controller's definition.
        configuration_id="163",  # configuration id as defined in compliance kit.
        title="The ESXi host must verify the DCUI.Access list",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: HostContext) -> Tuple[List[str], List[str]]:
        """Get dcui access users (with unconditional access) configured for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of list of dcui access users and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting dcui access users configured for esxi.")
        errors = []
        dcui_access_users = []
        try:
            # Fetch dcui access users
            result = esxi_advanced_settings_utils.invoke_advanced_option_query(context.host_ref, prefix=SETTINGS_NAME)
            dcui_access_users_str = result[0].value
            logger.debug(f"Getting {SETTINGS_NAME} value: {dcui_access_users_str}")

            # Create sorted list of dcui access users
            dcui_access_users = [user.strip() for user in dcui_access_users_str.split(",")]
            logger.debug(f"List of DCUI access users configured: {dcui_access_users}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return dcui_access_users, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set dcui access users (with unconditional access) configured for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Desired value of dcui access users to be configured.
        :type desired_values: list
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting dcui access users configured for esxi.")
        dcui_access_users_str = ",".join(desired_values)
        logger.debug(f"Setting {SETTINGS_NAME} with users: {dcui_access_users_str}")

        host_option = vim.option.OptionValue(key=SETTINGS_NAME, value=dcui_access_users_str)
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_advanced_settings_utils.update_advanced_option(context.host_ref, host_option=host_option)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
