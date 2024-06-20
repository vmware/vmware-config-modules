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

VPX_SYSLOG_ENABLEMENT_CONFIG_KEY = "vpxd.event.syslog.enabled"


class VpxSyslogEnablementPolicy(BaseController):
    """Manage VPX syslog enablement config with get and set methods

    | Config Id - 1221
    | Config Title - The vCenter Server must be configured to send events to a central log server.

    """

    metadata = ControllerMetadata(
        name="vpx_syslog_enablement_policy",  # controller name
        path_in_schema="compliance_config.vcenter.vpx_syslog_enablement_policy",  # path in the schema to this controller's definition.
        configuration_id="1221",  # configuration id as defined in compliance kit.
        title="The vCenter Server must be configured to send events to a central log server.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[bool, List[Any]]:
        """Get VPX syslog enablement config.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of VPX syslog enablement config as bool and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = vc_vmomi_client.get_vpxd_option_value(VPX_SYSLOG_ENABLEMENT_CONFIG_KEY)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = None
        return result, errors

    def set(self, context: VcenterContext, desired_values: bool) -> Tuple[str, List[Any]]:
        """
        Set VPX syslog enablement config.

        | Recommended syslog configuration: true | enabled

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VPX syslog enablement policy
        :type desired_values: Bool
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            _update_successful = vc_vmomi_client.set_vpxd_option_value(VPX_SYSLOG_ENABLEMENT_CONFIG_KEY, desired_values)
            if not _update_successful:
                status = RemediateStatus.FAILED
                errors.append(f"Failed to set VPXD option value for {VPX_SYSLOG_ENABLEMENT_CONFIG_KEY}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
