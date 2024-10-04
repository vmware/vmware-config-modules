from mock import patch

from config_modules_vmware.controllers.vcenter.backup_schedule_config import BackupScheduleConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestBackupScheduleConfig:
    def setup_method(self):
        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = vc_consts.VC_API_BASE.format(self.mock_vc_host_name)

        # Initialize control
        self.controller = BackupScheduleConfig()

        self.rest_api_get_compliant_daily_schedule = {
            "DailyBackup": {"recurrence_info": {"hour": 1, "minute": 0}, "enable": True, "parts": ["seat", "common"],
                            "location": "sftp://10.0.0.250:/root/backups", "location_user": "root",
                            "retention_info": {"max_count": 5}}}

        self.rest_api_get_compliant_weekly_schedule = {
            "DailyBackup": {"recurrence_info": {"hour": 1, "minute": 0, "days": ["MONDAY"]},
                            "enable": True, "parts": ["seat", "common"],
                            "location": "sftp://10.0.0.250:/root/backups", "location_user": "root",
                            "retention_info": {"max_count": 5}}}
        self.rest_api_get_compliant_custom_schedule = {
            "DailyBackup": {"recurrence_info": {"hour": 1, "minute": 0, "days": ["MONDAY", "SUNDAY"]},
                            "enable": True, "parts": ["seat", "common"],
                            "location": "sftp://10.0.0.250:/root/backups", "location_user": "root",
                            "retention_info": {"max_count": 5}}}

        self.rest_api_get_non_compliant_value = {
            "DailyBackup": {"recurrence_info": {"hour": 1, "minute": 0}, "enable": False, "parts": ["seat", "common"],
                            "location": "sftp://10.0.0.250:/root/backups", "location_user": "root",
                            "retention_info": {"max_count": 5}}}

        self.desired_values_daily_schedule = {"backup_location_url": "sftp://10.0.0.250:/root/backups",
                                              "backup_parts": ["seat", "common"], "backup_schedule_name": "DailyBackup",
                                              "backup_server_username": "root",
                                              "backup_server_password": "HFKMo18wrwBh.k.H",
                                              "backup_encryption_password": "HFKMo18wrwBh.k.H",
                                              "enable_backup_schedule": True,
                                              "recurrence_info": {"hour": 1, "minute": 0, "recurrence_type": "DAILY"},
                                              "retention_info": {"max_count": 5}}

        self.desired_values_weekly_schedule = {"backup_location_url": "sftp://10.0.0.250:/root/backups",
                                               "backup_parts": ["seat", "common"],
                                               "backup_schedule_name": "DailyBackup",
                                               "backup_server_username": "root",
                                               "backup_server_password": "HFKMo18wrwBh.k.H",
                                               "backup_encryption_password": "HFKMo18wrwBh.k.H",
                                               "enable_backup_schedule": True,
                                               "recurrence_info": {"hour": 1, "minute": 0,
                                                                   "days": ["MONDAY"],
                                                                   "recurrence_type": "WEEKLY"},
                                               "retention_info": {"max_count": 5}}
        self.desired_values_custom_schedule = {"backup_location_url": "sftp://10.0.0.250:/root/backups",
                                               "backup_parts": ["seat", "common"],
                                               "backup_schedule_name": "DailyBackup",
                                               "backup_server_username": "root",
                                               "backup_server_password": "HFKMo18wrwBh.k.H",
                                               "backup_encryption_password": "HFKMo18wrwBh.k.H",
                                               "enable_backup_schedule": True,
                                               "recurrence_info": {"hour": 1, "minute": 0,
                                                                   "days": ["MONDAY", "SUNDAY"],
                                                                   "recurrence_type": "CUSTOM"},
                                               "retention_info": {"max_count": 5}}
        self.compliant_value_daily = {"backup_location_url": "sftp://10.0.0.250:/root/backups",
                                      "backup_parts": ["seat", "common"], "backup_schedule_name": "DailyBackup",
                                      "backup_server_username": "root", "enable_backup_schedule": True,
                                      "recurrence_info": {"hour": 1, "minute": 0, "recurrence_type": "DAILY"},
                                      "retention_info": {"max_count": 5}}
        self.compliant_value_weekly = {"backup_location_url": "sftp://10.0.0.250:/root/backups",
                                       "backup_parts": ["seat", "common"],
                                       "backup_schedule_name": "DailyBackup",
                                       "backup_server_username": "root",
                                       "enable_backup_schedule": True,
                                       "recurrence_info": {"hour": 1, "minute": 0,
                                                           "days": ["MONDAY"],
                                                           "recurrence_type": "WEEKLY"},
                                       "retention_info": {"max_count": 5}}
        self.compliant_value_custom = {"backup_location_url": "sftp://10.0.0.250:/root/backups",
                                       "backup_parts": ["seat", "common"],
                                       "backup_schedule_name": "DailyBackup",
                                       "backup_server_username": "root",
                                       "enable_backup_schedule": True,
                                       "recurrence_info": {"hour": 1, "minute": 0,
                                                           "days": ["MONDAY", "SUNDAY"],
                                                           "recurrence_type": "CUSTOM"},
                                       "retention_info": {"max_count": 5}}
        self.non_compliant_value = {"backup_location_url": "sftp://10.0.0.250:/root/backups",
                                    "backup_parts": ["seat", "common"], "backup_schedule_name": "DailyBackup",
                                    "backup_server_username": "root", "enable_backup_schedule": False,
                                    "recurrence_info": {"hour": 1, "minute": 0, "recurrence_type": "DAILY"},
                                    "retention_info": {"max_count": 5}}

        self.set_schedule_payload = {
            "schedule": "DailyBackup",
            "spec": {
                "backup_password": "HFKMo18wrwBh.k.H",
                "enable": True,
                "location": "sftp://10.0.0.250:/root/backups",
                "location_user": "root",
                "location_password": "HFKMo18wrwBh.k.H",
                "parts": [
                    "seat",
                    "common"
                ],
                "recurrence_info": {
                    "hour": 1,
                    "minute": 0
                },
                "retention_info": {
                    "max_count": 5
                }
            }
        }

        self.output_during_exception = {}

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success_daily_schedule(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_compliant_daily_schedule
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_value_daily
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success_weekly_schedule(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_compliant_weekly_schedule
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_value_weekly
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success_custom_schedule(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_compliant_custom_schedule
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_value_custom
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while fetching backup schedule config")

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.output_during_exception
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_success(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_non_compliant_value

        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.set(mock_vc_context, self.desired_values_daily_schedule)
        create_schedule_url = self.vc_base_url + vc_consts.BACKUP_SCHEDULE_URL
        mock_vc_rest_client.post_helper.assert_called_with(create_schedule_url,
                                                           body=self.set_schedule_payload)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Creating backup schedule failed")

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.post_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.set(mock_vc_context, self.desired_values_daily_schedule)

        mock_vc_rest_client.post_helper.assert_called_with(self.vc_base_url + vc_consts.BACKUP_SCHEDULE_URL,
                                                           body=self.set_schedule_payload)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_compliant(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_compliant_daily_schedule
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_values_daily_schedule)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_non_compliant(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: {'enable_backup_schedule': False},
            consts.DESIRED: {'enable_backup_schedule': True}
        }

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value_daily)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Compliance check failed while fetching backup schedule config")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_values_daily_schedule)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_skipped_already_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_compliant_daily_schedule
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.desired_values_daily_schedule)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_success_daily_schedule(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: {'enable_backup_schedule': False},
                           consts.NEW: {'enable_backup_schedule': True}}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.rest_api_get_non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.desired_values_daily_schedule)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while getting backup schedule during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value_daily)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Remediation failed while creating backup schedule")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = {}
        mock_vc_rest_client.post_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value_daily)

        assert result == expected_result
