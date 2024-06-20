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


class SSOPasswordReusePolicy(BaseController):
    """Manage SSO Password reuse restriction Policy with get and set methods.

    | Config Id - 403
    | Config Title - The vCenter Server must prohibit password reuse.

    """

    metadata = ControllerMetadata(
        name="sso_password_reuse_restriction",  # controller name
        path_in_schema="compliance_config.vcenter.sso_password_reuse_restriction",  # path in the schema to this controller's definition.
        configuration_id="403",  # configuration id as defined in compliance kit.
        title="The vCenter Server must prohibit password reuse.",  # controller title as defined in compliance kit.
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
        Get SSO password reuse restriction policy.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of an integer for the number of previous passwords restricted and a list of error messages.
        :rtype: tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        try:
            result = vc_vmomi_sso_client.get_password_reuse_restriction()
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = -1
        return result, errors

    def set(self, context: VcenterContext, desired_values: int) -> Tuple[str, List[Any]]:
        """
        Set SSO password reuse restriction  policy.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the number of previous passwords restricted.
        :type desired_values: int
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            sso_prohibit_password_reuse_count = desired_values
            if not isinstance(sso_prohibit_password_reuse_count, int) or sso_prohibit_password_reuse_count < 0:
                raise ValueError("value must be a positive integer")
            vc_vmomi_sso_client.set_password_reuse_restriction(restrict_count=sso_prohibit_password_reuse_count)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
