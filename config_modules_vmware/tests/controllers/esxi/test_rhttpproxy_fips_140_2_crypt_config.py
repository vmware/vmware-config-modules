# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.rhttpproxy_fips_140_2_crypt_config import RHttpProxyFips140_2CryptConfig
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestRHttpProxyFips140_2CryptConfig:
    def setup_method(self):
        self.controller = RHttpProxyFips140_2CryptConfig()
        self.compliant_value = True
        self.non_compliant_value = False
        self.cli_return_compliant_value = "   Enabled: true"
        self.cli_return_non_compliant_value = "   Enabled: false"
        mock_host_ref = MagicMock()
        mock_host_ref.name = 'host-1'
        mock_host_ref.config.product.version = "7.0.3"
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

    def test_get_failed_cli_not_returning_rhttpproxy_fips_config(self):
        cli_return_value = ""
        expected_error = "Unable to fetch rhttpproxy fips config using command" \
                         " esxcli system security fips140 rhttpproxy get"
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
            consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]
        }
        assert result == expected_result

    def test_get_skipped(self):
        mock_host_context = MagicMock()
        mock_host_context.product_version = "8.0.0"
        result, errors = self.controller.get(mock_host_context)
        assert result is None
        assert errors == [consts.SKIPPED]

    def test_set_skipped(self):
        mock_host_context = MagicMock()
        mock_host_context.product_version = "8.0.0"
        status, errors = self.controller.set(mock_host_context, self.compliant_value)
        assert status == RemediateStatus.SKIPPED
        assert errors == [consts.CONTROL_NOT_APPLICABLE]

    def test_check_compliance_skipped(self):
        mock_host_context = MagicMock()
        mock_host_context.product_version = "8.0.0"
        expected_result = {
            consts.STATUS: ComplianceStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_NOT_APPLICABLE]
        }
        result = self.controller.check_compliance(mock_host_context, "no")
        assert expected_result == result
