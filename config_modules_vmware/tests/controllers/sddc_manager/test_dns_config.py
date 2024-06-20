from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.sddc_manager.dns_config import DnsConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import SDDC_MANAGER_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDNSConfig:
    def setup_method(self):
        # SDDC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.sddc_base_url = SDDC_MANAGER_API_BASE.format(self.mock_vc_host_name)

        # Initialize control
        self.controller = DnsConfig()
        self.compliant_value = {"servers": ["10.0.0.250", "10.221.77.21"], "is_local": False}
        self.compliant_single_value = {"servers": ["10.0.0.250"], "is_local": False}
        self.get_helper_values = {"dnsServers": [{"ipAddress": "10.0.0.250", "isPrimary": 'true'},
                                                 {"ipAddress": "10.221.77.21", "isPrimary": 'false'}]}
        self.get_helper_single_value = {"dnsServers": [{"ipAddress": "10.0.0.250", "isPrimary": 'true'}]}
        self.get_helper_non_compliant_values = {"dnsServers": [{"ipAddress": "8.8.8.8", "isPrimary": 'true'}]}
        self.put_helper_values = {"dnsServers": [{"ipAddress": "10.0.0.250", "isPrimary": 'true'},
                                                 {"ipAddress": "10.221.77.21", "isPrimary": 'false'}]}
        self.put_helper_single_value = {"dnsServers": [{"ipAddress": "10.0.0.250", "isPrimary": 'true'}]}
        self.non_compliant_value = {"servers": ["8.8.8.8"]}
        self.task_info = {"id": "5e31e722-e66d-4da0-a8ce-e8b42aef3e03", "name": "Configure DNS servers on VCF system",
                          "status": "IN_PROGRESS", "creationTimestamp": "2024-02-15T06:00:09.336Z"}
        self.output_during_exception = {"servers": []}

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)
        assert result == {'servers': self.compliant_value.get('servers', [])}
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while fetching DNS config")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.output_during_exception
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_value)

        mock_sddc_manager_rest_client.put_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.DNS_URL,
                                                                    body=self.put_helper_values, raise_for_status=True)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_success_single_value(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_single_value)

        mock_sddc_manager_rest_client.put_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.DNS_URL,
                                                                    body=self.put_helper_single_value, raise_for_status=True)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Setting DNS server failed")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.put_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_value)

        mock_sddc_manager_rest_client.put_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.DNS_URL,
                                                                    body=self.put_helper_values,
                                                                    raise_for_status=True)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_non_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: {'servers': self.compliant_value.get('servers', [])}
        }

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Compliance check failed while fetching DNS servers")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success_already_desired(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_value,
                           consts.NEW: {'servers': self.compliant_value.get('servers', [])}}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while getting DNS Mode during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Remediation failed while setting DNS Server")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_rest_client.put_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_task_status_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = True

        status, errors = self.controller.set(mock_sddc_manager_context, self.compliant_value)

        # Assertions
        assert status == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_task_status_failure(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Set up expected values
        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = False

        status, errors = self.controller.set(mock_sddc_manager_context, self.compliant_value)

        # Assertions
        assert status == RemediateStatus.FAILED
        assert errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.framework.clients.common.rest_client.get_smart_rest_client')
    def test_remediate_local_success(self, mock_get_smart_rest_client,
                                     mock_sddc_manager_rest_client,
                                     mock_sddc_manager_context):
        desired_values = {"is_local": True, "servers": ["10.0.0.250", "10.0.0.251"]}
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: {'servers': ['8.8.8.8']},
            consts.NEW: {'servers': desired_values.get('servers', [])}
        }
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_smart_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_smart_client.patch.return_value = mock_response
        mock_smart_client.raise_for_status.return_value = None
        mock_get_smart_rest_client.return_value = mock_smart_client

        result = self.controller.remediate(context=mock_sddc_manager_context, desired_values=desired_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.framework.clients.common.rest_client.get_smart_rest_client')
    def test_remediate_local_set_failed(self, mock_get_smart_rest_client,
                                        mock_sddc_manager_rest_client,
                                        mock_sddc_manager_context):
        expected_error = Exception("Remediation failed while setting DNS Server")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        desired_values = {"is_local": True, "servers": ["10.0.0.250", "10.0.0.251"]}
        mock_smart_client = MagicMock()
        mock_smart_client.patch.side_effect = expected_error
        mock_get_smart_rest_client.return_value = mock_smart_client

        result = self.controller.remediate(context=mock_sddc_manager_context, desired_values=desired_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.framework.clients.common.rest_client.get_smart_rest_client')
    def test_remediate_local_only_primary(self, mock_get_smart_rest_client,
                                          mock_sddc_manager_rest_client,
                                          mock_sddc_manager_context):
        desired_values = {"is_local": True, "servers": ["10.0.0.250"]}
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: {'servers': ['8.8.8.8']},
            consts.NEW: {'servers': desired_values.get('servers', [])}
        }
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_smart_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_smart_client.patch.return_value = mock_response
        mock_smart_client.raise_for_status.return_value = None
        mock_get_smart_rest_client.return_value = mock_smart_client

        result = self.controller.remediate(context=mock_sddc_manager_context, desired_values=desired_values)
        assert result == expected_result
