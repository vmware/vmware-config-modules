# Copyright 2024 Broadcom. All Rights Reserved.
from mock import patch

from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext


class TestSDDCManagerContext:

    def setup_method(self):
        self.hostname = "sddc_mgr_hostname"
        self.username = "sddc_mgr_username"
        self.password = "sddc_mgr_password"
        self.ssl_thumbprint = "ssl_thumbprint"
        self.saml_token = "saml_token"
        self.verify_ssl = False
        self.context = SDDCManagerContext(hostname=self.hostname, username=self.username, password=self.password,
                                          ssl_thumbprint=self.ssl_thumbprint, verify_ssl=self.verify_ssl)

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext.__enter__')
    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext.__exit__')
    def test_sddc_manager_context_initialization(self, mock_exit, mock_enter):
        assert self.context.username == self.username
        assert self.context.password == self.password
        assert self.context.hostname == self.hostname
        with self.context:
            assert mock_enter.call_count == 1
        assert mock_exit.call_count == 1

    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient'
           '.__init__')
    def test_sddc_manager_context_rest_client(self, mock_rest_client):
        # mocking as the variables are not stored inside the rest client
        mock_rest_client.return_value = None
        with self.context:
            assert self.context.sddc_manager_rest_client() is not None
            args = mock_rest_client.call_args.args
            assert self.hostname in args
            assert self.username in args
            assert self.password in args
            assert self.ssl_thumbprint in args
            assert self.verify_ssl in args
        assert self.context._sddc_manager_rest_client is None

    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient'
           '.get_helper')
    def test_sddc_manager_context_product_version(self, mock_rest_client):
        product_version = "5.0"
        mock_rest_client.return_value = {"elements": [{"version": product_version}]}
        assert self.context.product_version == product_version
