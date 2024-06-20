# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import MagicMock

from config_modules_vmware.controllers.esxi.utils import esxi_ssh_config_utils


class TestEsxiSshConfigUtils:

    def setup_method(self):
        self.context = MagicMock()
        self.esx_cli_client = MagicMock()
        self.context.esx_cli_client.return_value = self.esx_cli_client

    def test_get_ssh_config_value_success(self):
        cmd_output ="""Key                 Value
        ------------------  -----
        allowtcpforwarding  no"""
        self.esx_cli_client.run_esx_cli_cmd.return_value = (cmd_output, "", 0)
        ssh_config_value = esxi_ssh_config_utils.get_ssh_config_value(self.context, "allowtcpforwarding")
        assert ssh_config_value == "no"

    def test_get_ssh_config_value_no_matching_key(self):
        cmd_output ="""Key                 Value
        ------------------  -----
        invalid             no"""
        self.esx_cli_client.run_esx_cli_cmd.return_value = (cmd_output, "", 0)
        with pytest.raises(Exception):
            esxi_ssh_config_utils.get_ssh_config_value(self.context, "allowtcpforwarding")

    def test_get_ssh_config_value_value(self):
        cmd_output ="""Key                 Value
        ------------------  -----
        allowtcpforwarding"""
        with pytest.raises(Exception):
            self.esx_cli_client.run_esx_cli_cmd.return_value = (cmd_output, "", 0)
            esxi_ssh_config_utils.get_ssh_config_value(self.context, "allowtcpforwarding")

    def test_set_ssh_config_value(self):
        esxi_ssh_config_utils.set_ssh_config_value(self.context, "key", "val")
        self.esx_cli_client.run_esx_cli_cmd.assert_called_once()
