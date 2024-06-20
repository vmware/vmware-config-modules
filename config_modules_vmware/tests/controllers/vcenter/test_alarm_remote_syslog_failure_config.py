from mock import MagicMock
from mock import patch
from pyVmomi import vim

from config_modules_vmware.controllers.vcenter.alarm_remote_syslog_failure_config import AlarmRemoteSyslogFailureConfig
from config_modules_vmware.controllers.vcenter.alarm_remote_syslog_failure_config import ESX_REMOTE_SYSLOG_FAILURE_EVENT
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestAlarmRemoteSyslogFailureConfig:

    mock_alarm_def = MagicMock()

    def setup_method(self):
        self.controller = AlarmRemoteSyslogFailureConfig()
        self.mock_alarm_def.info.name = "Mocked Alarm"
        self.mock_alarm_def.info.description = "Mocked Alarm Description"
        self.mock_alarm_def.info.enabled = True
        self.mock_alarm_def.info.actionFrequency = 60

        mock_expression = MagicMock()
        mock_expression.status = "red"
        mock_expression.eventTypeId = ESX_REMOTE_SYSLOG_FAILURE_EVENT
        mock_expression.objectTypeId = "vim.Folder"
        mock_expression.__class__ = vim.alarm.EventAlarmExpression

        mock_comparison = MagicMock()
        mock_comparison.attributeName = 'Mocked Attribute'
        mock_comparison.operator = 'endsWith'
        mock_comparison.value = 'A'
        mock_expression.comparisons = [mock_comparison]
        self.mock_alarm_def.info.expression.expression = [mock_expression]

        mock_email_action = MagicMock()
        mock_email_action.transitionSpecs[0].repeats = True
        mock_email_action.transitionSpecs[0].startState = "red"
        mock_email_action.transitionSpecs[0].finalState = "yellow"
        mock_email_action.transitionSpecs[1].repeats = True
        mock_email_action.transitionSpecs[1].startState = "green"
        mock_email_action.transitionSpecs[1].finalState = "yellow"
        mock_email_action.action = MagicMock()
        mock_email_action.action.__class__ = vim.action.SendEmailAction
        mock_email_action.action.subject = "Mocked Subject"
        mock_email_action.action.toList = "Mocked To List"
        mock_email_action.action.ccList = "Mocked CC List"
        mock_email_action.action.body = "Mocked Body"

        mock_snmp_action = MagicMock()
        mock_snmp_action.action.__class__ = vim.action.SendSNMPAction
        mock_snmp_action.transitionSpecs[0].repeats = False
        mock_snmp_action.transitionSpecs[0].startState = "yellow"
        mock_snmp_action.transitionSpecs[0].finalState = "red"

        mock_script_action = MagicMock()
        mock_script_action.action.__class__ = vim.action.RunScriptAction
        mock_script_action.transitionSpecs[0].repeats = False
        mock_script_action.transitionSpecs[0].startState = "yellow"
        mock_script_action.transitionSpecs[0].finalState = "green"
        mock_script_action.action.script = "Mocked Script"

        self.mock_alarm_def.info.action.action = [mock_email_action, mock_snmp_action, mock_script_action]

        self.mock_vc_context = MagicMock()

        self.mock_alarm_manager = MagicMock()

        self.mock_alarm_manager.GetAlarm.return_value = [self.mock_alarm_def]

        self.mock_vc_context.vc_vmomi_client().content.alarmManager = self.mock_alarm_manager

        self.expected_alarms = [{
            'alarm_name': 'Mocked Alarm',
            'alarm_description': 'Mocked Alarm Description',
            'enabled': True,
            'target_type': 'VCENTER',
            'rule_expressions': [
                {'state': 'CRITICAL',
                 'event_type_id': ESX_REMOTE_SYSLOG_FAILURE_EVENT,
                 'comparisons': [
                     {'attribute': 'Mocked Attribute',
                      'operator': 'endsWith',
                      'value': 'A'
                      }
                 ]
                 }
            ],
            'action_frequency': 60,
            'alarm_actions': [
                {
                    'state': 'WARNING',
                    'repeats': True,
                    'action_type': 'EMAIL',
                    'email': {
                        'subject': 'Mocked Subject',
                        'to_list': 'Mocked To List',
                        'cc_list': 'Mocked CC List',
                        'body': 'Mocked Body'
                    }
                },
                {
                    'state': 'CRITICAL',
                    'repeats': False,
                    'action_type': 'SNMP'
                },
                {
                    'state': 'NORMAL',
                    'repeats': False,
                    'action_type': 'SCRIPT',
                    'script_name': 'Mocked Script'}
            ]
        }]

    @patch("config_modules_vmware.controllers.vcenter.utils.vc_alarms_utils.get_target_type")
    def test_get_success(self, mock_get_target_type):
        mock_get_target_type.return_value = 'VCENTER'
        result, errors = self.controller.get(self.mock_vc_context)
        assert len(result) == 1
        assert result == self.expected_alarms

    def test_get_failed(self):
        self.mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")
        result, errors = self.controller.get(self.mock_vc_context)
        assert result == []
        assert errors == ["Test exception"]

    def test_set_success(self):
        status, errors = self.controller.set(self.mock_vc_context, self.expected_alarms)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed_exception(self):
        self.mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")
        status, errors = self.controller.set(self.mock_vc_context, self.expected_alarms)
        assert status == RemediateStatus.FAILED
        assert errors == ["Error during Mocked Alarm creation with error Test exception."]

    def test_set_failed_exception_duplicate_name(self):
        mock_vc_context = MagicMock()
        mock_content = mock_vc_context.vc_vmomi_client().content
        mock_alarm_manager = mock_content.alarmManager
        mock_alarm_manager.CreateAlarm.side_effect = vim.fault.DuplicateName
        status, errors = self.controller.set(mock_vc_context, self.expected_alarms)
        assert status == RemediateStatus.FAILED
        assert errors == ["An alarm with same name 'Mocked Alarm' already exists.",
                          'Manual remediation required for an update or deletion.',
                          'Please either update/delete that alarm manually or choose different alarm name.']

    @patch("config_modules_vmware.controllers.vcenter.utils.vc_alarms_utils.get_target_type")
    def test_check_compliance_compliant(self, mock_get_target_type):
        mock_get_target_type.return_value = 'VCENTER'
        result = self.controller.check_compliance(self.mock_vc_context, self.expected_alarms)
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.utils.vc_alarms_utils.get_target_type")
    def test_check_compliance_non_compliant(self, mock_get_target_type):
        mock_get_target_type.return_value = 'VCENTER'
        non_complaint_alarms = self.expected_alarms
        non_complaint_alarms[0]['enabled'] = False
        result = self.controller.check_compliance(self.mock_vc_context, self.expected_alarms)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: [{'enabled': True, 'alarm_name': 'Mocked Alarm'}],
            consts.DESIRED: [{'enabled': False, 'alarm_name': 'Mocked Alarm'}]
        }
        assert result == expected_result

    def test_check_compliance_failed(self):
        self.mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")
        result = self.controller.check_compliance(self.mock_vc_context, self.expected_alarms)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ["Test exception"]
        }
        assert result == expected_result
