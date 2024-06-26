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

ESXI_SERVICE_CIM = "sfcbd-watchdog"
SERVICE_RUNNING = "service_running"
SERVICE_POLICY = "service_policy"


class CimServicePolicy(BaseController):
    """ESXi controller to start/stop/update cim service.

    | Config Id - 1126
    | Config Title - The ESXi CIM service must be disabled.

    """

    metadata = ControllerMetadata(
        name="cim_service_policy",  # controller name
        path_in_schema="compliance_config.esxi.cim_service_policy",
        # path in the schema to this controller's definition.
        configuration_id="1126",  # configuration id as defined in compliance kit.
        title="The ESXi CIM service must be disabled.",
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
        """Get cim service status for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of dict such as {"service_running": True, "service_policy": "off"} and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting cim service status for esxi.")
        errors = []
        cim_service_status = {}
        try:
            host_service = context.host_ref.configManager.serviceSystem
            util = HostServiceUtil(host_service)
            cim_service_status, errors = util.get_service_status(ESXI_SERVICE_CIM)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return cim_service_status, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Start/stop cim service for esxi host based on desired value.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: dict of { "service_running": True, "service_policy": "off"} to start/stop service or update policy.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting cim service policy for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            host_service = context.host_ref.configManager.serviceSystem
            util = HostServiceUtil(host_service)
            util.start_stop_service(ESXI_SERVICE_CIM, desired_values.get(SERVICE_RUNNING))
            util.update_service_policy(ESXI_SERVICE_CIM, desired_values.get(SERVICE_POLICY))
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
