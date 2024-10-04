from mock import patch

from config_modules_vmware.controllers.sddc_manager.backup import BackupConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import SDDC_MANAGER_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestBackupConfig:
    def setup_method(self):
        # SDDC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.sddc_base_url = SDDC_MANAGER_API_BASE.format(self.mock_vc_host_name)

        # Initialize control
        self.controller = BackupConfig()
        self.desired_value = {
                "encryption" : {
                    "passphrase" : "passphrase"
                },
                "backup_locations" : [ {
                    "server" : "10.0.0.250",
                    "username" : "root",
                    "password" : "UACLdsmB5us4Z*a*",
                    "directory_path" : "/tmp"
                } ],
                "backup_schedules" : [ {
                    "resource_type" : "SDDC_MANAGER",
                    "take_scheduled_backups" : True,
                    "frequency" : "WEEKLY",
                    "days_of_week" : [ "SUNDAY", "THURSDAY", "FRIDAY" ],
                    "hour_of_day" : 12,
                    "minute_of_hour" : 34,
                    "take_backup_on_state_change" : False,
                    "retention_policy" : {
                        "number_of_most_recent_backups" : 15,
                        "number_of_days_of_hourly_backups" : 10,
                        "number_of_days_of_daily_backups" : 20
                    }
                } ]
            }
        self.get_value = {
                            'backup_locations': [{
                                'directory_path': '/tmp',
                                'port': 22,
                                'protocol': 'SFTP',
                                'server': '10.0.0.250',
                                'username': 'root'
                            }],
                            'backup_schedules': [{
                                'days_of_week': [
                                    'SUNDAY',
                                    'THURSDAY',
                                    'FRIDAY'
                                ],
                                'frequency': 'WEEKLY',
                                'hour_of_day': 12,
                                'minute_of_hour': 34,
                                'resource_type': 'SDDC_MANAGER',
                                'retention_policy': {
                                    'number_of_days_of_daily_backups': 20,
                                    'number_of_days_of_hourly_backups': 10,
                                    'number_of_most_recent_backups': 15
                                },
                                'take_backup_on_state_change': False,
                                'take_scheduled_backups': True
                            }]
        }
        self.get_non_compliant_value = {
                                            'backup_locations': [{
                                                'directory_path': '/tmp',
                                                'port': 22,
                                                'protocol': 'SFTP',
                                                'server': '10.0.0.251',
                                                'username': 'root'
                                            }],
                                            'backup_schedules': [{
                                                'days_of_week': [
                                                    'SUNDAY',
                                                    'THURSDAY',
                                                    'FRIDAY'
                                                ],
                                                'frequency': 'WEEKLY',
                                                'hour_of_day': 11,
                                                'minute_of_hour': 34,
                                                'resource_type': 'SDDC_MANAGER',
                                                'retention_policy': {
                                                    'number_of_days_of_daily_backups': 20,
                                                    'number_of_days_of_hourly_backups': 10,
                                                    'number_of_most_recent_backups': 15
                                                },
                                                'take_backup_on_state_change': False,
                                                'take_scheduled_backups': True
                                            }]
        }
        self.get_helper_values = {
                "encryption" : {
                    "passphrase" : "passphrase"
                },
                "backupLocations" : [ {
                    "server" : "10.0.0.250",
                    "username" : "root",
                    "port": 22,
                    "protocol": "SFTP",
                    "password" : "UACLdsmB5us4Z*a*",
                    "directoryPath" : "/tmp"
                } ],
                "backupSchedules" : [ {
                    "resourceType" : "SDDC_MANAGER",
                    "takeScheduledBackups" : True,
                    "frequency" : "WEEKLY",
                    "daysOfWeek" : [ "SUNDAY", "THURSDAY", "FRIDAY" ],
                    "hourOfDay" : 12,
                    "minuteOfHour" : 34,
                    "takeBackupOnStateChange" : False,
                    "retentionPolicy" : {
                        "numberOfMostRecentBackups" : 15,
                        "numberOfDaysOfHourlyBackups" : 10,
                        "numberOfDaysOfDailyBackups" : 20
                    }
                } ]
            }
        self.get_helper_non_compliant_values = {
                "encryption" : {
                    "passphrase" : "passphrase"
                },
                "backupLocations" : [ {
                    "server" : "10.0.0.251",
                    "username" : "root",
                    "port": 22,
                    "protocol": "SFTP",
                    "password" : "UACLdsmB5us4Z*a*",
                    "directoryPath" : "/tmp"
                } ],
                "backupSchedules" : [ {
                    "resourceType" : "SDDC_MANAGER",
                    "takeScheduledBackups" : True,
                    "frequency" : "WEEKLY",
                    "daysOfWeek" : [ "SUNDAY", "THURSDAY", "FRIDAY" ],
                    "hourOfDay" : 11,
                    "minuteOfHour" : 34,
                    "takeBackupOnStateChange" : False,
                    "retentionPolicy" : {
                        "numberOfMostRecentBackups" : 15,
                        "numberOfDaysOfHourlyBackups" : 10,
                        "numberOfDaysOfDailyBackups" : 20
                    }
                } ]
            }
        self.put_helper_values = {
                "encryption" : {
                    "passphrase" : "passphrase"
                },
                "backupLocations" : [ {
                    "server" : "10.0.0.250",
                    "port" : 22,
                    "protocol" : "SFTP",
                    "username" : "root",
                    "password" : "UACLdsmB5us4Z*a*",
                    "directoryPath" : "/tmp",
                    "sshFingerprint": "SHA256:yA3FHIQMbiMnansI4+lONYBASLP2IQhGZkGJIMZ2Pi8"
                } ],
                "backupSchedules" : [ {
                    "resourceType" : "SDDC_MANAGER",
                    "takeScheduledBackups" : True,
                    "frequency" : "WEEKLY",
                    "daysOfWeek" : [ "SUNDAY", "THURSDAY", "FRIDAY" ],
                    "hourOfDay" : 12,
                    "minuteOfHour" : 34,
                    "takeBackupOnStateChange" : False,
                    "retentionPolicy" : {
                        "numberOfMostRecentBackups" : 15,
                        "numberOfDaysOfHourlyBackups" : 10,
                        "numberOfDaysOfDailyBackups" : 20
                    }
                } ]
            }
        self.non_compliant_value = {
                "encryption" : {
                    "passphrase" : "passphrase"
                },
                "backup_locations" : [ {
                    "server" : "10.0.0.250",
                    "username" : "root",
                    "password" : "UACLdsmB5us4Z*a*",
                    "directory_path" : "/tmp"
                } ],
                "backup_schedules" : [ {
                    "resource_type" : "SDDC_MANAGER",
                    "take_scheduled_backups" : True,
                    "frequency" : "WEEKLY",
                    "days_of_week" : [ "SUNDAY", "THURSDAY", "FRIDAY" ],
                    "hour_of_day" : 11,
                    "minute_of_hour" : 34,
                    "take_backup_on_state_change" : False,
                    "retention_policy" : {
                        "number_of_most_recent_backups" : 15,
                        "number_of_days_of_hourly_backups" : 10,
                        "number_of_days_of_daily_backups" : 20
                    }
                } ]
            }
        self.task_info = {
                            "id": "a9e56aa9-5cec-433e-8790-1860f8a89532",
                            "name": "Configure Backup of VCF Components (SDDC Manager and NSX Managers)",
                            "status": "IN_PROGRESS",
                            "creationTimestamp": "2024-02-19T15:29:36.702Z"
                        }
        self.output_during_exception = {}

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.get_value
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while fetching Backup config")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.output_during_exception
        assert errors == ["Error retrieving backup settings: "+ str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.framework.utils.utils.run_shell_cmd')
    def test_set_success(self, mock_run_shell_cmd, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = True
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_run_shell_cmd.side_effect = [(
                                          "# 10.0.0.250:22 SSH-2.0-OpenSSH_8.1 10.0.0.250 ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDl/s2ZAC/kZIWlE+dsP0aPhzmdVxj+sezcugOzD5gUKQ53xRPZxZzFUx8hNhpNw+8GWy8m9e3wremnz4vto1/9Jx7IoPlhg7BFi07KKEiqn5yFkI86L1IJUHF6fvzp53wkU5hOGLCgQ9J4RC4yuclE++ukr4UlGOQAOpYx6lpbtY1tIjvZ9EEZeGuVilGFiKyVjn1A9XiP6A2D/BMM9s5joCmE7uEMYQhPMD2b9SpzBWd4smVI6yhYPVlbhWRPxwQluzFj3wtZHc94LCBOJptcBiBcm/nD5fE+MvM6f5aAlAhCZBEjXaw9dtfP94622KPVekrvfGjsg7Yht/lPOiApW11XMSt33/EV2mppy6A/lImT1T6LKhPGyq1jzGStWEPSMrwydgfhVMcMvsjmN/d6+msOVDjkyvGITXD878z3xe7dVyK67eQpixsKED9XwQyiuuDqqaoS1wXO8Z9Tq0rVypszurrpiE6mf2XjfzHKTiUJUwu58WZkDTZykvHyu9k=",
                                          "", ""),
                                          ("3072 SHA256:yA3FHIQMbiMnansI4+lONYBASLP2IQhGZkGJIMZ2Pi8 10.0.0.250 (RSA)",
                                           "", ""), ]
        result, errors = self.controller.set(mock_sddc_manager_context, self.desired_value)
        mock_sddc_manager_rest_client.put_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.BACKUP_URL,
                                                                    body=self.put_helper_values)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.controllers.sddc_manager.backup.BackupConfig'
           '._BackupConfig__gen_ssh_fingerprint')
    def test_set_failed(self, gen_ssh_fingerprint_mock, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Setting Backup config failed")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.put_helper.side_effect = expected_error
        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = False
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        gen_ssh_fingerprint_mock.return_value = "SHA256:yA3FHIQMbiMnansI4+lONYBASLP2IQhGZkGJIMZ2Pi8"

        result, errors = self.controller.set(mock_sddc_manager_context, self.desired_value)

        mock_sddc_manager_rest_client.put_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.BACKUP_URL,
                                                                    body=self.put_helper_values)

        assert result == RemediateStatus.FAILED
        assert errors == ["Check for valid backup location and backup schedule and retry!!:" +str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.controllers.sddc_manager.backup.BackupConfig.get')
    def test_check_compliance_compliant(self, get_mock, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        get_mock.return_value = self.get_value, []

        result = self.controller.check_compliance(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.controllers.sddc_manager.backup.BackupConfig.get')
    def test_check_compliance_non_compliant(self, get_mock, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.get_non_compliant_value,
            consts.DESIRED: self.get_value
        }

        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        get_mock.return_value = self.get_non_compliant_value, []

        result = self.controller.check_compliance(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Compliance check failed while fetching Backup config")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: ["Error retrieving backup settings: " + str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_skipped_already_desired(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.controllers.sddc_manager.backup.BackupConfig'
           '._BackupConfig__gen_ssh_fingerprint')
    def test_remediate_success(self, gen_ssh_fingerprint_mock, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.get_non_compliant_value,
                           consts.NEW: self.get_value}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        gen_ssh_fingerprint_mock.return_value = "SHA256:yA3FHIQMbiMnansI4+lONYBASLP2IQhGZkGJIMZ2Pi8"

        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while getting Backup config during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: ["Error retrieving backup settings: " + str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.controllers.sddc_manager.backup.BackupConfig'
           '._BackupConfig__gen_ssh_fingerprint')
    def test_remediate_set_failed(self, gen_ssh_fingerprint_mock, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Remediation failed while setting Backup config")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: ["Check for valid backup location and backup schedule and retry!!:" + str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_rest_client.put_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        gen_ssh_fingerprint_mock.return_value = "SHA256:yA3FHIQMbiMnansI4+lONYBASLP2IQhGZkGJIMZ2Pi8"

        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.controllers.sddc_manager.backup.BackupConfig'
           '._BackupConfig__gen_ssh_fingerprint')
    def test_task_status_failure(self, gen_ssh_fingerprint_mock, mock_sddc_manager_rest_client,
                                 mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Set up expected values
        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = False
        gen_ssh_fingerprint_mock.return_value = "SHA256:yA3FHIQMbiMnansI4+lONYBASLP2IQhGZkGJIMZ2Pi8"

        status, errors = self.controller.set(mock_sddc_manager_context, self.desired_value)

        # Assertions
        assert status == RemediateStatus.FAILED
        assert errors
