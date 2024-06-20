from mock import patch

from config_modules_vmware.controllers.vcenter.cert_config import CertConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_consts import VC_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestCertConfig:
    def setup_method(self):
        self.controller = CertConfig()
        self.control_desired_value = {"certificate_issuer": ["OU=VMwareEngineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB","OU=VMwareEngineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"]}
        self.vc_return_value = {"issuer_dn": "OU=VMwareEngineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB"}
        self.vc_return_non_compliant_value = {"issuer_dn": "OU=VMwareSales,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB"}
        self.compliant_value = {"issuer": "OU=VMwareEngineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB"}
        self.non_compliant_display_value = "OU=VMwareSales,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB"
        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = VC_API_BASE.format(self.mock_vc_host_name)

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success(self, mock_vc_rest_client, mock_vc_context):

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_return_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_value
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
        assert result == {}
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_no_issuer(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects to raise an exception.
        expected_error = Exception("Unable to fetch issuer details from cert")

        mock_vc_rest_client.get_helper.return_value = {}
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_vc_context)

        # Assert expected results.
        assert result == {}
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_set_skipped(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for successfully changing the value.
        current_value = ["OU=VMwareEngineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"]
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ["Set is not implemented as this control requires manual intervention"]}
        mock_vc_rest_client.get_helper.return_value = current_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result, errors = self.controller.set(mock_vc_context, self.compliant_value)

        # Assert expected results.
        assert result == expected_result[consts.STATUS]
        assert errors == expected_result[consts.ERRORS]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_remediate_skipped(self, mock_vc_rest_client, mock_vc_context):
        # Setup Mock objects for successfully changing the value.

        current_value = ["OU=VMwareEngineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"]
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [
            "Set is not implemented as this control requires manual intervention"],
                           consts.DESIRED: self.control_desired_value, consts.CURRENT: self.non_compliant_display_value}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_return_non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        # Call Controller.
        result = self.controller.remediate(mock_vc_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = "test exception"
        expected_errors = [expected_error]
        mock_vc_rest_client.get_helper.side_effect = Exception(expected_error)
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: expected_errors}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_return_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_compliant(self, mock_vc_rest_client, mock_vc_context):

        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_return_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_non_compliant(self, mock_vc_rest_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_display_value,
            consts.DESIRED: self.control_desired_value
        }

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_return_non_compliant_value
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.control_desired_value)

        assert result == expected_result
