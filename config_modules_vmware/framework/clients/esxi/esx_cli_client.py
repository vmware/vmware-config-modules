# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import os
import shutil
from typing import Tuple

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

ESX_CLI_CMD_FORMAT = "{esx_cli_path} --vihost {esx_hostname} --server {vc_hostname} -d {vc_ssl_thumbprint} {command}"


class EsxCliClient(object):
    """
    Client for invoking esxcli commands.
    """

    def __init__(self, vc_hostname: str, vc_username: str, vc_password: str, vc_ssl_thumbprint: str):
        """
        Initialize EsxCliClient.
        :param vc_hostname: vCenter hostname
        :type vc_hostname: :class:'str'
        :param vc_username: vCenter username
        :type vc_username: :class:'str'
        :param vc_password: vCenter Password
        :type vc_password: :class:'str'
        :param vc_ssl_thumbprint: vCenter thumbprint
        :type vc_ssl_thumbprint: :class:'str'
        """
        self._vc_hostname = vc_hostname
        self._vc_username = vc_username
        self._vc_password = vc_password
        self._vc_ssl_thumbprint = vc_ssl_thumbprint
        self._path = shutil.which("esxcli")

    def run_esx_cli_cmd(self, hostname: str, command: str) -> Tuple[str, str, int]:
        """
        Run the esxcli command against the given host.
        :param hostname: ESXi hostname
        :type hostname: str
        :param command: The esx cli command to run
        :type command: str
        :return: The output from stdout, stderr and return code
        :rtype: Tuple[str, str, int]
        :raise: ValueError if input command is empty or any exception raised by the subprocess module.
        :raise: FileNotFoundError if esxcli cannot be found
        """
        if self._path is None:
            err_msg = "esxcli command cannot be found. Please ensure esxcli is installed and available in PATH"
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
        esx_cli_cmd = ESX_CLI_CMD_FORMAT.format(
            esx_cli_path=self._path,
            esx_hostname=hostname,
            vc_hostname=self._vc_hostname,
            vc_ssl_thumbprint=self._vc_ssl_thumbprint,
            command=command,
        )
        env = os.environ.copy()
        env["VI_USERNAME"] = self._vc_username
        env["VI_PASSWORD"] = self._vc_password
        # Workaround for esxcli dependent on "HOME" environment variable
        if not env.get("HOME"):
            env["HOME"] = "/tmp"  # nosec
        return utils.run_shell_cmd(command=esx_cli_cmd, env=env)
