# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

ACCEPTANCE_LEVEL = "acceptance_level"


class ImageProfileAcceptanceLevel(BaseController):
    """ESXi controller to get/config host image profile acceptance level..

    | Config Id - 157
    | Config Title - The ESXi Image Profile and vSphere Installation Bundle (VIB) Acceptance Levels must be verified.

    """

    metadata = ControllerMetadata(
        name="image_profile_acceptance_level",  # controller name
        path_in_schema="compliance_config.esxi.image_profile_acceptance_level",
        # path in the schema to this controller's definition.
        configuration_id="157",  # configuration id as defined in compliance kit.
        title="The ESXi Image Profile and vSphere Installation Bundle (VIB) Acceptance Levels must be verified",
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
        """Get image profile acceptance level for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of dict such as {"acceptance_level": "partner"} and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting host image profile acceptance level for esxi.")
        errors = []
        image_profile_acceptance_level = {}
        try:
            acceptance_level = context.host_ref.configManager.imageConfigManager.HostImageConfigGetAcceptance()
            image_profile_acceptance_level = {ACCEPTANCE_LEVEL: acceptance_level}
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return image_profile_acceptance_level, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set image profile acceptance level for esxi host based on desired value.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: dict of {"acceptance_level": "partner"} to update acceptance level.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting image profile acceptance level for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            acceptance_level = desired_values.get(ACCEPTANCE_LEVEL)
            context.host_ref.configManager.imageConfigManager.UpdateHostImageAcceptanceLevel(acceptance_level)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
