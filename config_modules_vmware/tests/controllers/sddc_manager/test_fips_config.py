from mock import patch

from config_modules_vmware.controllers.sddc_manager.fips_config import FipsConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestFipsConfig:
    def setup_method(self):
        self.controller = FipsConfig()

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        # Setup Mock objects.
        expected_result = {'enabled': True}

        mock_sddc_manager_rest_client.get_helper.return_value = expected_result
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_sddc_manager_context)

        # Assert expected results.
        assert result == expected_result['enabled']
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        # Setup Mock objects to raise an exception.
        expected_error = "test exception"
        expected_errors = [expected_error]

        mock_sddc_manager_rest_client.get_helper.side_effect = Exception(expected_error)
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_sddc_manager_context)

        # Assert expected results.
        assert result == None
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_skipped(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        # Setup Mock objects for successfully changing the value.
        desired_value = True
        current_value = {'enabled': False}

        expected_result = {'errors': [consts.REMEDIATION_SKIPPED_MESSAGE], consts.STATUS: RemediateStatus.SKIPPED,
                           consts.DESIRED: desired_value, consts.CURRENT: current_value['enabled']}

        mock_sddc_manager_rest_client.get_helper.return_value = current_value
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Call Controller.
        result = self.controller.remediate(mock_sddc_manager_context, desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed_type_error(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        # Setup Mock objects to raise an exception.
        expected_error = "FIPS response is not a dictionary"
        expected_errors = [expected_error]

        mock_sddc_manager_rest_client.get_helper.return_value = "enabled"
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_sddc_manager_context)

        # Assert expected results.
        assert result == None
        assert errors == expected_errors
