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

VPX_SDDC_COMPLIANCE_KIT_KEY = "config.SDDC.Deployed.ComplianceKit"


class VpxSDDCDeployedComplianceKitConfig(BaseController):
    """Manage Compliance kit configuration value for a recognized security control framework or standard
        (e.g., NIST-800-53) with get and set methods.

    | Config Id - 0000
    | Config Title - Set Compliance kit configuration value for a recognized security control framework or standard.

    """

    metadata = ControllerMetadata(
        name="vpx_sddc_deployed_compliance_kit_config",  # controller name
        path_in_schema="compliance_config.vcenter.vpx_sddc_deployed_compliance_kit_config",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Manage Compliance kit configuration value for a recognized security control framework or standard",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[str, List[Any]]:
        """Get Compliance kit configuration value for a recognized security control framework or standard
        (e.g., NIST-800-53).

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of SDDC deployed compliance kit configuration value as string and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = vc_vmomi_client.get_vpxd_option_value(VPX_SDDC_COMPLIANCE_KIT_KEY)
        except Exception as e:
            logger.exception(f"An error occurred while getting {VPX_SDDC_COMPLIANCE_KIT_KEY}: {e}")
            errors.append(str(e))
            result = None
        return result, errors

    def set(self, context: VcenterContext, desired_values: str) -> Tuple[str, List[Any]]:
        """Set Compliance kit configuration value for a recognized security control framework or standard
        (e.g., NIST-800-53).

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for SDDC compliance kit configuration value.
        :type desired_values: String
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            _update_successful = vc_vmomi_client.set_vpxd_option_value(VPX_SDDC_COMPLIANCE_KIT_KEY, desired_values)
            if not _update_successful:
                status = RemediateStatus.FAILED
                errors.append(f"Failed to set VPXD option value for {VPX_SDDC_COMPLIANCE_KIT_KEY}")
        except Exception as e:
            logger.exception(f"An error occurred while setting {VPX_SDDC_COMPLIANCE_KIT_KEY}: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
