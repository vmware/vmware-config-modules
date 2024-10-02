# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.esxi.ssh_compression_policy import SshCompressionPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.tests.controllers.esxi.test_ssh_host_based_auth_policy import HelperTestSshConfigControls


class TestSshCompressionPolicy:
    def setup_method(self):
        self.controller = SshCompressionPolicy()
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
    def test_set_skipped_8_0(self, mock_set_ssh_config_value):
        self.context.product_version = "8.0.3"
        status, errors = self.controller.set(self.context, "yes")
        mock_set_ssh_config_value.assert_not_called()
        assert status == RemediateStatus.SKIPPED
        assert errors == [consts.REMEDIATION_SKIPPED_MESSAGE]

    @patch('config_modules_vmware.controllers.esxi.utils.esxi_ssh_config_utils.set_ssh_config_value')
    def test_set_skipped_7_0(self, mock_set_ssh_config_value):
        self.context.product_version = "7.0.3"
        status, errors = self.controller.set(self.context, "yes")
        mock_set_ssh_config_value.assert_not_called()
        assert status == RemediateStatus.SKIPPED
        assert errors == [consts.CONTROL_NOT_AUTOMATED]

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
