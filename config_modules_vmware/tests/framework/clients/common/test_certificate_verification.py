# Copyright 2024 Broadcom. All Rights Reserved.
import ssl

import pytest
from mock import MagicMock
from mock import patch

from config_modules_vmware.framework.auth.ssl.cert_info import CertInfo
from config_modules_vmware.framework.clients.common import certificate_verification

class TestCertificateVerification:

    def setup_method(self):
        self.hostname = "vc_hostname"
        self.cert_str = "certificate string"
        cert_info = CertInfo(self.cert_str)
        self.cert_info_list = [cert_info]




    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_validate_all_certificates(self, mock_create_default_context, mock_create_connection):
        mocked_ssl_context_obj = MagicMock()
        mock_create_default_context.return_value = mocked_ssl_context_obj
        context, certificate = certificate_verification.validate_all_certificates(self.hostname, self.cert_info_list)
        assert context == mocked_ssl_context_obj

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_validate_all_certificates_bad_cert(self, mock_create_default_context, mock_create_connection):
        mocked_ssl_context_obj = MagicMock()
        expected_error = ssl.SSLCertVerificationError()
        expected_error.verify_message = "self-signed certificate"
        mocked_ssl_context_obj.wrap_socket.side_effect = expected_error
        mock_create_default_context.return_value = mocked_ssl_context_obj
        with pytest.raises(Exception) as e:
            certificate_verification.validate_all_certificates(self.hostname, self.cert_info_list)
        assert str(e.value) == "No valid certificate found"

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_validate_all_certificates_bad_hostname(self, mock_create_default_context, mock_create_connection):
        mocked_ssl_context_obj = MagicMock()
        expected_error = ssl.SSLCertVerificationError()
        expected_error.verify_message = "Hostname mismatch"
        mocked_ssl_context_obj.wrap_socket.side_effect = expected_error
        mock_create_default_context.return_value = mocked_ssl_context_obj
        with pytest.raises(Exception) as e:
            certificate_verification.validate_all_certificates(self.hostname, self.cert_info_list)
        assert str(e.value) == "No valid certificate found"

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_validate_all_certificates_no_verify_hostname(self, mock_create_default_context, mock_create_connection):
        mocked_ssl_context_obj_1 = MagicMock()
        mocked_ssl_context_obj_2 = MagicMock()
        expected_error = ssl.SSLCertVerificationError()
        expected_error.verify_message = "Hostname mismatch"
        mocked_ssl_context_obj_1.wrap_socket.side_effect = [expected_error, MagicMock()]
        mock_create_default_context.side_effect = [mocked_ssl_context_obj_1, mocked_ssl_context_obj_2]
        cert_info = CertInfo(self.cert_str, enforce_hostname_verification=False)
        cert_info_list = [cert_info]
        context, certificate = certificate_verification.validate_all_certificates(self.hostname, cert_info_list)
        assert context == mocked_ssl_context_obj_2

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_validate_all_certificates_expired(self, mock_create_default_context, mock_create_connection):
        mocked_ssl_context_obj = MagicMock()
        expected_error = ssl.SSLCertVerificationError()
        expected_error.verify_message = "certificate has expired"
        mocked_ssl_context_obj.wrap_socket.side_effect = expected_error
        mock_create_default_context.return_value = mocked_ssl_context_obj
        with pytest.raises(Exception) as e:
            certificate_verification.validate_all_certificates(self.hostname, self.cert_info_list)
        assert str(e.value) == "No valid certificate found"

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_validate_all_certificates_no_verify_date(self, mock_create_default_context, mock_create_connection):
        mocked_ssl_context_obj_1 = MagicMock()
        mocked_ssl_context_obj_2 = MagicMock()
        mocked_ssl_context_obj_3 = MagicMock()
        expected_error = ssl.SSLCertVerificationError()
        expected_error.verify_message = "certificate has expired"
        mocked_ssl_context_obj_1.wrap_socket.side_effect = expected_error
        mocked_ssl_context_obj_2.wrap_socket.side_effect = expected_error
        mock_create_default_context.side_effect = [mocked_ssl_context_obj_1, mocked_ssl_context_obj_2, mocked_ssl_context_obj_3]
        cert_info = CertInfo(self.cert_str, enforce_date_validity_checking=False)
        cert_info_list = [cert_info]
        context, certificate = certificate_verification.validate_all_certificates(self.hostname, cert_info_list)
        assert context == mocked_ssl_context_obj_3
