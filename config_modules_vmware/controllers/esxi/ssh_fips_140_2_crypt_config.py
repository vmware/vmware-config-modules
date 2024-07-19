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

SSH_FIPS_140_2_CONFIG_GET = "system security fips140 ssh get"
SSH_FIPS_140_2_CONFIG_SET = lambda enable: f"system security fips140 ssh set --enable={enable}"


class SshFips140_2CryptConfig(BaseController):
    """ESXi controller to get/config ssh fips 140-2 validated cryptographic modules.

    | Config Id - 1100
    | Config Title - The ESXi host SSH daemon must use FIPS 140-2 validated cryptographic modules to protect the confidentiality of remote access sessions.

    """

    metadata = ControllerMetadata(
        name="ssh_fips_140_2_crypt_config",  # controller name
        path_in_schema="compliance_config.esxi.ssh_fips_140_2_crypt_config",
        # path in the schema to this controller's definition.
        configuration_id="1100",  # configuration id as defined in compliance kit.
        title="The ESXi host SSH daemon must use FIPS 140-2 validated cryptographic modules to protect the confidentiality of remote access sessions.",
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

    def get(self, context: HostContext) -> Tuple[bool, List[str]]:
        """Get SSH daemon FIPS 140-2 validated cryptographic modules config for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of boolean value True/False and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting SSH daemon FIPS 140-2 validated cryptographic modules config for esxi.")
        errors = []
        enabled = None
        try:
            cli_output, _, _ = context.esx_cli_client().run_esx_cli_cmd(context.hostname, SSH_FIPS_140_2_CONFIG_GET)
            enabled = cli_output.split(":")[1].strip().lower() == "true"
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return enabled, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set SSH daemon FIPS 140-2 validated cryptographic modules config for esxi host based on desired value.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: boolean value True/False to update config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting SSH daemon FIPS 140-2 validated cryptographic modules config for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            context.esx_cli_client().run_esx_cli_cmd(context.hostname, SSH_FIPS_140_2_CONFIG_SET(desired_values))
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
