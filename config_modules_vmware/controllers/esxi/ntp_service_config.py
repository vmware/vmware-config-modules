# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils.service_utils import HostServiceUtil
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

ESXI_SERVICE_NTP = "ntpd"
SERVICE_RUNNING = "service_running"


class NtpServiceConfig(BaseController):
    """ESXi controller to start/stop ntp service..

    | Config Id - 149
    | Config Title - Start NTP service on the ESXi host.

    """

    metadata = ControllerMetadata(
        name="ntp_service_config",  # controller name
        path_in_schema="compliance_config.esxi.ntp_service_config",
        # path in the schema to this controller's definition.
        configuration_id="149",  # configuration id as defined in compliance kit.
        title="Start NTP service on the ESXi host.",
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
        """Get ntp service running status for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of dict ({"service_running": True}) and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting ntp service running status for esxi.")
        ntp_service_running_status = {}
        errors = []
        try:
            host_service = context.host_ref.configManager.serviceSystem
            util = HostServiceUtil(host_service)
            ntp_service_status, errors = util.get_service_status(ESXI_SERVICE_NTP)
            if not errors:
                ntp_service_running_status = {SERVICE_RUNNING: ntp_service_status.get(SERVICE_RUNNING)}
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return ntp_service_running_status, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Start/stop ntp service for esxi host based on desired value.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: dict of { "service_running": True" } to start/stop service.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting ntp service running configiuration for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            host_service = context.host_ref.configManager.serviceSystem
            util = HostServiceUtil(host_service)
            util.start_stop_service(ESXI_SERVICE_NTP, desired_values.get(SERVICE_RUNNING))
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
