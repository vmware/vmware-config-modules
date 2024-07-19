# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.syslog_enforce_ssl_certificates import SyslogEnforceSslCertificates
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSyslogEnforceSslCertificates:
    def setup_method(self):
        self.controller = SyslogEnforceSslCertificates()
        self.compliant_value = True
        self.non_compliant_value = False
        self.cli_return_compliant_value = "   Allow Vsan Backing: false\n" \
                                          "   Enforce SSLCertificates: true\n" \
                                          "   Log Level: error"
        self.cli_return_non_compliant_value = "   Allow Vsan Backing: false\n" \
                                              "   Enforce SSLCertificates: false\n" \
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
        assert result is None
        assert errors == [expected_error]

    def test_get_failed_cli_not_returning_ssl_certs_policy(self):
        cli_return_value = "   Allow Vsan Backing: false\n" \
                           "   Log Level: error"
        expected_error = "Unable to fetch enforce ssl certs using command esxcli system syslog config get"
        self.esx_cli_client().run_esx_cli_cmd.return_value = (cli_return_value, "", 0)
        result, errors = self.controller.get(self.mock_host_context)
        assert result is None
        assert errors == [expected_error]

    def test_set_success(self):
        self.esx_cli_client().run_esx_cli_cmd.return_value = (self.cli_return_non_compliant_value, "", 0)
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    def test_set_failed(self):
        expected_error = "Test exception"
        self.esx_cli_client().run_esx_cli_cmd.side_effect = Exception(expected_error)
        status, errors = self.controller.set(self.mock_host_context, self.compliant_value)
        assert status == RemediateStatus.FAILED
        assert errors == [expected_error]

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
        self.esx_cli_client().run_esx_cli_cmd.return_value = (self.cli_return_non_compliant_value, "", 0)
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
            consts.ERRORS: ['Control already compliant']
        }
        assert result == expected_result
