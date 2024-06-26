# Copyright 2024 Broadcom. All Rights Reserved.
import mock
from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.esxi.ssh_ignore_rhosts_policy import SshIgnoreRHostsPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSshIgnoreRHostsPolicy:
    def setup_method(self):
        self.controller = SshIgnoreRHostsPolicy()
        self.context = MagicMock()

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_true(self, mock_get_ssh_config_value):
        self.context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = "yes"
        result, errors = self.controller.get(self.context)
        assert result == "yes"
        assert errors == []

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_false(self, mock_get_ssh_config_value):
        self.context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = "no"
        result, errors = self.controller.get(self.context)
        assert result == "no"
        assert errors == []

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_empty(self, mock_get_ssh_config_value):
        self.context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = ""
        result, errors = self.controller.get(self.context)
        assert result == ""
        assert errors == []

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_failed(self, mock_get_ssh_config_value):
        self.context.product_version = "8.0.1"
        mock_get_ssh_config_value.side_effect = Exception("Test exception")
        result, errors = self.controller.get(self.context)
        assert result == ""
        assert errors == ["Test exception"]

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_skipped(self, mock_get_ssh_config_value):
        self.context.product_version = "7.0.3"
        mock_get_ssh_config_value.return_value = ""
        result, errors = self.controller.get(self.context)
        assert result == ""
        assert errors == [consts.SKIPPED]

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.set_ssh_config_value')
    def test_set_success(self, mock_set_ssh_config_value):
        self.context.product_version = "8.0.1"
        status, errors = self.controller.set(self.context, "yes")
        mock_set_ssh_config_value.assert_called_once_with(self.context, mock.ANY, "yes")
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.set_ssh_config_value')
    def test_set_failed(self, mock_set_ssh_config_value):
        self.context.product_version = "8.0.1"
        mock_set_ssh_config_value.side_effect = Exception("Test exception")
        status, errors = self.controller.set(self.context, "yes")
        assert status == RemediateStatus.FAILED
        assert errors == ["Test exception"]

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.set_ssh_config_value')
    def test_set_skipped(self, mock_set_ssh_config_value):
        self.context.product_version = "7.0.3"
        status, errors = self.controller.set(self.context, "yes")
        mock_set_ssh_config_value.assert_not_called()
        assert status == RemediateStatus.SKIPPED
        assert errors == []
