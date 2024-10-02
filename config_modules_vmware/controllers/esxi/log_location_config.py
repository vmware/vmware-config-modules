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

LOG_LOCATION = "log_location"
IS_PERSISTENT = "is_persistent"


class LogLocationConfig(BaseController):
    """ESXi controller to get/set/check_compliance/remediate persistent log location config.

    | Config Id - 136
    | Config Title - Configure a persistent log location for all locally stored logs.

    """

    metadata = ControllerMetadata(
        name="log_location_config",  # controller name
        path_in_schema="compliance_config.esxi.log_location_config",
        # path in the schema to this controller's definition.
        configuration_id="136",  # configuration id as defined in compliance kit.
        title="Configure a persistent log location for all locally stored logs",
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

    def _is_log_location_persistent(self, context: HostContext) -> bool:
        """Check if the log location is persistent.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: True if log location is persistent otherwise False.
        :rtype: bool
        :raises: Exception if fetching the config fails.
        """
        persistent_log_config_get_command = "system syslog config get"
        cli_output, _, _ = context.esx_cli_client().run_esx_cli_cmd(context.hostname, persistent_log_config_get_command)
        logger.debug(f"{persistent_log_config_get_command} output is {cli_output}")

        # Fetch persistent flag.
        match = re.search(r"Local Log Output Is Persistent:\s*(\w+)", cli_output)
        if not match:
            err_msg = f"Unable to fetch persistent flag using command esxcli {persistent_log_config_get_command}"
            raise Exception(err_msg)

        return match.group(1).lower() == "true"

    def _get_log_location(self, context: HostContext) -> str:
        """Get log location for the esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Log location.
        :rtype: str
        :raises: Exception if fetching the config fails.
        """
        persistent_log_config_get_command = "system syslog config get"
        out, err, ret_code = context.esx_cli_client().run_esx_cli_cmd(
            hostname=context.hostname, command=persistent_log_config_get_command, raise_on_non_zero=False
        )
        logger.debug(f"{persistent_log_config_get_command} output is {out}")

        if ret_code:
            err_msg = f"Command esxcli {persistent_log_config_get_command} failed."
            if out:
                err_msg += f" {out}"
            if err:
                err_msg += f" {err}"
            raise Exception(err_msg)

        # Fetch persistent flag.
        match = re.search(r"Local Log Output:\s*(/.+)", out)
        if not match:
            err_msg = f"Unable to fetch log location using command esxcli {persistent_log_config_get_command}"
            raise Exception(err_msg)

        return match.group(1)

    def _set_log_location(self, context: HostContext, log_location: str):
        """Set log location for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :param log_location: Log location
        :type log_location: str
        :raises: Exception if there is any error during set operation
        """
        persistent_log_config_set_command = f"system syslog config set --logdir={log_location}"
        out, err, ret_code = context.esx_cli_client().run_esx_cli_cmd(
            hostname=context.hostname, command=persistent_log_config_set_command, raise_on_non_zero=False
        )
        if ret_code:
            err_msg = f"Command esxcli {persistent_log_config_set_command} failed."
            if out:
                err_msg += f" {out}"
            if err:
                err_msg += f" {err}"
            raise Exception(err_msg)

    def get(self, context: HostContext) -> Tuple[dict, List[str]]:
        """Get persistent log location config for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of dictionary with keys "log_location" and "is_persistent" and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting persistent log location config for syslog for esxi.")
        errors = []
        persistent_log_config = {}
        try:
            persistent_log_config = {
                IS_PERSISTENT: self._is_log_location_persistent(context),
                LOG_LOCATION: self._get_log_location(context),
            }

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return persistent_log_config, errors

    def set(self, context: HostContext, desired_values: dict) -> Tuple[RemediateStatus, List[str]]:
        """Set persistent log location config for esxi host.
        It sets the log location and verifies if the log location persistent criteria matches with desired or not.
        If it does not, then reverts to the original log location and report error

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: dictionary with keys "log_location" and "is_persistent"
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting persistent log location config for syslog for esxi.")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            current_log_location = self._get_log_location(context)

            is_persistent_required = desired_values.get(IS_PERSISTENT)

            desired_log_location = desired_values.get(LOG_LOCATION)
            logger.debug(f"Set the desired logdir to {desired_log_location}")
            self._set_log_location(context=context, log_location=desired_log_location)
            if is_persistent_required != self._is_log_location_persistent(context):
                # Revert the location path and report error message
                self._set_log_location(context=context, log_location=current_log_location)
                err_msg = (
                    f"'log_location: {desired_log_location}' is not matching the "
                    f"desired criteria 'is_persistent: {is_persistent_required}'"
                )
                raise Exception(err_msg)

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
