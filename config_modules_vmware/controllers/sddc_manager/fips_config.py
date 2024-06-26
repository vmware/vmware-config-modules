# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class FipsConfig(BaseController):
    """
    Class for Fips config with get method.
    """

    metadata = ControllerMetadata(
        name="fips_mode_enabled",  # controller name
        path_in_schema="compliance_config.sddc_manager.fips_mode_enabled",  # path in the schema to this controller's definition.
        configuration_id="1608",  # configuration id as defined in compliance kit.
        title="SDDC Manager must be deployed with FIPS mode enabled",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.SDDC_MANAGER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context):
        """
        Get FIPS mode status.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext
        :return: Tuple of fips mode status (as a boolean data type) and list of error messages
        :rtype: tuple
        """

        logger.info("Getting FIPS mode details for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.FIPS_URL
        errors = []
        try:
            fips_resp = sddc_manager_rest_client.get_helper(url)

            if not isinstance(fips_resp, dict):
                raise TypeError("FIPS response is not a dictionary")
            logger.info(fips_resp)
            fips_mode = fips_resp["enabled"]

        except TypeError as te:
            errors.append(str(te))
            fips_mode = None
            logger.error(f"Type error: {te}")

        except KeyError as ke:
            errors.append(str(ke))
            fips_mode = None
            logger.error("Enabled key not found in the API response.")

        except Exception as e:
            errors.append(str(e))
            fips_mode = None

        return fips_mode, errors

    def set(self, context, desired_values):
        """
        Set will not be implemented as in current VCF versions we can't change FIPS mode post bringup.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext
        :param desired_values: True
        :type desired_values: boolean
        :return: Tuple of status and list of error messages
        :rtype: tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        logger.info("Remediate is not implemented as it is not possible to change FIPS mode post bringup")

        return status, errors
