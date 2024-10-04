# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.log_location_config import IS_PERSISTENT
from config_modules_vmware.controllers.esxi.log_location_config import LOG_LOCATION
from config_modules_vmware.controllers.esxi.log_location_config import LogLocationConfig
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestLogLocationConfig:
    def setup_method(self):
        self.controller = LogLocationConfig()
        self.compliant_value = {IS_PERSISTENT: True, LOG_LOCATION: "/scratch/logs"}
        self.non_compliant_value = {IS_PERSISTENT: False, LOG_LOCATION: "/tmp/logs"}
        self.invalid_value = {IS_PERSISTENT: True, LOG_LOCATION: "/invalid"}
        self.cli_return_compliant_value = "   Allow Vsan Backing: false\n" \
                                          "   Local Log Output: /scratch/logs\n" \
                                          "   Local Log Output Is Persistent: true\n" \
                                          "   Log Level: error"
        self.cli_return_non_compliant_value = "   Allow Vsan Backing: false\n" \
                                              "   Local Log Output: /tmp/logs\n" \
                                              "   Local Log Output Is Persistent: false\n" \
                                              "   Log Level: error"
        mock_host_ref = MagicMock()
        mock_host_ref.name = 'host-1'
        self.esx_cli_client = MagicMock()
        self.mock_host_context = HostContext(host_ref=mock_host_ref, esx_cli_client_func=self.esx_cli_client)

    def test_get_success(self):
        self.esx_cli_client().run_esx_cli_cmd.return_value = (self.cli_return_compliant_value, "", 0)
        result, errors = self.controller.get(self.mock_host_context)
        assert result == self.compliant_value
        assert errors == []

    def test_get_failed(self):
        expected_error = "Test exception"
        self.esx_cli_client().run_esx_cli_cmd.side_effect = Exception(expected_error)
        result, errors = self.controller.get(self.mock_host_context)
        assert result == {}
        assert errors == [expected_error]

    def test_get_failed_cli_not_returning_log_location(self):
        cli_return_value = "   Allow Vsan Backing: false\n" \
                           "   Local Log Output Is Persistent: true\n" \
                           "   Log Level: error"
        expected_error = "Unable to fetch log location using command esxcli system syslog config get"
        self.esx_cli_client().run_esx_cli_cmd.return_value = (cli_return_value, "", 0)
        result, errors = self.controller.get(self.mock_host_context)
        assert result == {}
        assert errors == [expected_error]

    def test_get_failed_cli_not_returning_log_persistent_flag(self):
        cli_return_value = "   Allow Vsan Backing: false\n" \
                           "   Local Log Output: /scratch/logs\n" \
                           "   Log Level: error"
        expected_error = "Unable to fetch persistent flag using command esxcli system syslog config get"
        self.esx_cli_client().run_esx_cli_cmd.return_value = (cli_return_value, "", 0)
        result, errors = self.controller.get(self.mock_host_context)
        assert result == {}
        assert errors == [expected_error]

    def test_get_failed_cli_execution_failed(self):
        expected_error = f"Command esxcli system syslog config get failed. Dummy_out Dummy_err"
        self.esx_cli_client().run_esx_cli_cmd.side_effect = [(self.cli_return_non_compliant_value, "", 0),
                                                             ("Dummy_out", "Dummy_err", 1)]
        result, errors = self.controller.get(self.mock_host_context)
        assert errors == [expected_error]
        assert result == {}

    def test_set_success(self):
        self.cli_return_not_persistent_value = "   Allow Vsan Backing: false\n" \
                                               "   Local Log Output: /scratch/logs\n" \
                                               "   Local Log Output Is Persistent: false\n" \
                                               "   Log Level: error"
        self.esx_cli_client().run_esx_cli_cmd.side_effect = [(self.cli_return_non_compliant_value, "", 0),
                                                             ("", "", 0),
                                                             (self.cli_return_compliant_value, "", 0)]
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        out = "Failed to create directory /invalid: Operation not permitted."
        expected_error = f"Command esxcli system syslog config set --logdir=/invalid failed. {out} Dummy_err"
        self.esx_cli_client().run_esx_cli_cmd.side_effect = [(self.cli_return_non_compliant_value, "", 0),
                                                             (out, "Dummy_err", 1)]
        status, errors = self.controller.set(self.mock_host_context, self.invalid_value)
        assert errors == [expected_error]
        assert status == RemediateStatus.FAILED

    def test_set_failed_conflict_desired_values(self):
        conflict_desired_value = {IS_PERSISTENT: True, LOG_LOCATION: "/tmp/logs"}
        cli_return_conflict_desired_values = "   Allow Vsan Backing: false\n" \
                                             "   Local Log Output: /tmp/logs\n" \
                                             "   Local Log Output Is Persistent: false\n" \
                                             "   Log Level: error"
        expected_errors = ["'log_location: /tmp/logs' is not matching the desired criteria 'is_persistent: True'"]
        self.esx_cli_client().run_esx_cli_cmd.side_effect = [(cli_return_conflict_desired_values, "", 0),
                                                             ("", "", 0),
                                                             (cli_return_conflict_desired_values, "", 0),
                                                             ("", "", 0)]
        status, errors = self.controller.set(self.mock_host_context, conflict_desired_value)
        assert errors == expected_errors
        assert status == RemediateStatus.FAILED

    def test_check_compliance_compliant(self):
        self.esx_cli_client().run_esx_cli_cmd.return_value = (self.cli_return_compliant_value, "", 0)
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value)
        assert result == expected_result

    def test_check_compliance_non_compliant(self):
        self.esx_cli_client().run_esx_cli_cmd.return_value = (self.cli_return_non_compliant_value, "", 0)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value
        }
        result = self.controller.check_compliance(self.mock_host_context, self.compliant_value)
        assert result == expected_result

    def test_remediate(self):
        self.esx_cli_client().run_esx_cli_cmd.side_effect = [(self.cli_return_non_compliant_value, "", 0),
                                                             (self.cli_return_non_compliant_value, "", 0),
                                                             (self.cli_return_non_compliant_value, "", 0),
                                                             ("", "", 0),
                                                             (self.cli_return_compliant_value, "", 0)]
        result = self.controller.remediate(self.mock_host_context, self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_value,
            consts.NEW: self.compliant_value
        }
        assert result == expected_result

    def test_remediate_with_already_compliant(self):
        self.esx_cli_client().run_esx_cli_cmd.return_value = (self.cli_return_compliant_value, "", 0)
        result = self.controller.remediate(self.mock_host_context, self.compliant_value)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result
