from mock import patch

from config_modules_vmware.controllers.sample.sample_controller import SampleController
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestSampleController:
    def setup_method(self):
        # Initialize controller.
        self.controller = SampleController()

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects.
        expected_result = 123
        mock_vc_rest_client.get_helper.return_value = expected_result
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_vc_context)

        # Assert expected results.
        assert result == expected_result
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_failed(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects to raise an exception.
        expected_error = "test exception"
        expected_errors = [expected_error]
        mock_vc_rest_client.get_helper.side_effect = Exception(expected_error)
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_vc_context)

        # Assert expected results.
        assert result == -1
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_success(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects.
        mock_vc_rest_client.get_base_url.return_value = "base_url"
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call controller.
        desired_value = 123
        result, errors = self.controller.set(mock_vc_context, desired_value)

        # Verify controller calls the Mock objects with expected parameters.
        mock_vc_rest_client.put_helper.assert_called_with("base_url/test_url/sample_control",
                                                          body={"sample_control": desired_value}, raise_for_status=True)

        # Assert expected results.
        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_failed(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects to raise an exception.
        expected_error = "test exception"
        expected_errors = [expected_error]
        desired_value = 123
        mock_vc_rest_client.get_base_url.return_value = "base_url"
        mock_vc_rest_client.put_helper.side_effect = Exception(expected_error)
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result, errors = self.controller.set(mock_vc_context, desired_value)

        # Verify controller calls the Mock objects with expected parameters.
        mock_vc_rest_client.put_helper.assert_called_with("base_url/test_url/sample_control",
                                                          body={"sample_control": desired_value}, raise_for_status=True)

        # Assert expected results.
        assert result == RemediateStatus.FAILED
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_compliant(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for current value to equal the desired value.
        desired_value = 123
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        mock_vc_rest_client.get_helper.return_value = desired_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.check_compliance(mock_vc_context, desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_non_compliant(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for current value being different from the desired value.
        desired_value = 123
        non_desired_value = 456
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_desired_value,
            consts.DESIRED: desired_value
        }
        mock_vc_rest_client.get_helper.return_value = non_desired_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.check_compliance(mock_vc_context, desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_failed(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for get function to raise an exception.
        desired_value = 123
        expected_error = "test exception"
        expected_errors = [expected_error]
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: expected_errors}

        mock_vc_rest_client.get_helper.side_effect = Exception(expected_error)
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.check_compliance(mock_vc_context, desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_success_already_desired(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for current value already being the desired value.
        desired_value = 123
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}
        mock_vc_rest_client.get_helper.return_value = desired_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_success(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for successfully changing the value.
        desired_value = 123
        current_value = 456
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS, consts.OLD: current_value, consts.NEW: desired_value}
        mock_vc_rest_client.get_helper.return_value = current_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_get_failed(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for get function to raise an exception.
        desired_value = 123
        expected_error = "test exception"
        expected_errors = [expected_error]
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: expected_errors}
        mock_vc_rest_client.get_helper.side_effect = Exception(expected_error)
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_set_failed(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for set function to raise an exception.
        desired_value = 123
        current_value = 456
        expected_error = "test exception"
        expected_errors = [expected_error]
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: expected_errors}
        mock_vc_rest_client.get_helper.return_value = current_value
        mock_vc_rest_client.put_helper.side_effect = Exception(expected_error)
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, desired_value)

        # Assert expected results.
        assert result == expected_result
