# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
from typing import List

from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))


def get_ssh_config_value(context: HostContext, config_key: str) -> str:
    """
    Retrieve the ssh configuration value for the given key.
    :param context: Esxi context instance.
    :type context: HostContext
    :param config_key: SSH config key to retrieve
    :type config_key: str
    :return: The configuration value
    :rtype: str
    """
    esx_cli_command = f"system ssh server config list -k {config_key}"
    stdout, _, _ = context.esx_cli_client().run_esx_cli_cmd(context.hostname, esx_cli_command)

    try:
        # Example command output:
        # Key                 Value
        # ------------------  -----
        # allowtcpforwarding  no
        last_line = stdout.splitlines()[-1]
        key, val = last_line.split()
        if key != config_key:
            raise Exception(f"ssh config key was {key}, not {config_key}")
    except ValueError as e:
        err_msg = f"Could not find key in ssh config: '{config_key}'"
        raise Exception(err_msg) from e
    return val


def set_ssh_config_value(context: HostContext, config_key: str, config_val: str):
    """
    Set the ssh configuration value for the given key.
    :param context: Esxi context instance.
    :type context: HostContext
    :param config_key: SSH config key to retrieve
    :type config_key: str
    :param config_val: The configuration value to set
    :type config_val: str
    """
    esx_cli_command = f"system ssh server config set -k {config_key} -v {config_val}"
    context.esx_cli_client().run_esx_cli_cmd(context.hostname, esx_cli_command)


def check_compliance_for_ssh_config(current_value: str, desired_value: str, errors: List) -> Dict:
    """Helper method for checking compliance for ssh configurations.

    :param current_value: Current ssh config value.
    :type current_value: str
    :param desired_value: Desired ssh config value.
    :type desired_value: str
    :param errors: list
    :type errors: errors found during get config.
    :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
    :rtype: dict
    """
    if errors:
        if len(errors) == 1 and errors[0] == consts.SKIPPED:
            return {
                consts.STATUS: ComplianceStatus.SKIPPED,
                consts.ERRORS: [consts.CONTROL_NOT_AUTOMATED],
            }
        # If errors are seen during get, return "FAILED" status with errors.
        return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

    # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
    # Otherwise, return "COMPLIANT".
    current_config, desired_config = Comparator.get_non_compliant_configs(current_value, desired_value)
    if current_config or desired_config:
        result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: current_config,
            consts.DESIRED: desired_config,
        }
    else:
        result = {consts.STATUS: ComplianceStatus.COMPLIANT}
    return result
