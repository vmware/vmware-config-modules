# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils import esxi_advanced_settings_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

SETTINGS_NAME = "UserVars.ESXiVPsDisabledProtocols"

SUPPORTED_PROTOCOLS_SET = {"sslv3", "tlsv1", "tlsv1.1", "tlsv1.2"}


class TlsVersion(BaseController):
    """ESXi controller class to get/set/check compliance/remediate tls protocols on esxi hosts.

    | Config Id - 1107
    | Config Title - The ESXi host must exclusively enable TLS 1.2 for all endpoints.
    """

    metadata = ControllerMetadata(
        name="tls_version",  # controller name
        path_in_schema="compliance_config.esxi.tls_version",
        # path in the schema to this controller's definition.
        configuration_id="1107",  # configuration id as defined in compliance kit.
        title="The ESXi host must exclusively enable TLS 1.2 for all endpoints",
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

    def get(self, context: HostContext) -> Tuple[int, List[str]]:
        """Get tls protocols enabled for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of list of enabled tls/ssl protocols and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting tls versions enabled for esxi.")
        errors = []
        enabled_protocols = []
        try:
            # Fetch disabled tls protocols and create a list of enabled protocols
            result = esxi_advanced_settings_utils.invoke_advanced_option_query(context.host_ref, prefix=SETTINGS_NAME)
            disabled_protocols_str = result[0].value
            logger.debug(f"Getting {SETTINGS_NAME} value: {disabled_protocols_str}")

            # Product allows duplicates values in the input disabled protocols string like "tlsv1,tlsv1"
            # So, using set to remove the duplicates. Create sorted list of enabled protocols
            disabled_protocols = {protocol.strip() for protocol in disabled_protocols_str.split(",")}
            enabled_protocols = sorted(list(SUPPORTED_PROTOCOLS_SET - disabled_protocols))
            logger.debug(f"List of TLS/SSL protocols enabled: {enabled_protocols}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return enabled_protocols, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set tls protocols enabled for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Desired value of tls/ssl protocols to be enabled.
        :type desired_values: list
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting tls versions to be enabled for esxi.")
        disabled_protocols = list(SUPPORTED_PROTOCOLS_SET - set(desired_values))
        disabled_protocols_str = ",".join(disabled_protocols)
        logger.debug(f"Setting {SETTINGS_NAME} with protocols: {disabled_protocols_str}")

        host_option = vim.option.OptionValue(key=SETTINGS_NAME, value=disabled_protocols_str)
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_advanced_settings_utils.update_advanced_option(context.host_ref, host_option=host_option)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
