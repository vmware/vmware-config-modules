# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils import firewall_default_action_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class FirewallDefaultActionIncoming(BaseController):
    """ESXi controller to get/set firewall default action for incoming traffic.

    | Config Id - 105
    | Config Title - The ESXi host must configure the firewall to block incoming network traffic by default.

    """

    metadata = ControllerMetadata(
        name="firewall_default_action_incoming",  # controller name
        path_in_schema="compliance_config.esxi.firewall_default_action_incoming",
        # path in the schema to this controller's definition.
        configuration_id="105",  # configuration id as defined in compliance kit.
        title="The ESXi host must configure the firewall to block incoming network traffic by default",
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
        """Get firewall default action for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of str value DROP/PASS and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting firewall default action incoming traffic for esxi.")
        return firewall_default_action_utils.get_firewall_default_action(context)

    def set(self, context: HostContext, desired_values: str) -> Tuple[RemediateStatus, List[str]]:
        """Set firewall default action for esxi host based on desired value.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: DROP/PASS to block/allow the network traffic.
        :type desired_values: str
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting firewall default action incoming traffic for esxi.")
        return firewall_default_action_utils.set_firewall_default_action(context, desired_values)
