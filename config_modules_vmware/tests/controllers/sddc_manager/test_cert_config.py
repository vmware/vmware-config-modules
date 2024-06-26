from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.sddc_manager.cert_config import CertConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestCertConfig:
    def setup_method(self):
        self.controller = CertConfig()
        self.control_desired_value = {"certificate_issuer": ["OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB","OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"]}
        self.desired_api_response = {'elements': [
            {'domain': {'id': '7e76a916-c85b-4bf8-b5f1-284eadb3c6dd'}, 'id': 'ca773c66-7c7e-4738-bb0a-f14d162fc7d4',
             'fqdn': 'sddc-manager.vrack.vsphere.local', 'version': '4.4.1.1-19948546', 'ipAddress': '10.0.0.4'}]}
        self.get_expected_result = {'issuer': 'OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA'}
        self.issuer = "OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"
        self.non_compliant_issuer = "OU=VMwareEngineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"

    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('ssl.DER_cert_to_PEM_cert', MagicMock())
    @patch('ssl.SSLSocket.getpeercert', MagicMock())
    @patch('ssl.SSLContext.wrap_socket', MagicMock())
    @patch('socket.create_connection', MagicMock())
    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context, mock_load_pem_x509_certificate):

        # Setup Mock objects.
        mock_sddc_manager_rest_client.get_helper.return_value = self.desired_api_response
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_cert_obj = MagicMock()
        # Set the return value for issuer.rfc4514_string()
        mock_cert_obj.issuer.rfc4514_string.return_value = self.issuer
        # Set the return value for x509.load_pem_x509_certificate()
        mock_load_pem_x509_certificate.return_value = mock_cert_obj

        # Call Controller.
        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.get_expected_result
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_helper_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        expected_error = "test exception"
        expected_errors = [expected_error]

        mock_sddc_manager_rest_client.get_helper.side_effect = Exception(expected_error)
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_sddc_manager_context)

        # Assert expected results.
        assert result == {}
        assert errors == expected_errors

    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('ssl.DER_cert_to_PEM_cert', MagicMock())
    @patch('ssl.SSLSocket.getpeercert', MagicMock())
    @patch('ssl.SSLContext.wrap_socket', MagicMock())
    @patch('socket.create_connection', MagicMock())
    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_skipped(self, mock_sddc_manager_rest_client, mock_sddc_manager_context, mock_load_pem_x509_certificate):

        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE],
                           consts.DESIRED: self.control_desired_value, consts.CURRENT: self.non_compliant_issuer}

        mock_sddc_manager_rest_client.get_helper.return_value = self.desired_api_response
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_cert_obj = MagicMock()

        # Set the return value for issuer.rfc4514_string()
        mock_cert_obj.issuer.rfc4514_string.return_value = self.non_compliant_issuer

        # Set the return value for x509.load_pem_x509_certificate()
        mock_load_pem_x509_certificate.return_value = mock_cert_obj
        # Call Controller.
        result = self.controller.remediate(mock_sddc_manager_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('ssl.DER_cert_to_PEM_cert', MagicMock())
    @patch('ssl.SSLSocket.getpeercert', MagicMock())
    @patch('ssl.SSLContext.wrap_socket', MagicMock())
    @patch('socket.create_connection', MagicMock())
    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context,
                                        mock_load_pem_x509_certificate):

        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_sddc_manager_rest_client.get_helper.return_value = self.desired_api_response
        mock_sddc_manager_context.mock_sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_cert_obj = MagicMock()

        # Set the return value for issuer.rfc4514_string()
        mock_cert_obj.issuer.rfc4514_string.return_value = self.issuer

        # Set the return value for x509.load_pem_x509_certificate()
        mock_load_pem_x509_certificate.return_value = mock_cert_obj

        # Call Controller.
        result = self.controller.check_compliance(mock_sddc_manager_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('ssl.DER_cert_to_PEM_cert', MagicMock())
    @patch('ssl.SSLSocket.getpeercert', MagicMock())
    @patch('ssl.SSLContext.wrap_socket', MagicMock())
    @patch('socket.create_connection', MagicMock())
    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_non_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context,
                                            mock_load_pem_x509_certificate):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_issuer,
            consts.DESIRED: self.control_desired_value
        }

        mock_sddc_manager_rest_client.get_helper.return_value = self.desired_api_response
        mock_sddc_manager_context.mock_sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_cert_obj = MagicMock()

        # Set the return value for issuer.rfc4514_string()
        mock_cert_obj.issuer.rfc4514_string.return_value = self.non_compliant_issuer

        # Set the return value for x509.load_pem_x509_certificate()
        mock_load_pem_x509_certificate.return_value = mock_cert_obj

        # Call Controller.
        result = self.controller.check_compliance(mock_sddc_manager_context, self.control_desired_value)

        # Assert expected results.
        assert result == expected_result

    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('ssl.DER_cert_to_PEM_cert', MagicMock())
    @patch('ssl.SSLSocket.getpeercert', MagicMock())
    @patch('ssl.SSLContext.wrap_socket', MagicMock())
    @patch('socket.create_connection', MagicMock())
    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context,
                        mock_load_pem_x509_certificate):

        expected_error = ["Unable to fetch issuer details from cert"]
        cert = {}

        mock_sddc_manager_rest_client.get_helper.return_value = self.desired_api_response
        mock_sddc_manager_context.mock_sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_cert_obj = MagicMock()

        # Set the return value for issuer.rfc4514_string()
        mock_cert_obj.issuer.rfc4514_string.return_value = cert

        # Set the return value for x509.load_pem_x509_certificate()
        mock_load_pem_x509_certificate.return_value = mock_cert_obj

        # Call Controller.
        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == {}
        assert errors == expected_error

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_connection_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        expected_error = ["Unable to fetch issuer details from cert"]

        mock_sddc_manager_rest_client.get_helper.return_value = self.desired_api_response
        mock_sddc_manager_context.mock_sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Call Controller.
        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == {}
        assert errors == expected_error

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE]}

        # Call Controller.
        status, errors = self.controller.set(mock_sddc_manager_context, self.control_desired_value)

        # Assert expected results.
        assert errors == expected_result[consts.ERRORS]
        assert status == expected_result[consts.STATUS]

    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('ssl.DER_cert_to_PEM_cert', MagicMock())
    @patch('ssl.SSLSocket.getpeercert', MagicMock())
    @patch('ssl.SSLContext.wrap_socket', MagicMock())
    @patch('socket.create_connection', MagicMock())
    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context,
                                     mock_load_pem_x509_certificate):

        expected_failed_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ['Unable to fetch issuer details from cert']
        }
        error = "Unable to fetch issuer details from cert"

        mock_sddc_manager_rest_client.get_helper.return_value = self.desired_api_response
        mock_sddc_manager_context.mock_sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_load_pem_x509_certificate.return_value = Exception(error)

        # Call Controller.
        result = self.controller.check_compliance(mock_sddc_manager_context, self.control_desired_value)
        assert result == expected_failed_result
