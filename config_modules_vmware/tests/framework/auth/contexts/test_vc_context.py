# Copyright 2024 Broadcom. All Rights Reserved.
from mock import patch

from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext


class TestVcenterContext:

    def setup_method(self):
        self.hostname = "vc_hostname"
        self.username = "vc_username"
        self.password = "vc_password"
        self.ssl_thumbprint = "ssl_thumbprint"
        self.saml_token = "saml_token"
        self.verify_ssl = False
        self.context = VcenterContext(hostname=self.hostname, username=self.username, password=self.password,
                                      ssl_thumbprint=self.ssl_thumbprint, saml_token=self.saml_token,
                                      verify_ssl=self.verify_ssl)

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext.__enter__')
    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext.__exit__')
    def test_vc_context_initialization(self, mock_exit, mock_enter):
        assert self.context.hostname == self.hostname
        with self.context:
            assert mock_enter.call_count == 1
        assert mock_exit.call_count == 1

    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient.connect')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient.disconnect')
    def test_vc_context_vmomi_client(self, mock_vc_vmomi_client_disconnect, mock_vc_vmomi_client_connect):
        mock_vc_vmomi_client_connect.return_value = None
        mock_vc_vmomi_client_disconnect.return_value = None
        with self.context:
            vc_vmomi_client = self.context.vc_vmomi_client()
            assert vc_vmomi_client.vc_name == self.hostname
            assert vc_vmomi_client.user == self.username
            assert vc_vmomi_client.pwd == self.password
            assert vc_vmomi_client.ssl_thumbprint == self.ssl_thumbprint
            assert vc_vmomi_client.saml_token == self.saml_token
            assert vc_vmomi_client.verify_ssl == self.verify_ssl
        assert mock_vc_vmomi_client_disconnect.call_count == 1

    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient.__init__')
    def test_vc_context_rest_client(self, mock_rest_client):
        # mocking as the variables are not stored inside the rest client
        mock_rest_client.return_value = None
        with self.context:
            assert self.context.vc_rest_client() is not None
            args = mock_rest_client.call_args.args
            assert self.hostname in args
            assert self.username in args
            assert self.password in args
            assert self.ssl_thumbprint in args
            assert self.verify_ssl in args
        assert self.context._vc_rest_client is None

    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient.connect')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient.disconnect')
    def test_vc_vmomi_sso_client(self, mock_vc_vmomi_sso_client_disconnect, mock_vc_vmomi_sso_client_connect):
        mock_vc_vmomi_sso_client_connect.return_value = None
        mock_vc_vmomi_sso_client_disconnect.return_value = None
        with self.context:
            vc_vmomi_sso_client = self.context.vc_vmomi_sso_client()
            assert vc_vmomi_sso_client.vc_name == self.hostname
            assert vc_vmomi_sso_client.user == self.username
            assert vc_vmomi_sso_client.pwd == self.password
            assert vc_vmomi_sso_client.ssl_thumbprint == self.ssl_thumbprint
            assert vc_vmomi_sso_client.verify_ssl == self.verify_ssl
        assert mock_vc_vmomi_sso_client_disconnect.call_count == 1

    @patch('config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient.connect')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient.set_ssl_context')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient.disconnect')
    def test_vc_vsan_vmomi_client(self, mock_vc_vsan_vmomi_client_disconnect, mock_vc_vsan_vmomi_client_set_ssl_context, mock_vc_vsan_vmomi_client_connect):
        mock_vc_vsan_vmomi_client_set_ssl_context.return_value = None
        mock_vc_vsan_vmomi_client_connect.return_value = None
        mock_vc_vsan_vmomi_client_disconnect.return_value = None
        with self.context:
            vc_vsan_vmomi_client = self.context.vc_vsan_vmomi_client()
            assert vc_vsan_vmomi_client.vc_name == self.hostname
            assert vc_vsan_vmomi_client.user == self.username
            assert vc_vsan_vmomi_client.pwd == self.password
            assert vc_vsan_vmomi_client.ssl_thumbprint == self.ssl_thumbprint
            assert vc_vsan_vmomi_client.verify_ssl == self.verify_ssl
        assert mock_vc_vsan_vmomi_client_disconnect.call_count == 1

    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient.get_vcsa_version')
    def test_vc_context_product_version(self, mock_rest_client):
        product_version = "8.0.3"
        mock_rest_client.return_value = product_version
        assert self.context.product_version == product_version
