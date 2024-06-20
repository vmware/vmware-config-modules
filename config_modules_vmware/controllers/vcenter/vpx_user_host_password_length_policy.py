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

VPX_USER_HOST_PASSWORD_LENGTH_POLICY = "config.vpxd.hostPasswordLength"  # nosec


class VpxUserPasswordLengthPolicy(BaseController):
    """Manage VPX User host password length policy with get and set methods.

    | Config Id - 427
    | Config Title - The vCenter Server must configure the vpxuser host password meets length policy.

    """

    metadata = ControllerMetadata(
        name="vpx_host_password_length_policy",  # controller name
        path_in_schema="compliance_config.vcenter.vpx_host_password_length_policy",  # path in the schema to this controller's definition.
        configuration_id="427",  # configuration id as defined in compliance kit.
        title="The vCenter Server must configure the vpxuser host password meets length policy.",  # controller title as defined in compliance kit.
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
        """Get VPX user host password length policy.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of VPX password length policy as int or None if not configured and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = vc_vmomi_client.get_vpxd_option_value(VPX_USER_HOST_PASSWORD_LENGTH_POLICY)
            # Convert the result to an integer if it's not None.
            # This conversion is necessary to align with the schema.
            # Keeping this as number in schema for min/max validation
            result = int(result) if result else None
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = None
        return result, errors

    def set(self, context: VcenterContext, desired_values: int) -> Tuple[str, List[Any]]:
        """
        Set VPX user host password length policy.

        | Recommended vpx user password length: >=32 characters or Null

        | Note: The vpxuser password default length is 32 characters.
        | Ensure this setting meets site policies; if not, configure to meet password length policies.
        | Longer passwords make brute-force password attacks more difficult.
        | The vpxuser password is added by vCenter, meaning no manual intervention is normally required.
        | The vpxuser password length must never be modified to less than the default length of 32 characters.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VPX user host password length policy.
        :type desired_values: int
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            # Converting the integer to a string as VPXD settings only accept string values.
            # Retaining the value as a number in the schema for the purpose of min/max validation.
            password_length_str = str(desired_values)
            _update_successful = vc_vmomi_client.set_vpxd_option_value(
                VPX_USER_HOST_PASSWORD_LENGTH_POLICY, password_length_str
            )
            if not _update_successful:
                status = RemediateStatus.FAILED
                errors.append(f"Failed to set VPXD option value for {VPX_USER_HOST_PASSWORD_LENGTH_POLICY}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
