# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging
import os
import shlex  # nosec CWE-78
import subprocess  # nosec CWE-78
from datetime import datetime
from typing import Tuple
from typing import Union

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


def read_json_file(json_file_path: str) -> dict:
    """
    Read and return the requested json file.
    @param json_file_path: the json file to read
    @type json_file_path: str
    @return: the requested json file in python object
    @rtype: dict
    """
    if os.path.exists(json_file_path) and os.path.isfile(json_file_path):
        try:
            with open(json_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding {json_file_path}': {e}.") from e
    else:
        raise Exception(f"Missing file {json_file_path}.")


def filter_dict_keys(data, desired_keys):
    """
    Filters a dictionary based on the desired keys.

    :param data: The input dictionary to be filtered.
    :type data: dict
    :param desired_keys: A list of keys to include in the filtered dictionary.
    :type desired_keys: list
    :return: A new dictionary containing only the key-value pairs corresponding to the desired keys.
    :rtype: dict
    """
    # Basic type checking
    if not isinstance(data, dict):
        raise TypeError("Input 'data' must be a dictionary.")
    if not isinstance(desired_keys, list):
        raise TypeError("Input 'desired_keys' must be a list.")

    # Handle missing keys
    return {key: data.get(key) for key in desired_keys if key in data}


def run_shell_cmd(
    command: str, timeout: int = None, raise_on_non_zero: bool = True, input_to_stdin: str = None, env: dict = None
) -> Tuple[str, str, int]:
    """
    Runs the given command as a shell command and returns the output.
    :param command: the shell command to invoke
    :type command: str
    :param timeout: timeout for the command
    :type timeout: int
    :param input_to_stdin: String to be sent as input (stdin) to the process.
    :type input_to_stdin: str
    :param env: environment variables to be set in the shell before executing commands.
    :type env: dict
    :param raise_on_non_zero: When set to true, it raises called processor error for all non-zero exit codes.
    :type raise_on_non_zero: bool
    :return: The output from stdout, stderr and return code
    :rtype: Tuple[str, str, int]
    :raise: ValueError if input command is empty or any exception raised by the subprocess module.
    """
    try:
        if not command:
            raise ValueError("Empty shell command provided")

        logger.info(f"Executing command {command} with timeout: {timeout} raise_on_error: {raise_on_non_zero}")
        result = subprocess.run(
            shlex.split(command),
            env=env,
            timeout=timeout,
            capture_output=True,
            text=True,
            check=raise_on_non_zero,
            input=input_to_stdin,  # nosec
        )

        output = result.stdout
        error = result.stderr
        ret_code = result.returncode
        if output:
            logger.debug(f"Output for {command} - {output}")
        if error:
            logger.debug(f"Error for {command} - {error}")
        if ret_code:
            logger.debug(f"Return code for {command} - {ret_code}")

        return output, error, ret_code
    except Exception as e:
        logger.error(f"Exception running shell command {command} - {e}")
        raise e


def get_current_time(format: str = consts.DEFAULT_TIMESTAMP_FORMAT) -> str:  # pylint: disable=W0622
    """
    Get current utc time in given format.
    :param format: Optional format string. Defaults to iso format(YYYY-MM-DDTHH:MM:SS.mmmmmm)
    :return: Formatted timestamp
    :rtype: str
    """
    return datetime.utcnow().strftime(format)


def is_newer_or_same_version(cur_version, ref_version):
    """
    Compare current version number to reference version (such as "4.5.X.X") and determines if it's newer.
    :param current_version: current version.
    :type str
    :param ref_version: reference version to compare with.
    :type str
    :return: true if current version is newer or same false if it is older.
    :rtype: boolean
    """
    if cur_version is None or ref_version is None:
        return False

    # Current version may contain build number as well. We only compare version number.
    cur_version = cur_version.split("-")[0]
    cur_version_list = [int(x) for x in cur_version.split(".")]
    ref_version_list = [int(x) for x in ref_version.split(".")]
    for i in range(len(min(cur_version_list, ref_version_list))):
        if cur_version_list[i] > ref_version_list[i]:
            return True
        elif cur_version_list[i] < ref_version_list[i]:
            return False

    return True


def get_product_major_version(product_version: str) -> Union[int, None]:
    """
    Get product major version from product_version string.

    :param product_version: The product version
    :type product_version: str
    :return: The major product version
    :rtype: int or None if not found/not valid
    """
    if product_version:
        try:
            return int(product_version.split(".")[0])
        except ValueError:
            return None
    return None
