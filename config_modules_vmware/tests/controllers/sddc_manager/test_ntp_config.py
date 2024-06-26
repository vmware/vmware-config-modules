from mock import call
from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.sddc_manager.ntp_config import NtpConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import SDDC_MANAGER_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestNtpConfig:
    def setup_method(self):
        self.controller = NtpConfig()

        # SDDC API Base url
        self.mock_sddc_host_name = "mock-sddc.eng.vmware.com"
        self.sddc_base_url = SDDC_MANAGER_API_BASE.format(self.mock_sddc_host_name)
        # Desired
        self.compliant_values = {"servers": ["10.0.0.250", "time.vmware.com"], "is_local": False}
        self.get_helper_values = {"ntpServers": [{"ipAddress": "10.0.0.250"}, {"ipAddress": "time.vmware.com"}]}
        self.get_helper_non_compliant_values = {"ntpServers": [{"ipAddress": "xyz.abc.com"}, {"ipAddress": "0.0.0.0"}]}
        self.put_helper_values = {"ntpServers": [{"ipAddress": server} for server in self.compliant_values.get("servers")],}
        # Exception
        self.output_during_exception = {'servers': []}
        # Non-Desired
        self.non_compliant_ntp_servers = ["xyz.abc.com", "0.0.0.0"]
        self.non_compliant_values = {"servers": ["xyz.abc.com", "0.0.0.0"]}
        self.task_info = {"id": "e2b61c4b-fbb5-4faf-b4bf-a8690fa13673", "name": "Configuring NTP servers on VCF system",
                          "status": "IN_PROGRESS", "creationTimestamp": "2024-02-15T05:49:48.031Z"
}

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == {'servers': self.compliant_values.get('servers', [])}
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while fetching NTP config")
        mock_sddc_manager_rest_client.get_helper.side_effect = [expected_error, ""]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Instantiate the class containing the `get` method
        result, errors = self.controller.get(mock_sddc_manager_context)
        assert result == self.output_during_exception
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)

        expected_put_helper_calls = [
            call(self.sddc_base_url + sddc_manager_consts.NTP_URL, body=self.put_helper_values,
                 raise_for_status=True)
        ]

        # Asset calls in order, since we call set server followed by set mode
        mock_sddc_manager_rest_client.put_helper.assert_has_calls(expected_put_helper_calls, any_order=False)
        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Setting NTP server failed")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.put_helper.side_effect = [expected_error, []]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)
        expected_put_helper_calls = [
            call(self.sddc_base_url + sddc_manager_consts.NTP_URL, body=self.put_helper_values,
                 raise_for_status=True)

        ]
        # Asset calls in order, since we call get server followed by get mode
        mock_sddc_manager_rest_client.put_helper.assert_has_calls(expected_put_helper_calls, any_order=False)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_non_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_values,
            consts.DESIRED: {'servers': self.compliant_values.get('servers', [])}
        }

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Compliance check failed while fetching NTP servers")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_helper.side_effect = [expected_error, []]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success_already_desired(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.get_helper_values]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_values,
                           consts.NEW: {'servers': self.compliant_values.get('servers', [])}}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.get_helper_non_compliant_values]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while getting NTP Mode during remediation")

        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_helper.side_effect = [expected_error, ""]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Remediation failed while setting NTP Mode")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.get_helper_non_compliant_values]

        mock_sddc_manager_rest_client.put_helper.side_effect = [expected_error, []]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_task_status_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = True
        status, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)

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

        status, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)

        # Assertions
        assert status == RemediateStatus.FAILED
        assert errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    @patch('config_modules_vmware.framework.clients.common.rest_client.get_smart_rest_client')
    def test_remediate_local_success_ntp(self, mock_get_smart_rest_client,
                                         mock_sddc_manager_rest_client,
                                         mock_sddc_manager_context):
        desired_values = {"is_local": True, "servers": ["10.0.0.250"]}
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: {'servers': ['xyz.abc.com', '0.0.0.0']},
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
        desired_values = {"is_local": True, "servers": ["10.0.0.250"]}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        expected_error = Exception("Exception while setting NTP during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_smart_client = MagicMock()
        mock_smart_client.patch.side_effect = expected_error
        mock_get_smart_rest_client.return_value = mock_smart_client

        result = self.controller.remediate(context=mock_sddc_manager_context, desired_values=desired_values)
        assert result == expected_result
