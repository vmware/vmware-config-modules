# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
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

CONFIG_KEY = "strictmodes"


class SshStrictModePolicy(BaseController):
    """ESXi ssh host strict mode settings.
    The control is automated only for vsphere 8.x and above. No remediation support as the property is no configurable.

    | Config Id - 11
    | Config Title - ESXi host SSH daemon performs strict mode checking of home directory configuration files.
    """

    metadata = ControllerMetadata(
        name="ssh_strict_mode",  # controller name
        path_in_schema="compliance_config.esxi.ssh_strict_mode",
        # path in the schema to this controller's definition.
        configuration_id="11",  # configuration id as defined in compliance kit.
        title="ESXi host SSH daemon performs strict mode checking of home directory configuration files",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: HostContext) -> Tuple[str, List[str]]:
        """Get ssh host strict mode settings for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of str for 'strictmodes' value and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting ssh host strict mode policy for esxi.")
        if not utils.is_newer_or_same_version(context.product_version, "8.0.0"):
            return "", [consts.SKIPPED]
        else:
            errors = []
            strict_mode_settings = ""
            try:
                strict_mode_settings = esxi_ssh_config_utils.get_ssh_config_value(context, CONFIG_KEY)
            except Exception as e:
                logger.exception(f"An error occurred: {e}")
                errors.append(str(e))
            return strict_mode_settings, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set ssh host strict mode settings for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Desired value for 'strictmodes' config.
        :type desired_values: str
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting ssh host strict mode policy for esxi.")
        if not utils.is_newer_or_same_version(context.product_version, "8.0.0"):
            errors = [consts.CONTROL_NOT_AUTOMATED]
        else:
            errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def check_compliance(self, context: HostContext, desired_values: str) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: HostContext
        :param desired_values: Desired value for the ssh host strict mode settings.
        :type desired_values: str
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance.")
        strict_mode_settings, errors = self.get(context=context)
        return esxi_ssh_config_utils.check_compliance_for_ssh_config(
            current_value=strict_mode_settings, desired_value=desired_values, errors=errors
        )
