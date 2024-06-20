from mock import patch

from config_modules_vmware.controllers.vcenter.task_and_event_retention_policy import DESIRED_EVENT_MAX_AGE_KEY
from config_modules_vmware.controllers.vcenter.task_and_event_retention_policy import DESIRED_TASK_CLEANUP_ENABLED_KEY
from config_modules_vmware.controllers.vcenter.task_and_event_retention_policy import TaskAndEventRetentionPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestTaskAndEventRetentionPolicy:
    def setup_method(self):
        self.controller = TaskAndEventRetentionPolicy()
        self.compliant_value = {
            "task_cleanup_enabled": True,
            "task_max_age": 30,
            "event_cleanup_enabled": True,
            "event_max_age": 30,
        }

        self.non_compliant_value = {
            "task_cleanup_enabled": True,
            "task_max_age": 20,
            "event_cleanup_enabled": True,
            "event_max_age": 20,
        }

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = [True, 30, True, 30]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_value
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get task and event retention policy")

        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.set_vpxd_option_value.side_effect = [True, True, True, True]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failed_due_to_exception(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to set VPX Option value")

        mock_vc_vmomi_client.set_vpxd_option_value.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failed_due_to_failed_update(self, mock_vc_vmomi_client, mock_vc_context):
        # Case where update of one of the values fails
        mock_vc_vmomi_client.set_vpxd_option_value.side_effect = [True, True, True, False]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.FAILED
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = [True, 30, True, 30]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: {
                "task_max_age": 20,
                "event_max_age": 20,
            },
            consts.DESIRED: {
                "task_max_age": 30,
                "event_max_age": 30,
            },
        }
        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = [
            self.non_compliant_value[DESIRED_TASK_CLEANUP_ENABLED_KEY],
            self.non_compliant_value[DESIRED_EVENT_MAX_AGE_KEY],
            self.non_compliant_value[DESIRED_TASK_CLEANUP_ENABLED_KEY],
            self.non_compliant_value[DESIRED_EVENT_MAX_AGE_KEY],
        ]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_errors = [str(expected_error)]
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: expected_errors}

        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success_already_desired(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = [
            self.compliant_value[DESIRED_TASK_CLEANUP_ENABLED_KEY],
            self.compliant_value[DESIRED_EVENT_MAX_AGE_KEY],
            self.compliant_value[DESIRED_TASK_CLEANUP_ENABLED_KEY],
            self.compliant_value[DESIRED_EVENT_MAX_AGE_KEY],
        ]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: {
                "task_max_age": 20,
                "event_max_age": 20,
            },
            consts.NEW: {
                "task_max_age": 30,
                "event_max_age": 30,
            },
        }

        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = [
            self.non_compliant_value[DESIRED_TASK_CLEANUP_ENABLED_KEY],
            self.non_compliant_value[DESIRED_EVENT_MAX_AGE_KEY],
            self.non_compliant_value[DESIRED_TASK_CLEANUP_ENABLED_KEY],
            self.non_compliant_value[DESIRED_EVENT_MAX_AGE_KEY],
        ]

        mock_vc_vmomi_client.set_vpxd_option_value.side_effect = [True, True, True, True]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Get exception while remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_vpxd_option_value.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Exception while set during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.set_vpxd_option_value.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
