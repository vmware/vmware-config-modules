# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import List
from typing import Tuple

from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


def get_firewall_default_action(context: HostContext) -> Tuple[str, List[str]]:
    """
    :param context: ESXi context instance.
    :type context: HostContext
    :return: Tuple of str value DROP/PASS and a list of errors.
    :rtype: Tuple
    """
    errors = []
    default_action = None
    try:
        firewall_default_action_get_command = "network firewall get"
        cli_output, _, _ = context.esx_cli_client().run_esx_cli_cmd(
            context.hostname, firewall_default_action_get_command
        )
        logger.debug(f"cli_output is {cli_output}")
        match = re.search(r"Default Action:\s*(\w+)", cli_output)
        if not match:
            err_msg = f"Unable to fetch default action using command esxcli {firewall_default_action_get_command}"
            raise Exception(err_msg)
        else:
            default_action = match.group(1)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        errors.append(str(e))
    return default_action, errors


def set_firewall_default_action(context: HostContext, desired_values: str) -> Tuple[RemediateStatus, List[str]]:
    """
    :param context: Esxi context instance.
    :type context: HostContext
    :param desired_values: DROP/PASS to block/allow the network traffic.
    :type desired_values: str
    :return: Tuple of "status" and list of error messages.
    :rtype: Tuple
    """
    errors = []
    status = RemediateStatus.SUCCESS

    # Convert 'DROP' to 'false and 'PASS' to 'true' before feeding to set cli.
    is_action_pass = "true" if desired_values == "PASS" else "false"
    try:
        firewall_default_action_set_command = f"network firewall set --default-action={is_action_pass}"
        context.esx_cli_client().run_esx_cli_cmd(context.hostname, firewall_default_action_set_command)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        errors.append(str(e))
        status = RemediateStatus.FAILED
    return status, errors
