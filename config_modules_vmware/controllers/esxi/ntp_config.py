# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

PROTOCOL = "protocol"
NTP_PROTOCOL = "ntp"
NTP_SERVERS = "servers"


class NtpConfig(BaseController):
    """ESXi controller to get/set ntp configurations for hosts.

    | Config Id - 147
    | Config Title - ESXi host must configure NTP time synchronization.

    """

    metadata = ControllerMetadata(
        name="ntp_config",  # controller name
        path_in_schema="compliance_config.esxi.ntp_config",
        # path in the schema to this controller's definition.
        configuration_id="147",  # configuration id as defined in compliance kit.
        title="ESXi host must configure NTP time synchronization.",
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
        """Get ntp configuration for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of dict ({"protocol": "ntp", "server": ["10.0.0.250"]}) and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting ntp configurations for esxi.")
        time_configs = {}
        errors = []
        try:
            datetime_info = context.host_ref.config.dateTimeInfo
            time_protocol = datetime_info.systemClockProtocol
            if time_protocol == NTP_PROTOCOL:
                ntp_config = datetime_info.ntpConfig
                time_configs[NTP_SERVERS] = [ip for ip in ntp_config.server]
            time_configs[PROTOCOL] = time_protocol
            logger.debug(f"Datetime configurations for esxi: {time_configs}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return time_configs, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set ntp configurations for esxi host based on desired values.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: dict of { "protocol": "ntp", "server": ["10.0.0.250"] }.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting ntp configiurations for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            protocol = desired_values.get(PROTOCOL)
            servers = [ip for ip in desired_values.get(NTP_SERVERS)]
            datetime_config = vim.host.DateTimeConfig()
            datetime_config.protocol = protocol
            datetime_config.ntpConfig = vim.host.NtpConfig()
            datetime_config.ntpConfig.server = servers
            logger.debug(f"Updating ntp configiurations for esxi with {desired_values}")
            context.host_ref.configManager.dateTimeSystem.UpdateDateTimeConfig(config=datetime_config)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
