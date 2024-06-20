# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class SSOAutoUnlockInterval(BaseController):
    """Manage SSO Auto Unlock Interval Policy with get and set methods.

    | Config Id - 435
    | Config Title - The vCenter server passwords should meet max auto unlock interval policy.

    """

    metadata = ControllerMetadata(
        name="sso_auto_unlock_interval",  # controller name
        path_in_schema="compliance_config.vcenter.sso_auto_unlock_interval",  # path in the schema to this controller's definition.
        configuration_id="435",  # configuration id as defined in compliance kit.
        title="The vCenter server passwords should meet max auto unlock interval policy.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[int, List[Any]]:
        """
        Get SSO auto unlock interval.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of an integer for the auto unlock interval in seconds and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        try:
            result = vc_vmomi_sso_client.get_auto_unlock_interval()
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = -1
        return result, errors

    def set(self, context: VcenterContext, desired_values: int) -> Tuple[str, List[Any]]:
        """
        Set SSO auto unlock interval.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the SSO auto unlock interval in seconds.
        :type desired_values: int
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            sso_auto_unlock_interval_sec = desired_values
            if not isinstance(sso_auto_unlock_interval_sec, int) or sso_auto_unlock_interval_sec < 0:
                raise ValueError("value must be a positive integer")
            vc_vmomi_sso_client.set_auto_unlock_interval(interval=sso_auto_unlock_interval_sec)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
