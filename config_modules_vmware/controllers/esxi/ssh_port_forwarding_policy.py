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

CONFIG_KEY = "allowtcpforwarding"


class SshPortForwardingPolicy(BaseController):
    """ESXi ssh port forwarding configuration. The control is automated only for vsphere 8.x and above.

    | Config Id - 1111
    | Config Title - The ESXi host Secure Shell (SSH) daemon must disable port forwarding.
    """

    metadata = ControllerMetadata(
        name="ssh_port_forwarding",  # controller name
        path_in_schema="compliance_config.esxi.ssh_port_forwarding",
        # path in the schema to this controller's definition.
        configuration_id="1111",  # configuration id as defined in compliance kit.
        title="The ESXi host Secure Shell (SSH) daemon must disable port forwarding.",
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
        """Get ssh port forwarding policy for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of str for 'AllowTcpForwarding' value and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting ssh port forwarding policy for esxi.")
        if not utils.is_newer_or_same_version(context.product_version, "8.0.0"):
            return self._get_skipped()
        else:
            errors = []
            ssh_port_forwarding_enabled = ""
            try:
                ssh_port_forwarding_enabled = esxi_ssh_config_utils.get_ssh_config_value(context, CONFIG_KEY)
            except Exception as e:
                logger.exception(f"An error occurred: {e}")
                errors.append(str(e))
            return ssh_port_forwarding_enabled, errors

    def _get_skipped(self) -> Tuple[str, List[str]]:
        return "", [consts.SKIPPED]

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set ssh port forwarding policy for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Desired value for 'AllowTcpForwarding' property.
        :type desired_values: str
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting ssh port forwarding policy for esxi.")
        if not utils.is_newer_or_same_version(context.product_version, "8.0.0"):
            return self._set_skipped()
        else:
            errors = []
            status = RemediateStatus.SUCCESS
            try:
                esxi_ssh_config_utils.set_ssh_config_value(context, CONFIG_KEY, desired_values)
            except Exception as e:
                logger.exception(f"An error occurred: {e}")
                errors.append(str(e))
                status = RemediateStatus.FAILED
            return status, errors

    def _set_skipped(self) -> Tuple[RemediateStatus, List[str]]:
        return RemediateStatus.SKIPPED, []

    def check_compliance(self, context: HostContext, desired_values: str) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: HostContext
        :param desired_values: Desired value for the 'AllowTcpForwarding' config.
        :type desired_values: str
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance.")
        ssh_port_forwarding_enabled, errors = self.get(context=context)
        return esxi_ssh_config_utils.check_compliance_for_ssh_config(
            current_value=ssh_port_forwarding_enabled, desired_value=desired_values, errors=errors
        )
