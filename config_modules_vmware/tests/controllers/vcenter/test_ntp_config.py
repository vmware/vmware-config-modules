from mock import call
from mock import patch

from config_modules_vmware.controllers.vcenter.ntp_config import NtpConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.clients.vcenter.vc_consts import VC_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestNtpConfig:
    def setup_method(self):
        self.controller = NtpConfig()

        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = VC_API_BASE.format(self.mock_vc_host_name)
        # Desired
        self.compliant_ntp_servers = ["time.vmware.com", "10.0.0.250"]
        self.compliant_ntp_mode = "NTP"
        # Exception
        self.output_during_exception = {'mode': '', 'servers': []}
        self.compliant_values = {'mode': self.compliant_ntp_mode, 'servers': self.compliant_ntp_servers}
        # Un-Desired
        self.non_compliant_ntp_servers = ["xyz.abc.com", "0.0.0.0"]
        self.non_compliant_ntp_mode = "DISABLED"
        self.non_compliant_values = {'mode': self.non_compliant_ntp_mode, 'servers': self.non_compliant_ntp_servers}

        self.desired_values_with_extra_fields = {'mode': self.compliant_ntp_mode, 'servers': self.compliant_ntp_servers,
                                                 "extra_field": 10}

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {"mode": self.compliant_ntp_mode, "servers": self.compliant_ntp_servers}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.compliant_ntp_servers, self.compliant_ntp_mode]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == expected_result
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while fetching NTP config")

        mock_vc_rest_client.get_helper.side_effect = [expected_error, ""]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.output_during_exception
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_success(self, mock_vc_rest_client, mock_vc_context):

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_values)

        expected_put_helper_calls = [
            call(self.vc_base_url + vc_consts.NTP_URL, body={"servers": self.compliant_values.get("servers")},
                 raise_for_status=True),
            call(self.vc_base_url + vc_consts.TIMESYNC_URL, body={"mode": self.compliant_values.get("mode")},
                 raise_for_status=True),
        ]

        # Asset calls in order, since we call set server followed by set mode
        mock_vc_rest_client.put_helper.assert_has_calls(expected_put_helper_calls, any_order=False)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Setting NTP server failed")

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.put_helper.side_effect = [expected_error, []]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_values)

        expected_put_helper_calls = [
            call(self.vc_base_url + vc_consts.NTP_URL, body={"servers": self.compliant_values.get("servers")},
                 raise_for_status=True),
            call(self.vc_base_url + vc_consts.TIMESYNC_URL, body={"mode": self.compliant_values.get("mode")},
                 raise_for_status=True),

        ]
        # Asset calls in order, since we call get server followed by get mode
        mock_vc_rest_client.put_helper.assert_has_calls(expected_put_helper_calls, any_order=False)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_compliant(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.compliant_ntp_servers, self.compliant_ntp_mode]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_non_compliant(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_values,
            consts.DESIRED: self.compliant_values
        }

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.non_compliant_ntp_servers, self.non_compliant_ntp_mode]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Compliance check failed while fetching NTP servers")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_helper.side_effect = [expected_error, []]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_success_already_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.compliant_ntp_servers, self.compliant_ntp_mode]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_success(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_values,
                           consts.NEW: self.compliant_values}
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.non_compliant_ntp_servers, self.non_compliant_ntp_mode]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while getting NTP Mode during remediation")

        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_helper.side_effect = [[], expected_error]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Remediation failed while setting NTP Mode")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.non_compliant_ntp_servers, self.non_compliant_ntp_mode]

        mock_vc_rest_client.put_helper.side_effect = [[], expected_error]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_values)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_with_extra_fields_in_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.compliant_ntp_servers, self.compliant_ntp_mode]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_with_extra_fields_in_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_values,
                           consts.NEW: self.compliant_values}
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = [self.non_compliant_ntp_servers, self.non_compliant_ntp_mode]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_values)

        assert result == expected_result
