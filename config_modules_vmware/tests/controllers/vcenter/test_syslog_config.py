from mock import patch

from config_modules_vmware.controllers.vcenter.syslog_config import SyslogConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.clients.vcenter.vc_consts import VC_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSysLogConfig:
    def setup_method(self):
        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = VC_API_BASE.format(self.mock_vc_host_name)

        self.controller = SyslogConfig()

        # Expected Desired states
        self.compliant_value = {
            "servers": [
                {
                    "hostname": "10.0.0.250",
                    "protocol": "TLS",
                    "port": 514
                },
                {
                    "hostname": "10.0.0.251",
                    "protocol": "TLS",
                    "port": 514
                }
            ]
        }
        self.get_helper_compliant_value = [
            {
                "hostname": "10.0.0.250",
                "protocol": "TLS",
                "port": 514
            },
            {
                "hostname": "10.0.0.251",
                "protocol": "TLS",
                "port": 514
            }
        ]

        # Expected Desired states
        self.desired_values_with_extra_fields = {
            "servers": [
                {
                    "hostname": "10.0.0.250",
                    "protocol": "TLS",
                    "port": 514
                },
                {
                    "hostname": "10.0.0.251",
                    "protocol": "TLS",
                    "port": 514
                }
            ],
            "extra_field": 10
        }
        self.put_payload_compliant_value = {"cfg_list": self.compliant_value.get("servers")}
        self.non_compliant_value = self.output_during_exception = {"servers": []}
        self.get_helper_non_compliant_value = []

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success(self, mock_vc_rest_client, mock_vc_context):

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.get_helper_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_value
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while fetching syslog config")

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

        mock_vc_rest_client.put_helper.assert_called_with(self.vc_base_url + vc_consts.SYSLOG_URL,
                                                          body=self.put_payload_compliant_value,
                                                          raise_for_status=True)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Setting Syslog server failed")

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.put_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)

        mock_vc_rest_client.put_helper.assert_called_with(self.vc_base_url + vc_consts.SYSLOG_URL,
                                                          body=self.put_payload_compliant_value,
                                                          raise_for_status=True)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_compliant(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.get_helper_compliant_value
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
        mock_vc_rest_client.get_helper.return_value = self.get_helper_non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Compliance check failed while fetching SYSlog servers")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_success_already_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.get_helper_compliant_value
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
        mock_vc_rest_client.get_helper.return_value = self.get_helper_non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while getting SYSlog config during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_set_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Remediation failed while setting Syslog Server")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.get_helper_non_compliant_value

        mock_vc_rest_client.put_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_with_extra_fields_in_desired(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.get_helper_compliant_value
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
        mock_vc_rest_client.get_helper.return_value = self.get_helper_non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.remediate(mock_vc_context, self.desired_values_with_extra_fields)
        assert result == expected_result
