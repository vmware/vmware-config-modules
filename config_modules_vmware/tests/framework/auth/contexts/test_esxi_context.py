# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from mock import patch

from config_modules_vmware.framework.auth.contexts.esxi_context import EsxiContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext


class TestEsxiContext:

    def setup_method(self):
        self.hostname = "vc_hostname"
        self.username = "vc_username"
        self.password = "vc_password"
        self.ssl_thumbprint = "ssl_thumbprint"
        self.saml_token = "saml_token"
        self.product_version = "8.0.3"
        self.verify_ssl = False
        self.context = EsxiContext(vc_hostname=self.hostname, vc_username=self.username, vc_password=self.password,
                                   vc_ssl_thumbprint=self.ssl_thumbprint, vc_saml_token=self.saml_token,
                                   verify_ssl=self.verify_ssl)

    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient.connect')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient.disconnect')
    def test_esx_vc_context_vmomi_client(self, mock_vc_vmomi_client_disconnect, mock_vc_vmomi_client_connect):
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
    def test_esx_vc_context_rest_client(self, mock_rest_client):
        # mocking as the variables are not stored inside the rest client
        mock_rest_client.return_value = None
        with self.context:
            assert self.context.vc_rest_client() is not None
            args = mock_rest_client.call_args.args
            self.context._vc_rest_client._rest_client_session = None
            assert self.hostname in args
            assert self.username in args
            assert self.password in args
            assert self.ssl_thumbprint in args
            assert self.verify_ssl in args
        assert self.context._vc_rest_client is None

    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient.connect')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client.VcVmomiSSOClient.disconnect')
    def test_esx_vc_vmomi_sso_client(self, mock_vc_vmomi_sso_client_disconnect, mock_vc_vmomi_sso_client_connect):
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
    def test_esx_vc_vsan_vmomi_client(self, mock_vc_vsan_vmomi_client_disconnect,
                                      mock_vc_vsan_vmomi_client_set_ssl_context, mock_vc_vsan_vmomi_client_connect):
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

    def test_host_ref_version(self):
        mock_host_ref = MagicMock()
        version = "8.0.3"
        mock_host_ref.config.product.version = version
        host_context = HostContext(host_ref=mock_host_ref)
        assert host_context.product_version == version

    def test_host_ref_version_does_not_exist(self):
        mock_host_ref = MagicMock(spec=["a"])
        host_context = HostContext(host_ref=mock_host_ref)
        assert host_context.product_version is None
