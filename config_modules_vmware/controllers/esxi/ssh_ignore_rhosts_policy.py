# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils import esxi_ssh_config_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

CONFIG_KEY = "ignorerhosts"


class SshIgnoreRHostsPolicy(BaseController):
    """ESXi ignore ssh rhosts configuration.

    | Config Id - 3
    | Config Title - The ESXi host Secure Shell (SSH) daemon must ignore .rhosts files.
    """

    metadata = ControllerMetadata(
        name="ssh_ignore_rhosts",  # controller name
        path_in_schema="compliance_config.esxi.ssh_ignore_rhosts",
        # path in the schema to this controller's definition.
        configuration_id="3",  # configuration id as defined in compliance kit.
        title="The ESXi host Secure Shell (SSH) daemon must ignore .rhosts files.",
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
        """Get ssh ignore rhosts policy for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of str for 'IgnoreRhosts' value and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting ssh ignore rhosts policy for esxi.")
        major_version = utils.get_product_major_version(context.product_version)
        if major_version and major_version >= 8:
            return self._get_v8(context)
        else:
            return self._get_skipped()

    def _get_skipped(self) -> Tuple[str, List[str]]:
        return "", [consts.SKIPPED]

    def _get_v8(self, context: HostContext) -> Tuple[str, List[str]]:
        errors = []
        ssh_ignore_rhosts = ""
        try:
            ssh_ignore_rhosts = esxi_ssh_config_utils.get_ssh_config_value(context, CONFIG_KEY)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return ssh_ignore_rhosts, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set ssh ignore rhosts policy for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Desired value for 'IgnoreRhosts' property.
        :type desired_values: str
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting ssh ignore rhosts policy for esxi.")
        major_version = utils.get_product_major_version(context.product_version)
        if major_version and major_version >= 8:
            return self._set_v8(context, desired_values)
        else:
            return self._set_skipped()

    def _set_skipped(self) -> Tuple[RemediateStatus, List[str]]:
        return RemediateStatus.SKIPPED, []

    def _set_v8(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_ssh_config_utils.set_ssh_config_value(context, CONFIG_KEY, desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
