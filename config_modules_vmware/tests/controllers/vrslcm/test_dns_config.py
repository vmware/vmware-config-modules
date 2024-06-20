# Copyright 2024 Broadcom. All Rights Reserved.
import requests
from mock import ANY
from mock import call
from mock import Mock
from mock import patch

from config_modules_vmware.controllers.vrslcm.dns_config import DnsConfig
from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDnsConfig:

    def setup_method(self):
        self.hostname = "localhost"
        self.context = VrslcmContext(self.hostname)
        self.config = DnsConfig()
        patch('config_modules_vmware.framework.clients.aria_suite.aria_auth.get_http_headers', return_value="").start()

    @patch('config_modules_vmware.controllers.vrslcm.dns_config.requests.request')
    def test_check_compliance(self, mock_request):
        get_dns_api_response = [{"hostName": "8.8.8.8", "name": "dns1"}, {"hostName": "8.8.4.4", "name": "dns2"}]
        desired_value = {"mode": "is_static", "servers": [server['hostName'] for server in get_dns_api_response]}
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = get_dns_api_response

        with self.context:
            result = self.config.check_compliance(context=self.context, desired_values=desired_value)
            assert result.get(consts.STATUS) == ComplianceStatus.COMPLIANT

    @patch('config_modules_vmware.controllers.vrslcm.dns_config.requests.request')
    def test_non_compliance(self, mock_request):
        get_dns_api_response = [{"hostName": "8.8.8.8", "name": "dns1"}, {"hostName": "8.8.4.4", "name": "dns2"}]
        desired_value = {"mode": "is_static", "servers": ["8.8.8.8", "4.4.4.4"]}
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = get_dns_api_response

        result = self.config.check_compliance(context=self.context, desired_values=desired_value)
        assert result.get(consts.STATUS) == ComplianceStatus.NON_COMPLIANT
        assert result.get(consts.CURRENT) == {"servers": [server["hostName"] for server in get_dns_api_response]}
        assert result.get(consts.DESIRED) == {"servers": desired_value.get("servers", {})}

    @patch('config_modules_vmware.controllers.vrslcm.dns_config.requests.request')
    def test_compliance_failed(self, mock_request):
        expected_error = "test exception"
        expected_errors = [requests.exceptions.HTTPError(expected_error)]
        mock_request.return_value.status_code = 404
        mock_request.return_value.raise_for_status.side_effect = expected_errors[0]

        desired_value = {"mode": "is_static", "servers": ["8.8.8.8", "4.4.4.4"]}
        result = self.config.check_compliance(self.context, desired_value)

        assert result.get(consts.STATUS) == ComplianceStatus.FAILED
        assert result.get(consts.ERRORS) == [expected_error]

    @patch('config_modules_vmware.controllers.vrslcm.dns_config.requests.request')
    def test_remediate_success(self, mock_request):
        mock_get = Mock()
        mock_get.json.return_value = [{"hostName": "8.8.4.4", "name": "dns1"}, {"hostName": "8.8.8.8", "name": "dns2"}]
        mock_get.status_code = 200

        mock_call = Mock()
        mock_call.status_code = 200

        desired_value = {"mode": "is_static", "servers": ["time.google.com", "time.vmware.com"]}
        mock_request.side_effect = [mock_get, mock_get, mock_call, mock_call, mock_call, mock_call]
        status = self.config.remediate(self.context, desired_value)
        mock_request.assert_has_calls([
            call("GET", f"https://{self.hostname}/lcm/lcops/api/v2/settings/dns", headers=ANY,
                 data=ANY, verify=False, timeout=ANY),
            call("GET", f"https://{self.hostname}/lcm/lcops/api/v2/settings/dns", headers=ANY,
                 data=ANY, verify=False, timeout=ANY),
            call("DELETE", f"https://{self.hostname}/lcm/lcops/api/v2/settings/dns", headers=ANY,
                 data='{"name": "dns1", "hostName": "8.8.4.4"}', verify=False, timeout=ANY),
            call("DELETE", f"https://{self.hostname}/lcm/lcops/api/v2/settings/dns", headers=ANY,
                 data='{"name": "dns2", "hostName": "8.8.8.8"}', verify=False, timeout=ANY),
            call("POST", f"https://{self.hostname}/lcm/lcops/api/v2/settings/dns", headers=ANY,
                 data='{"name": "dns", "hostName": "time.google.com"}', verify=False, timeout=ANY),
            call("POST", f"https://{self.hostname}/lcm/lcops/api/v2/settings/dns", headers=ANY,
                 data='{"name": "dns1", "hostName": "time.vmware.com"}', verify=False, timeout=ANY)
        ])
        assert status.get(consts.STATUS) == RemediateStatus.SUCCESS

    @patch('config_modules_vmware.controllers.vrslcm.dns_config.requests.request')
    def test_remediate_failed(self, mock_request):
        mock_get = Mock()
        mock_get.json.return_value = [{"hostName": "8.8.8.8", "name": "dns1"}, {"hostName": "8.8.4.4", "name": "dns2"}]
        mock_get.status_code = 200

        mock_set = Mock()
        expected_error = "test exception"
        expected_errors = [requests.exceptions.HTTPError(expected_error)]
        mock_set.status_code = 404
        mock_set.raise_for_status.side_effect = expected_errors[0]

        mock_request.side_effect = [mock_get, mock_set]
        desired_value = {"mode": "is_static", "servers": ["8.8.8.8", "4.4.4.4"]}
        result = self.config.remediate(self.context, desired_value)

        assert result.get(consts.STATUS) == RemediateStatus.FAILED
        assert result.get(consts.ERRORS) == [expected_error]

    def teardown_method(self):
        patch.stopall()
