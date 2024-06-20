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

VPX_USER_PASSWORD_EXPIRATION_DAYS_KEY = "VirtualCenter.VimPasswordExpirationInDays"  # nosec


class VpxUserPasswordExpirationPolicy(BaseController):
    """Manage VPX User password expiration policy with get and set methods.

    | Config Id - 428
    | Config Title - The vCenter Server must configure the vpxuser auto-password to be changed periodically.

    """

    metadata = ControllerMetadata(
        name="vpx_password_expiration_policy",  # controller name
        path_in_schema="compliance_config.vcenter.vpx_password_expiration_policy",  # path in the schema to this controller's definition.
        configuration_id="428",  # configuration id as defined in compliance kit.
        title="The vCenter Server must configure the vpxuser auto-password to be changed periodically.",  # controller title as defined in compliance kit.
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
        """Get VPX user password expiration policy.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of VPX password expiration policy as int or None if not configured and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = vc_vmomi_client.get_vpxd_option_value(VPX_USER_PASSWORD_EXPIRATION_DAYS_KEY)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = None
        return result, errors

    def set(self, context: VcenterContext, desired_values: int) -> Tuple[str, List[Any]]:
        """
        Set VPX user password expiration policy.

        | Recommended value: 30 Days

        | Note: By default, vCenter will change the "vpxuser" password automatically every 30 days.
        | Ensure this setting meets site policies. If it does not, configure it to meet password aging policies.
        | It is very important the password aging policy is not shorter than the default interval that is
            set to automatically change the "vpxuser" password to preclude the possibility that vCenter might be
            locked out of an ESXi host.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VPX user password expiration policy in days.
        :type desired_values: int
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            _update_successful = vc_vmomi_client.set_vpxd_option_value(
                VPX_USER_PASSWORD_EXPIRATION_DAYS_KEY, desired_values
            )
            if not _update_successful:
                status = RemediateStatus.FAILED
                errors.append(f"Failed to set VPXD option value for {VPX_USER_PASSWORD_EXPIRATION_DAYS_KEY}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
