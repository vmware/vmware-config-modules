# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from pyVmomi import vim

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


def invoke_advanced_option_query(host_ref, prefix):
    """
    Query config manager advanced option using prefix
    :param host_ref: Host object reference of type vim.HostSystem
    :param prefix: str query
    :return: List of option values of type vim.option.OptionValue
    """

    try:
        options = host_ref.configManager.advancedOption.QueryOptions(prefix)
        if options is None or not isinstance(options, list):
            raise Exception("Invalid returned options")
    except vim.fault.InvalidName as e:
        error_message = f"Invalid query param: {prefix} for advanced options for host: {host_ref.name}"
        # pylint disabled on the following line. vim.fault.InvalidName is an Exception.
        raise Exception(error_message) from e  # pylint: disable=E0705
    except Exception as e:
        error_message = (
            f"Exception on querying advanced options: {prefix} for host: {host_ref.name} with error msg: {e}"
        )
        raise Exception(error_message) from e
    return options


def update_advanced_option(host_ref, host_option):
    """
    Update config manager advanced option using prefix
    :param host_ref: Host object reference of type vim.HostSystem
    :param host_option: list of option values of type vim.option.OptionValue
    :return: error_message or empty error_message
    """

    try:
        host_ref.configManager.advancedOption.UpdateOptions(changedValue=[host_option])
    except Exception as e:
        error_message = f"Exception on updating advanced options for host: {host_ref.name} with error msg: {e}"
        raise Exception(error_message) from e
