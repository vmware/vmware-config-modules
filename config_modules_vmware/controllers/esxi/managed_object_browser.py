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

SETTINGS_NAME = "Config.HostAgent.plugins.solo.enableMob"


class ManagedObjectBrowser(BaseController):
    """ESXi controller class to configure managed object browser settings.

    | Config Id - 166
    | Config Title - The ESXi host must disable the Managed Object Browser (MOB).
    """

    metadata = ControllerMetadata(
        name="managed_object_browser",  # controller name
        path_in_schema="compliance_config.esxi.managed_object_browser",
        # path in the schema to this controller's definition.
        configuration_id="166",  # configuration id as defined in compliance kit.
        title="The ESXi host must disable the Managed Object Browser (MOB).",
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

    def get(self, context: HostContext) -> Tuple[int, List[str]]:
        """Get managed object browser setting for ESXi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of boolean for the managed object browser flag and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting managed object browser setting for esxi.")
        errors = []
        mob_flag = False
        try:
            # Fetch password max lifetime.
            result = esxi_advanced_settings_utils.invoke_advanced_option_query(context.host_ref, prefix=SETTINGS_NAME)
            mob_flag = result[0].value
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return mob_flag, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set managed object browser setting for ESXi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Desired value of managed object browser flag
        :type desired_values: boolean
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting managed object browser setting for esxi.")
        host_option = vim.option.OptionValue(key=SETTINGS_NAME, value=desired_values)
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_advanced_settings_utils.update_advanced_option(context.host_ref, host_option=host_option)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
