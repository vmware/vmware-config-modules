# Copyright 2024 Broadcom. All Rights Reserved.
import mock
from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.esxi.ssh_port_forwarding_policy import SshPortForwardingPolicy
from config_modules_vmware.tests.controllers.esxi.test_ssh_host_based_auth_policy import HelperTestSshConfigControls


class TestSshPortForwardingPolicy:
    def setup_method(self):
        self.controller = SshPortForwardingPolicy()
        self.context = MagicMock()

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_true(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_get_true(self.controller, self.context, mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_false(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_get_false(self.controller, self.context, mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_empty(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_get_empty(self.controller, self.context, mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_failed(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_get_failed(self.controller, self.context, mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_get_skipped(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_get_skipped(self.controller, self.context, mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.set_ssh_config_value')
    def test_set_success(self, mock_set_ssh_config_value):
        HelperTestSshConfigControls.helper_test_set_success(self.controller, self.context, mock_set_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.set_ssh_config_value')
    def test_set_failed(self, mock_set_ssh_config_value):
        HelperTestSshConfigControls.helper_test_set_failed(self.controller, self.context, mock_set_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.set_ssh_config_value')
    def test_set_skipped(self, mock_set_ssh_config_value):
        HelperTestSshConfigControls.helper_test_set_skipped(self.controller, self.context, mock_set_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_check_compliance_non_compliant(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_check_compliance_non_compliant(self.controller, self.context,
                                                                               mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_check_compliance_compliant(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_check_compliance_compliant(self.controller, self.context,
                                                                           mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_check_compliance_failed(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_check_compliance_failed(self.controller, self.context,
                                                                        mock_get_ssh_config_value)

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.get_ssh_config_value')
    def test_check_compliance_skipped(self, mock_get_ssh_config_value):
        HelperTestSshConfigControls.helper_test_check_compliance_skipped(self.controller, self.context,
                                                                         mock_get_ssh_config_value)
