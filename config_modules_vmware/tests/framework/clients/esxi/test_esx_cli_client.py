# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import patch

from config_modules_vmware.framework.clients.esxi.esx_cli_client import EsxCliClient


class TestEsxCliClient:

    def setup_method(self):
        self.esxi_hostname = "esxi_hostname"
        self.vc_hostname = "vc_hostname"
        self.vc_username = "vc_username"
        self.vc_password = "vc_password"
        self.vc_ssl_thumbprint = "vc_ssl_thumbprint"

    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    @patch('shutil.which')
    def test_run_esx_cli_cmd(self, mock_shutil_which, mock_run_shell_cmd):
        mock_shutil_which.return_value = "/usr/bin/esxcli"
        esx_cli_client = EsxCliClient(
            self.vc_hostname, self.vc_username, self.vc_password, self.vc_ssl_thumbprint
        )
        mock_run_shell_cmd.return_value = ("stdout", "stderr", 0)
        esx_cli_client.run_esx_cli_cmd("hostname", "cmd")
        _, kwargs = mock_run_shell_cmd.call_args
        assert "command" in kwargs
        assert "cmd" in kwargs["command"]
        assert "env" in kwargs
        assert kwargs["env"]["VI_USERNAME"] == self.vc_username
        assert kwargs["env"]["VI_PASSWORD"] == self.vc_password
        assert "HOME" in kwargs["env"]

    @patch('shutil.which')
    def test_run_esx_cli_cmd_path_not_found(self, mock_shutil_which):
        mock_shutil_which.return_value = None
        esx_cli_client = EsxCliClient(
            self.vc_hostname, self.vc_username, self.vc_password, self.vc_ssl_thumbprint
        )
        with pytest.raises(FileNotFoundError):
            esx_cli_client.run_esx_cli_cmd("hostname", "cmd")
