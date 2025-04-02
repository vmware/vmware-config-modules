from mock import patch

from config_modules_vmware.controllers.vcenter.tls_version_config import RECONFIGURE_VC_TLS_SCRIPT_PATH
from config_modules_vmware.controllers.vcenter.tls_version_config import SCAN_COMMAND
from config_modules_vmware.controllers.vcenter.tls_version_config import TlsVersion
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestTlsVersion:
    def setup_method(self):
        self.controller = TlsVersion()
        self.non_compliant_scan_std_err = """
            vCenter Transport Layer Security reconfigurator, version=7.0.3, build=9775800
            For more information refer to the following article: https://kb.vmware.com/kb/2147469
            Log file: "/var/log/vmware/vSphere-TlsReconfigurator/VcTlsReconfigurator.log".
            ==================== Scanning vCenter Server TLS endpoints =====================
            +---------------------+-------------------+----------------+
            | Service Name        | TLS Endpoint Port | TLS Version(s) |
            +---------------------+-------------------+----------------+
            | service1            | 1514              | TLSv1.2        |
            | service2            | 1514              | TLSv1.1 TLSv1.2|
            | service3            | 443               | TLSv1.2        |
            | service4            | 1                 | NOT RUNNING    |
            | service5            | 12                | TLSv1.1        |
            | service6            | 15                | TLSv1.1        |
            +---------------------+-------------------+----------------+
        """

        self.non_compliant_shell_cmd_return_val = ("", self.non_compliant_scan_std_err, 0)

        self.compliant_scan_std_err = """
            vCenter Transport Layer Security reconfigurator, version=7.0.3, build=9775800
            For more information refer to the following article: https://kb.vmware.com/kb/2147469
            Log file: "/var/log/vmware/vSphere-TlsReconfigurator/VcTlsReconfigurator.log".
            ==================== Scanning vCenter Server TLS endpoints =====================
            +---------------------+-------------------+----------------+
            | Service Name        | TLS Endpoint Port | TLS Version(s) |
            +---------------------+-------------------+----------------+
            | service1            | 1514              | TLSv1.2        |
            | service2            | 1514              | TLSv1.2        |
            | service3            | 443               | TLSv1.2        |
            | service4            | 1                 | NOT RUNNING    |
            | service5            | 12                | TLSv1.2        |
            | service6            | 15                | TLSv1.2        |
            +---------------------+-------------------+----------------+
        """

        self.compliant_shell_cmd_return_val = ("", self.compliant_scan_std_err, 0)
        self.failed_result = None
        command = "{} {}".format(RECONFIGURE_VC_TLS_SCRIPT_PATH, SCAN_COMMAND)
        self.cmd_failure_msg = f"Exception running shell command {command}"
        self.shell_cmd_set_return_failure = ("", "", 1)

        self.desired_values_only_global = {
            consts.GLOBAL: ['TLSv1.2']
        }

        self.desired_values_global_with_services = {
            consts.GLOBAL: ['TLSv1.2'],
            'service2': ['TLSv1.1', 'TLSv1.2']
        }

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_success(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.return_value = self.non_compliant_shell_cmd_return_val
        result, errors = self.controller.get(mock_vc_context)

        expected_current_value = {
            "service1": ['TLSv1.2'],
            "service2": ['TLSv1.1', 'TLSv1.2'],
            "service3": ['TLSv1.2'],
            "service4": ['NOT RUNNING'],
            "service5": ['TLSv1.1'],
            "service6": ['TLSv1.1'],
        }
        assert result == expected_current_value

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_failed(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.side_effect = Exception(f"{self.cmd_failure_msg}")
        _, errors = self.controller.get(mock_vc_context)

        expected_errors = [self.cmd_failure_msg]
        assert errors == expected_errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val
        status, errors = self.controller.set(mock_vc_context, self.desired_values_only_global)

        # Assert expected results.
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_failed(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.side_effect = Exception(f"{self.cmd_failure_msg}")
        _, errors = self.controller.set(mock_vc_context, self.desired_values_only_global)

        expected_errors = [self.cmd_failure_msg]
        assert errors == expected_errors

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_failed(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.side_effect = Exception(f"{self.cmd_failure_msg}")
        result = self.controller.check_compliance(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: [self.cmd_failure_msg]
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_non_compliant_only_global(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.return_value = self.non_compliant_shell_cmd_return_val
        result = self.controller.check_compliance(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: {
                "service2": ['TLSv1.1', 'TLSv1.2'],
                "service5": ['TLSv1.1'],
                "service6": ['TLSv1.1']
            },
            consts.DESIRED: {
                "service2": ['TLSv1.2'],
                "service5": ['TLSv1.2'],
                "service6": ['TLSv1.2']
            }
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_non_compliant_global_with_services(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        non_compliant_scan_std_err = """
            vCenter Transport Layer Security reconfigurator, version=7.0.3, build=9775800
            For more information refer to the following article: https://kb.vmware.com/kb/2147469
            Log file: "/var/log/vmware/vSphere-TlsReconfigurator/VcTlsReconfigurator.log".
            ==================== Scanning vCenter Server TLS endpoints =====================
            +---------------------+-------------------+----------------+
            | Service Name        | TLS Endpoint Port | TLS Version(s) |
            +---------------------+-------------------+----------------+
            | service1            | 1514              | TLSv1.2        |
            | service2            | 1514              | TLSv1.0 TLSv1.2|
            | service3            | 443               | TLSv1.2        |
            | service4            | 1                 | NOT RUNNING    |
            | service5            | 12                | TLSv1.1        |
            | service6            | 15                | TLSv1.1        |
            +---------------------+-------------------+----------------+
        """
        compliant_shell_cmd_return_val = ("", non_compliant_scan_std_err, 0)
        mock_execute_shell_cmd.return_value = compliant_shell_cmd_return_val
        result = self.controller.check_compliance(mock_vc_context, self.desired_values_global_with_services)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: {
                "service2": ['TLSv1.0', 'TLSv1.2'],
                "service5": ['TLSv1.1'],
                "service6": ['TLSv1.1']
            },
            consts.DESIRED: {
                "service2": ['TLSv1.1', 'TLSv1.2'],
                "service5": ['TLSv1.2'],
                "service6": ['TLSv1.2']
            }
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_success_global_with_services(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        non_compliant_scan_std_err = """
            vCenter Transport Layer Security reconfigurator, version=7.0.3, build=9775800
            For more information refer to the following article: https://kb.vmware.com/kb/2147469
            Log file: "/var/log/vmware/vSphere-TlsReconfigurator/VcTlsReconfigurator.log".
            ==================== Scanning vCenter Server TLS endpoints =====================
            +---------------------+-------------------+----------------+
            | Service Name        | TLS Endpoint Port | TLS Version(s) |
            +---------------------+-------------------+----------------+
            | service1            | 1514              | TLSv1.2        |
            | service2            | 1514              | TLSv1.0 TLSv1.2|
            | service3            | 443               | TLSv1.2        |
            | service4            | 1                 | NOT RUNNING    |
            | service5            | 12                | TLSv1.1        |
            | service6            | 15                | TLSv1.1        |
            +---------------------+-------------------+----------------+
        """

        non_compliant_shell_cmd_return_val = ("", non_compliant_scan_std_err, 0)

        compliant_scan_std_err = """
            vCenter Transport Layer Security reconfigurator, version=7.0.3, build=9775800
            For more information refer to the following article: https://kb.vmware.com/kb/2147469
            Log file: "/var/log/vmware/vSphere-TlsReconfigurator/VcTlsReconfigurator.log".
            ==================== Scanning vCenter Server TLS endpoints =====================
            +---------------------+-------------------+----------------+
            | Service Name        | TLS Endpoint Port | TLS Version(s) |
            +---------------------+-------------------+----------------+
            | service1            | 1514              | TLSv1.2        |
            | service2            | 1514              | TLSv1.1 TLSv1.2|
            | service3            | 443               | TLSv1.2        |
            | service4            | 1                 | NOT RUNNING    |
            | service5            | 12                | TLSv1.2        |
            | service6            | 15                | TLSv1.2        |
            +---------------------+-------------------+----------------+
        """

        compliant_shell_cmd_return_val = ("", compliant_scan_std_err, 0)
        mock_execute_shell_cmd.side_effect = [non_compliant_shell_cmd_return_val,
                                              compliant_shell_cmd_return_val,
                                              compliant_shell_cmd_return_val]
        result = self.controller.remediate(mock_vc_context, self.desired_values_global_with_services)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: {
                "service2": ['TLSv1.0', 'TLSv1.2'],
                "service5": ['TLSv1.1'],
                "service6": ['TLSv1.1']
            },
            consts.NEW: {
                "service2": ['TLSv1.1', 'TLSv1.2'],
                "service5": ['TLSv1.2'],
                "service6": ['TLSv1.2']
            }
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_compliant(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val
        result = self.controller.check_compliance(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_success(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.side_effect = [self.non_compliant_shell_cmd_return_val,
                                              self.compliant_shell_cmd_return_val]
        result = self.controller.remediate(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: {
                "service2": ['TLSv1.1', 'TLSv1.2'],
                "service5": ['TLSv1.1'],
                "service6": ['TLSv1.1']
            },
            consts.NEW: {
                "service2": ['TLSv1.2'],
                "service5": ['TLSv1.2'],
                "service6": ['TLSv1.2']
            }
        }
        assert result == expected_result


    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_for_already_compliant_config(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.return_value = self.compliant_shell_cmd_return_val
        result = self.controller.remediate(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: ['Control already compliant']
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediate_failed_on_compliance_check(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.side_effect = Exception(f"{self.cmd_failure_msg}")
        result = self.controller.remediate(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: RemediateStatus.FAILED,
            consts.ERRORS: [self.cmd_failure_msg]
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_unknown_services(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.return_value = self.non_compliant_shell_cmd_return_val
        desired_values_unknown_services = {
            consts.GLOBAL: ['TLSv1.2'],
            'service_unknown': ['TLSv1.1', 'TLSv1.2']
        }
        result = self.controller.check_compliance(mock_vc_context, desired_values_unknown_services)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ["Service not found. Failed to get the TLS version for service 'service_unknown'."]
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_services_not_applicable(self, mock_execute_shell_cmd, mock_vc_context):
        mock_vc_context.product_version = "7.0.0.00100"
        mock_execute_shell_cmd.return_value = self.non_compliant_shell_cmd_return_val
        desired_values_unknown_services = {
            consts.GLOBAL: ['TLSv1.2'],
            'VC Storage Clients': ['TLSv1.1', 'TLSv1.2']
        }
        result = self.controller.check_compliance(mock_vc_context, desired_values_unknown_services)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ["Can not override service 'VC Storage Clients' in desired spec. "
                            "Desired spec needs to be fixed."]
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_for_8_x_vc(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_context.product_version = "8.0.2.00100"
        mock_vc_rest_client.get_base_url.return_value = "http://localhost"
        mock_vc_rest_client.get_helper.return_value = {"protocol_versions": [{"version": "tlsv1_2"}]}
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.get(mock_vc_context)
        expected_result = ({"global": ["TLSv1.2"]}, [])
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_set_skipped_for_versions_not_applicable(self, mock_vc_context):
        mock_vc_context.product_version = "8.0.2.00100"
        result = self.controller.set(mock_vc_context, self.desired_values_only_global)
        expected_result = (RemediateStatus.SKIPPED, [consts.CONTROL_NOT_AUTOMATED])
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_for_8_x_vc(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_context.product_version = "8.0.2.00100"
        mock_vc_rest_client.get_base_url.return_value = "http://localhost"
        mock_vc_rest_client.get_helper.side_effect = [{"profile": "COMPATIBLE"},
                                                      {"protocol_versions": [{"version": "tlsv1_2"}]}]
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result = self.controller.check_compliance(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_remediate_for_versions_not_applicable(self, mock_vc_context):
        mock_vc_context.product_version = "8.0.2.00100"
        result = self.controller.remediate(mock_vc_context, self.desired_values_only_global)
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.CONTROL_NOT_AUTOMATED],
            consts.DESIRED: self.desired_values_only_global,
            consts.CURRENT: {"global": []}
        }
        assert result == expected_result
