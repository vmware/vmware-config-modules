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

SETTINGS_NAME = "Syslog.global.logHost"


class RemoteLogServerConfig(BaseController):
    """ESXi controller for get/set remote log server configurations.

    | Config Id - 164
    | Config Title - Configure a remote log server for the ESXi hosts.
    """

    metadata = ControllerMetadata(
        name="remote_log_server_config",  # controller name
        path_in_schema="compliance_config.esxi.remote_log_server_config",
        # path in the schema to this controller's definition.
        configuration_id="164",  # configuration id as defined in compliance kit.
        title="Configure a remote log server for the ESXi hosts.",
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

    def get(self, context: HostContext) -> Tuple[List[str], List[str]]:
        """Get remote log server configurations for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of a list of remote log server string and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting remote log host for esxi.")
        errors = []
        remote_log_hosts = []
        try:
            # Fetch remote log hosts.
            result = esxi_advanced_settings_utils.invoke_advanced_option_query(context.host_ref, prefix=SETTINGS_NAME)
            remote_log_hosts = [host.strip() for host in result[0].value.split(",") if host.strip()]
            logger.debug(f"Remote log hosts: {remote_log_hosts}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return remote_log_hosts, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set remote log hosts for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: Desired value of remote log hosts.
        :type desired_values: a list of log hosts (str)
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting remote log hosts for esxi")
        remote_log_hosts = ",".join([s.strip() for s in desired_values]) if desired_values else ""
        host_option = vim.option.OptionValue(key=SETTINGS_NAME, value=remote_log_hosts)
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_advanced_settings_utils.update_advanced_option(context.host_ref, host_option=host_option)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
