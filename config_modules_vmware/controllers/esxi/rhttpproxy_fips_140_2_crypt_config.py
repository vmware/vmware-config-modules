# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class RHttpProxyFips140_2CryptConfig(BaseController):
    """ESXi controller to get/config ssh fips 140-2 validated cryptographic modules.

    | Config Id - 1117
    | Config Title - The ESXi host rhttpproxy daemon must use FIPS 140-2 validated cryptographic modules to protect the confidentiality of remote access sessions

    """

    metadata = ControllerMetadata(
        name="rhttpproxy_fips_140_2_crypt_config",  # controller name
        path_in_schema="compliance_config.esxi.rhttpproxy_fips_140_2_crypt_config",
        # path in the schema to this controller's definition.
        configuration_id="1117",  # configuration id as defined in compliance kit.
        title="The ESXi host rhttpproxy daemon must use FIPS 140-2 validated cryptographic modules to protect the confidentiality of remote access sessions",
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
        """Get rhttpproxy daemon FIPS 140-2 validated cryptographic modules config for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of boolean value True/False and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting rhttpproxy daemon FIPS 140-2 validated cryptographic modules config for esxi.")
        errors = []
        enabled = None
        try:
            rtthpproxy_fips_140_2_get_command = "system security fips140 rhttpproxy get"
            cli_output, _, _ = context.esx_cli_client().run_esx_cli_cmd(
                context.hostname, rtthpproxy_fips_140_2_get_command
            )
            logger.debug(f"cli_output is {cli_output}")
            match = re.search(r"Enabled:\s*(\w+)", cli_output)
            if not match:
                err_msg = (
                    f"Unable to fetch rhttpproxy fips config using command esxcli {rtthpproxy_fips_140_2_get_command}"
                )
                raise Exception(err_msg)
            else:
                enabled = match.group(1).lower() == "true"
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return enabled, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set rhttpproxy daemon FIPS 140-2 validated cryptographic modules config for esxi host based on desired value.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: boolean value True/False to update config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting rhttpproxy daemon FIPS 140-2 validated cryptographic modules config for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            enabled_str = "true" if desired_values is True else "false"
            rtthpproxy_fips_140_2_set_command = f"system security fips140 rhttpproxy set --enable={enabled_str}"
            context.esx_cli_client().run_esx_cli_cmd(context.hostname, rtthpproxy_fips_140_2_set_command)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
