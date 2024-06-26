import fcntl

from mock import call
from mock import MagicMock
from mock import mock_open
from mock import patch

from config_modules_vmware.controllers.sddc_manager.proxy_config import ProxyConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import SDDC_MANAGER_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

VCF_4_5_X_X_VERSION = "4.5.0.0"
VCF_4_X_VERSION = "4.4.1.1"

class TestProxyConfig:
    def setup_method(self):
        self.controller = ProxyConfig()

        # SDDC API Base url
        self.mock_sddc_host_name = "mock-sddc.eng.vmware.com"
        self.sddc_base_url = SDDC_MANAGER_API_BASE.format(self.mock_sddc_host_name)
        # Desired
        self.compliant_values = {"proxy_enabled": False, "host": "10.0.0.250", "port": 3128}
        self.non_compliant_values = {"proxy_enabled": True, "host": "10.0.0.250", "port": 3128}
        self.get_helper_values = {"isEnabled": False, "isConfigured": True, "host": "10.0.0.250", "port": 3128}
        self.get_helper_non_compliant_values = {"isEnabled": True, "host": "10.0.0.250", "port": 3128}
        self.put_helper_values = {"isEnabled": False, "isConfigured": True, "host": "10.0.0.250", "port": 3128}
        self.file_read_values = {"lcm.depot.adapter.proxyEnabled=false", "lcm.depot.adapter.proxyHost=10.0.0.250", "lcm.depot.adapter.proxyPort=3128"}
        self.file_write_values = {"lcm.depot.adapter.proxyEnabled=false", "lcm.depot.adapter.proxyHost=10.0.0.250", "lcm.depot.adapter.proxyPort=3128"}

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION
        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.compliant_values
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=false\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_get_success_file(self, mock_open, mock_sddc_manager_context):
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION
        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.compliant_values
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while retrieveing proxy config")
        mock_sddc_manager_rest_client.get_helper.side_effect = [expected_error, ""]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result, errors = self.controller.get(mock_sddc_manager_context)
        assert result == {}
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=false\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_get_failed_file(self, mock_open, mock_sddc_manager_context):
        expected_error = Exception("Exception while retrieveing proxy config")
        mock_open.side_effect = [expected_error, ""]
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION
        result, errors = self.controller.get(mock_sddc_manager_context)
        assert result == {}
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_success_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=false\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    @patch("fcntl.flock")
    def test_set_success_file1(self, mock_flock, mock_run_shell_cmd, mock_open, mock_sddc_manager_context):
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION
        mock_open.return_value.__dict__['fileno'] = lambda: 10
        mock_run_shell_cmd.return_value = ("", "", 0)
        mock_flock.return_value = None

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_failed_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Setting Proxy Config failed")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.patch_helper.side_effect = [expected_error, []]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=false\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_set_failed_file(self, mock_open, mock_sddc_manager_context):
        expected_error = Exception("Setting Proxy Config failed")
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION
        mock_open.side_effect = [expected_error, ""]

        result, errors = self.controller.set(mock_sddc_manager_context, self.compliant_values)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_compliant_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
                              consts.STATUS: ComplianceStatus.COMPLIANT,
                              consts.CURRENT: self.compliant_values,
                              consts.DESIRED: self.compliant_values
                          }

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=false\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_check_compliance_compliant_file(self, mock_open, mock_sddc_manager_context):
        expected_result = {
                              consts.STATUS: ComplianceStatus.COMPLIANT,
                              consts.CURRENT: self.compliant_values,
                              consts.DESIRED: self.compliant_values
                          }

        mock_sddc_manager_context.product_version = VCF_4_X_VERSION

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_non_compliant_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_values,
            consts.DESIRED: self.compliant_values
        }
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=true\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_check_compliance_non_compliant_file(self, mock_open, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_values,
            consts.DESIRED: self.compliant_values
        }
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Compliance check failed while fetching proxy config")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_sddc_manager_rest_client.get_helper.side_effect = [expected_error, []]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=true\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_check_compliance_failed_file(self, mock_open, mock_sddc_manager_context):
        expected_error = Exception("Compliance check failed while fetching proxy config")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_open.side_effect = [expected_error, ""]
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success_already_desired_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.get_helper_values]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=false\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_remediate_success_already_desired_file(self, mock_open, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_values,
                           consts.NEW: self.compliant_values}
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = [self.get_helper_non_compliant_values]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=true\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    @patch("fcntl.flock")
    def test_remediate_success_file(self, mock_flock, mock_run_shell_cmd, mock_open, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_values,
                           consts.NEW: self.compliant_values}
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION
        mock_run_shell_cmd.return_value = ("", "", 0)
        mock_open.return_value.__dict__['fileno'] = lambda: 10
        mock_flock.return_value = None

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_set_failed_api(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Remediation failed while setting proxy config")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.patch_helper.side_effect = [expected_error, []]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        mock_sddc_manager_context.product_version = VCF_4_5_X_X_VERSION

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)

        # Assert expected results.
        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch("builtins.open", new_callable=mock_open, read_data="lcm.depot.adapter.proxyEnabled=true\nlcm.depot.adapter.proxyHost=10.0.0.250\nlcm.depot.adapter.proxyPort=3128")
    def test_remediate_set_failed_api(self, mock_open, mock_sddc_manager_context):
        expected_error = Exception("Remediation failed while setting proxy config")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}
        mock_open.side_effect = [expected_error, ""]
        mock_sddc_manager_context.product_version = VCF_4_X_VERSION

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_values)

        # Assert expected results.
        assert result == expected_result
