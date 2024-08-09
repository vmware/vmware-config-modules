# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class LockdownModeConfig(BaseController):
    """ESXi controller to get/set lockdown mode.

    | Config Id - 31
    | Config Title - Enable Normal lockdown mode on the host.

    """

    metadata = ControllerMetadata(
        name="lockdown_mode",  # controller name
        path_in_schema="compliance_config.esxi.lockdown_mode",
        # path in the schema to this controller's definition.
        configuration_id="31",  # configuration id as defined in compliance kit.
        title="Enable Normal lockdown mode on the host",
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

    def get(self, context: HostContext) -> Tuple[str, List[str]]:
        """Get lockdown mode for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of lockdown mode and a list of errors if any..
        :rtype: Tuple
        """
        logger.info("Getting lockdown mode for esxi.")
        errors = []
        lockdown_mode = "DISABLED"
        try:
            lockdown_mode_result = context.host_ref.configManager.hostAccessManager.lockdownMode
            logger.debug(f"Fetch result for lockdown mode for the esxi host: {lockdown_mode_result}")
            lockdown_mode_parts = lockdown_mode_result.split("lockdown")
            if len(lockdown_mode_parts) < 2:
                raise Exception("Unable to fetch lockdown mode")
            else:
                lockdown_mode = lockdown_mode_parts[1].upper()
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return lockdown_mode, errors

    def set(self, context: HostContext, desired_values: str) -> Tuple[RemediateStatus, List[str]]:
        """Set lockdown mode for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Lockdown mode - NORMAL or DISABLED or STRICT.
        :type desired_values: str
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting lockdown mode for esxi.")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            new_lockdown_mode = f"lockdown{desired_values.capitalize()}"
            context.host_ref.configManager.hostAccessManager.ChangeLockdownMode(new_lockdown_mode)
            logger.debug(f"Updated lockdown mode for the esxi host to {new_lockdown_mode}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
