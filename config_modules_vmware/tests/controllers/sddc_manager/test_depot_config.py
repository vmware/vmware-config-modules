from mock import patch

from config_modules_vmware.controllers.sddc_manager.depot_config import DepotConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import SDDC_MANAGER_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDepotConfig:
    def setup_method(self):
        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.sddc_base_url = SDDC_MANAGER_API_BASE.format(self.mock_vc_host_name)

        # Initialize control
        self.controller = DepotConfig()

        self.compliant_value = {"vmware_account": {"username": "vlcmtester4@vmware.com", "password": "test123"}}
        self.get_helper_values = {"vmwareAccount": {"username": "vlcmtester4@vmware.com", "password": "test123",
                                                    "status": "DEPOT_CONNECTION_SUCCESSFUL", "message":
                                                        "Depot Status: Success"}}
        self.get_helper_non_compliant_values = {"vmware_account": None}
        self.put_helper_values = {"vmwareAccount": {"username": "vlcmtester4@vmware.com", "password": "test123"}}
        self.non_compliant_value = {"vmware_account": None}

        self.output_during_exception = {}

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.compliant_value
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while fetching Depot config")

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

        mock_sddc_manager_rest_client.put_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.DEPOT_URL,
                                                                    body=self.put_helper_values, raise_for_status=True)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Setting Depot Config failed")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.put_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_value)

        mock_sddc_manager_rest_client.put_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.DEPOT_URL,
                                                                    body=self.put_helper_values,
                                                                    raise_for_status=True)

        assert result == RemediateStatus.FAILED
        assert errors == ["Check for valid depot credentials and retry!!:" + str(expected_error)]

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
            consts.DESIRED: self.compliant_value
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
    def test_remediate_skipped_already_desired(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

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
                           consts.NEW: self.compliant_value}

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
        expected_error = Exception("Remediation failed while setting Depot Config")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: ["Check for valid depot credentials and retry!!:" + str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_rest_client.put_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result
