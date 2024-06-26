from mock import patch

from config_modules_vmware.controllers.vcenter.dns_config import DnsConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.clients.vcenter.vc_consts import VC_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDNSConfig:
    def setup_method(self):
        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = VC_API_BASE.format(self.mock_vc_host_name)

        # Initialize control
        self.controller = DnsConfig()

        self.compliant_value = {"mode": "is_static", "servers": ["10.0.0.250", "10.0.0.251"]}
        self.desired_values_with_extra_fields = {"mode": "is_static", "servers": ["10.0.0.250", "10.0.0.251"],
                                                 "extra_key": 10}
        self.non_compliant_value = {"mode": "dhcp", "servers": ["8.8.8.8", "8.8.4.4"]}

        self.output_during_exception = {"servers": [], "mode": ""}

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success(self, mock_vc_rest_client, mock_vc_context):

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_value
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while fetching DNS config")

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
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)

        mock_vc_rest_client.put_helper.assert_called_with(self.vc_base_url + vc_consts.DNS_URL,
                                                          body={"mode": self.compliant_value.get("mode"),
                                                                "servers": self.compliant_value.get("servers")},
                                                          raise_for_status=True)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Setting DNS server failed")

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.put_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)

        mock_vc_rest_client.put_helper.assert_called_with(self.vc_base_url + vc_consts.DNS_URL,
                                                          body={"mode": self.compliant_value.get("mode"),
                                                                "servers": self.compliant_value.get("servers")},
                                                          raise_for_status=True)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_compliant(self, mock_vc_rest_client, mock_vc_context):

        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_non_compliant(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value
        }

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Compliance check failed while fetching DNS servers")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_skipped_already_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ['Control already compliant']}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_success(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_value,
                           consts.NEW: self.compliant_value}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while getting DNS Mode during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Remediation failed while setting DNS Server")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.non_compliant_value
        mock_vc_rest_client.put_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_with_extra_fields_in_desired(self, mock_vc_rest_client, mock_vc_context):

        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_values_with_extra_fields)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_with_extra_fields_in_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_value,
                           consts.NEW: self.compliant_value}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.desired_values_with_extra_fields)

        assert result == expected_result
