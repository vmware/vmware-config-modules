# Copyright 2024 Broadcom. All Rights Reserved.
import mock
from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.esxi.ssh_host_based_auth_policy import SshHostBasedAuthPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class HelperTestSshConfigControls:
    @staticmethod
    def get_default_failed_value(desired_configs):
        if isinstance(desired_configs, bool):
            return False
        elif isinstance(desired_configs, int):
            return -1
        elif isinstance(desired_configs, str):
            return ""
        elif isinstance(desired_configs, list):
            return []
        else:
            return None

    @staticmethod
    def helper_test_get_true(controller, context, mock_get_ssh_config_value):
        context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = "yes"
        result, errors = controller.get(context)
        assert result == "yes"
        assert errors == []

    @staticmethod
    def helper_test_get_false(controller, context, mock_get_ssh_config_value):
        context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = "no"
        result, errors = controller.get(context)
        assert result == "no"
        assert errors == []

    @staticmethod
    def helper_test_get_empty(controller, context, mock_get_ssh_config_value):
        context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = ""
        result, errors = controller.get(context)
        assert result == ""
        assert errors == []

    @staticmethod
    def helper_test_get_failed(controller, context, mock_get_ssh_config_value):
        context.product_version = "8.0.1"
        mock_get_ssh_config_value.side_effect = Exception("Test exception")
        result, errors = controller.get(context)
        assert result == ""
        assert errors == ["Test exception"]

    @staticmethod
    def helper_test_get_skipped(controller, context, mock_get_ssh_config_value):
        context.product_version = "7.0.3"
        mock_get_ssh_config_value.return_value = ""
        result, errors = controller.get(context)
        assert result == ""
        assert errors == [consts.SKIPPED]

    @staticmethod
    def helper_test_set_success(controller, context, mock_set_ssh_config_value):
        context.product_version = "8.0.1"
        status, errors = controller.set(context, "yes")
        mock_set_ssh_config_value.assert_called_once_with(context, mock.ANY, "yes")
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    @staticmethod
    def helper_test_set_failed(controller, context, mock_set_ssh_config_value):
        context.product_version = "8.0.1"
        mock_set_ssh_config_value.side_effect = Exception("Test exception")
        status, errors = controller.set(context, "yes")
        assert status == RemediateStatus.FAILED
        assert errors == ["Test exception"]

    @staticmethod
    def helper_test_set_skipped(controller, context, mock_set_ssh_config_value):
        context.product_version = "7.0.3"
        status, errors = controller.set(context, "yes")
        mock_set_ssh_config_value.assert_not_called()
        assert status == RemediateStatus.SKIPPED
        assert errors == []

    @staticmethod
    def helper_test_check_compliance_non_compliant(controller, context, mock_get_ssh_config_value):
        context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = "yes"
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: "yes",
            consts.DESIRED: "no"
        }
        result = controller.check_compliance(context, "no")
        assert expected_result == result

    @staticmethod
    def helper_test_check_compliance_compliant(controller, context, mock_get_ssh_config_value):
        context.product_version = "8.0.1"
        mock_get_ssh_config_value.return_value = "no"
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        result = controller.check_compliance(context, "no")
        assert expected_result == result

    @staticmethod
    def helper_test_check_compliance_failed(controller, context, mock_get_ssh_config_value):
        context.product_version = "8.0.1"
        mock_get_ssh_config_value.side_effect = Exception("Test exception")
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ["Test exception"]
        }
        result = controller.check_compliance(context, "no")
        assert expected_result == result

    @staticmethod
    def helper_test_check_compliance_skipped(controller, context, mock_get_ssh_config_value):
        context.product_version = "7.0.3"
        mock_get_ssh_config_value.return_value = ""
        expected_result = {
            consts.STATUS: ComplianceStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_NOT_AUTOMATED]
        }
        result = controller.check_compliance(context, "no")
        assert expected_result == result


class TestSshHostBasedAuthPolicy:
    def setup_method(self):
        self.controller = SshHostBasedAuthPolicy()
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
