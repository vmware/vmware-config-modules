# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

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
