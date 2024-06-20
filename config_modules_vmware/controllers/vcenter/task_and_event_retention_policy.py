# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

# VPX Config keys
VPX_TASK_MAX_AGE_KEY = "task.maxAge"
VPX_TASK_CLEANUP_ENABLED_KEY = "task.maxAgeEnabled"
VPX_EVENT_MAX_AGE_KEY = "event.maxAge"
VPX_EVENT_CLEANUP_ENABLED_KEY = "event.maxAgeEnabled"

# Desired state keys
DESIRED_TASK_MAX_AGE_KEY = "task_max_age"
DESIRED_TASK_CLEANUP_ENABLED_KEY = "task_cleanup_enabled"
DESIRED_EVENT_MAX_AGE_KEY = "event_max_age"
DESIRED_EVENT_CLEANUP_ENABLED_KEY = "event_cleanup_enabled"


class TaskAndEventRetentionPolicy(BaseController):
    """Manage Task and Event retention policy with get and set methods.

    | Config Id - 1226
    | Config Title - vCenter task and event retention must be set to a defined number of days.

    """

    metadata = ControllerMetadata(
        name="task_and_event_retention",  # controller name
        path_in_schema="compliance_config.vcenter.task_and_event_retention",  # path in the schema to this controller's definition.
        configuration_id="1226",  # configuration id as defined in compliance kit.
        title="vCenter task and event retention must be set to a defined number of days.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Get Task and event retention policy for vCenter.

        | Sample get output

        .. code-block:: json

            {
              "task_cleanup_enabled": true,
              "task_max_age": 50,
              "event_cleanup_enabled": true,
              "event_max_age": 50
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict with task and event retention policy and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = self.__get_task_and_event_retention_policy(vc_vmomi_client)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set Task and Event retention policy.

        | Recommended value task and event retention: >=30 days

        | Sample desired state

        .. code-block:: json

            {
              "task_cleanup_enabled": true,
              "task_max_age": 30,
              "event_cleanup_enabled": true,
              "event_max_age": 30
            }

        | Note: Increasing the events retention to more than 30 days will result in a significant increase of vCenter
            database size and could shut down the vCenter Server.
        | Please ensure that you enlarge the vCenter database accordingly.
        | Applied changes will take effect only after restarting vCenter Server manually.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the Task and event retention policies.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            _update_successful = self.__set_task_and_event_retention_policy(vc_vmomi_client, desired_values)
            if not _update_successful:
                status = RemediateStatus.FAILED
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def __get_task_and_event_retention_policy(self, vc_vmomi_client: VcVmomiClient) -> Dict:
        """
        Get task and event retention policy.

        | Sample Task and Event retention policy output

        .. code-block:: json

            {
                "task_cleanup_enabled": true,
                "task_max_age": 30,
                "event_cleanup_enabled": true,
                "event_max_age": 30
            }

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: Dictionary containing task and event retention policy information.
        :rtype: Dict
        """
        task_cleanup_enabled = vc_vmomi_client.get_vpxd_option_value(VPX_TASK_CLEANUP_ENABLED_KEY)
        task_max_age = vc_vmomi_client.get_vpxd_option_value(VPX_TASK_MAX_AGE_KEY)

        event_cleanup_enabled = vc_vmomi_client.get_vpxd_option_value(VPX_EVENT_CLEANUP_ENABLED_KEY)
        event_max_age = vc_vmomi_client.get_vpxd_option_value(VPX_EVENT_MAX_AGE_KEY)

        return {
            "task_cleanup_enabled": task_cleanup_enabled,
            "task_max_age": task_max_age,
            "event_cleanup_enabled": event_cleanup_enabled,
            "event_max_age": event_max_age,
        }

    def __set_task_and_event_retention_policy(self, vc_vmomi_client: VcVmomiClient, desired_values: Dict) -> bool:
        """
        Set Task and Event retention policy.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :param desired_values: Dictionary containing task and event retention policy information.
        :type desired_values: Dict
        :return: Returns bool denoting success/failure
        :rtype: bool
        """
        # Set Task config
        task_cleanup_enabled_success = vc_vmomi_client.set_vpxd_option_value(
            VPX_TASK_CLEANUP_ENABLED_KEY, desired_values.get(DESIRED_TASK_CLEANUP_ENABLED_KEY)
        )
        task_max_age_success = vc_vmomi_client.set_vpxd_option_value(
            VPX_TASK_MAX_AGE_KEY, desired_values.get(DESIRED_TASK_MAX_AGE_KEY)
        )

        # Set Event config
        event_cleanup_enabled_success = vc_vmomi_client.set_vpxd_option_value(
            VPX_EVENT_CLEANUP_ENABLED_KEY, desired_values.get(DESIRED_EVENT_CLEANUP_ENABLED_KEY)
        )
        event_max_age_success = vc_vmomi_client.set_vpxd_option_value(
            VPX_EVENT_MAX_AGE_KEY, desired_values.get(DESIRED_EVENT_MAX_AGE_KEY)
        )

        return (
            task_cleanup_enabled_success
            and task_max_age_success
            and event_cleanup_enabled_success
            and event_max_age_success
        )
