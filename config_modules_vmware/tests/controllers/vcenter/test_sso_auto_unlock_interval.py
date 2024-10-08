from mock import patch

from config_modules_vmware.controllers.vcenter.sso_auto_unlock_interval import SSOAutoUnlockInterval
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSSOAutoUnlockInterval:
    def setup_method(self):
        self.controller = SSOAutoUnlockInterval()
        self.compliant_value = 300
        self.non_compliant_value = 100
        self.error_condition = -100

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_get_success(self, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_vmomi_sso_client.get_auto_unlock_interval.return_value = self.compliant_value
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_value
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_get_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Failed to get Auto unlock interval")

        mock_vc_vmomi_sso_client.get_auto_unlock_interval.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == -1
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_set_success(self, mock_vc_vmomi_sso_client, mock_vc_context):
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_set_failed_due_to_exception(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Failed to set auto unlock interval config")

        mock_vc_vmomi_sso_client.set_auto_unlock_interval.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_set_failed_due_to_negative_value(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("value must be a positive integer")

        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result, errors = self.controller.set(mock_vc_context, self.error_condition)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vmomi_sso_client.get_auto_unlock_interval.return_value = self.compliant_value
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value,
        }
        mock_vc_vmomi_sso_client.get_auto_unlock_interval.return_value = self.non_compliant_value
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_sso_client.get_auto_unlock_interval.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_remediate_skipped_already_desired(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_vc_vmomi_sso_client.get_auto_unlock_interval.return_value = self.compliant_value
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_remediate_success(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_value,
            consts.NEW: self.compliant_value,
        }

        mock_vc_vmomi_sso_client.get_auto_unlock_interval.return_value = self.non_compliant_value
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_remediate_get_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Get exception while remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_sso_client.get_auto_unlock_interval.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient")
    def test_remediate_set_failed(self, mock_vc_vmomi_sso_client, mock_vc_context):
        expected_error = Exception("Exception while set during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_sso_client.get_auto_unlock_interval.return_value = self.non_compliant_value
        mock_vc_vmomi_sso_client.set_auto_unlock_interval.side_effect = expected_error
        mock_vc_context.vc_vmomi_sso_client.return_value = mock_vc_vmomi_sso_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
