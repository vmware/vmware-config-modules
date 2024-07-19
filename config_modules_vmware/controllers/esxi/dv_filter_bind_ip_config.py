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

SETTINGS_NAME = "Net.DVFilterBindIpAddress"
DV_FILTER_BIND_IP = "security_appliance_ip"


class DvFilterBindIpConfig(BaseController):
    """ESXi dvFilter configuration.

    | Config Id - 169
    | Config Title - Use of the dvFilter network APIs must be restricted.
    """

    metadata = ControllerMetadata(
        name="dv_filter_bind_ip_config",  # controller name
        path_in_schema="compliance_config.esxi.dv_filter_bind_ip_config",
        # path in the schema to this controller's definition.
        configuration_id="169",  # configuration id as defined in compliance kit.
        title="Use of the dvFilter network APIs must be restricted.",
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

    def get(self, context: HostContext) -> Tuple[dict, List[str]]:
        """Get dvFilter configuration for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of dict for DVFilterBindIpAdress and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting DVFilterBindIpAdress configuration for esxi.")
        errors = []
        dv_filter_bind_ip = {}
        try:
            # Fetch configuration from advanced option setting.
            result = esxi_advanced_settings_utils.invoke_advanced_option_query(context.host_ref, prefix=SETTINGS_NAME)
            dv_filter_bind_ip = {DV_FILTER_BIND_IP: result[0].value}
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return dv_filter_bind_ip, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set DVFilterBindIpAdress for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: dict such as {"security_appliance_ip": "10.0.0.250"} to update DVFilterBindIpAddress.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting DVFilterBindIpAdress in advanced option for esxi.")
        security_appliance_ip = desired_values.get(DV_FILTER_BIND_IP)
        host_option = vim.option.OptionValue(key=SETTINGS_NAME, value=security_appliance_ip)
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_advanced_settings_utils.update_advanced_option(context.host_ref, host_option=host_option)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
