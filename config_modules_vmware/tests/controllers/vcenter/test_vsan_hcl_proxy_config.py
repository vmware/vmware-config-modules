from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.vsan_hcl_proxy_config import VSANHCLProxyConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestVSANHCLProxyConfig:
    def setup_method(self):
        self.controller = VSANHCLProxyConfig()
        self.non_compliant_cluster_configs = [
            {
                "host": "time.vmware.com",
                "port": 100,
                "user": "proxy_user_1",
                "internet_access_enabled": False,
                "cluster_name": "sfo-m01-cl01",
            },
            {
                "host": "abc.vmware.com",
                "port": 50,
                "user": "proxy_user_2",
                "internet_access_enabled": False,
                "cluster_name": "sfo-m01-cl02",
            },
            {
                "host": "time.vmware.com",
                "port": 60,
                "user": "proxy_user_3",
                "internet_access_enabled": False,
                "cluster_name": "sfo-m01-cl03",
            },
        ]
        self.compliant_cluster_proxy_config = {
            "host": "hcl.vmware.com",
            "port": 80,
            "user": "proxy_user",
            "internet_access_enabled": True,
        }
        self.compliant_cluster_configs = [
            {
                "host": "hcl.vmware.com",
                "port": 80,
                "user": "proxy_user",
                "internet_access_enabled": True,
                "cluster_name": "sfo-m01-cl01",
            },
            {
                "host": "hcl.vmware.com",
                "port": 80,
                "user": "proxy_user",
                "internet_access_enabled": True,
                "cluster_name": "sfo-m01-cl02",
            },
            {
                "host": "hcl.vmware.com",
                "port": 80,
                "user": "proxy_user",
                "internet_access_enabled": True,
                "cluster_name": "sfo-m01-cl03",
            },
        ]
        self.all_vsan_enabled_mock_cluster_refs = \
            self.create_mock_objs_all_vsan_clusters(self.compliant_cluster_configs)

    def create_vsan_cluster_proxy_mock_obj(self, proxy_spec):
        """
        Create mock object for vSAN cluster proxy
        :param proxy_spec:
        :return:
        """
        vsan_proxy_mock_object = MagicMock()
        vsan_proxy_mock_object.vsanTelemetryProxy = vim.cluster.VsanClusterTelemetryProxyConfig()
        vsan_proxy_mock_object.vsanTelemetryProxy.host = proxy_spec.get("host")
        vsan_proxy_mock_object.vsanTelemetryProxy.port = proxy_spec.get("port")
        vsan_proxy_mock_object.vsanTelemetryProxy.user = proxy_spec.get("user")
        vsan_proxy_mock_object.vsanTelemetryProxy.password = proxy_spec.get("password")
        return vsan_proxy_mock_object

    def create_mock_objs_all_vsan_clusters(self, cluster_proxy_configs):
        """
        Create pyvmomi like mock object for all clusters
        :param cluster_proxy_configs:
        :return:
        """
        all_vsan_cluster_refs = []
        for cluster_proxy_config in cluster_proxy_configs:
            cluster_ref = MagicMock()
            cluster_ref.name = cluster_proxy_config.get("cluster_name")
            all_vsan_cluster_refs.append(cluster_ref)
        return all_vsan_cluster_refs

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_get_success(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = [
            self.compliant_cluster_configs[0],
            self.compliant_cluster_configs[1],
            self.compliant_cluster_configs[2],
        ]
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_cluster_configs
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_get_failed(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get vSAN cluster proxy config")

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = expected_error
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_set_success(self, mock_vc_vsan_vmomi_client, mock_vc_context):

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = [
            self.compliant_cluster_configs[0],
            self.compliant_cluster_configs[1],
            self.compliant_cluster_configs[2],
        ]
        mock_vc_vsan_vmomi_client.get_vsan_config_by_key_for_cluster.return_value = vim.option.OptionValue(
            key="enableinternetaccess", value=self.compliant_cluster_proxy_config["internet_access_enabled"]
        )
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_set_failed(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to set vSAN cluster proxy config")

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = expected_error
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = [
            self.compliant_cluster_configs[0],
            self.compliant_cluster_configs[1],
            self.compliant_cluster_configs[2],
        ]
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_cluster_configs,
            consts.DESIRED: self.compliant_cluster_proxy_config,
        }

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = [
            self.non_compliant_cluster_configs[0],
            self.non_compliant_cluster_configs[1],
            self.non_compliant_cluster_configs[2],
        ]
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = expected_error
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_remediate_skipped_already_desired(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ['Control already compliant']}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = [
            self.compliant_cluster_configs[0],
            self.compliant_cluster_configs[1],
            self.compliant_cluster_configs[2],
        ]
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_remediate_success(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: self.non_compliant_cluster_configs,
            consts.NEW: self.compliant_cluster_proxy_config,
        }

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = [
            self.non_compliant_cluster_configs[0],
            self.non_compliant_cluster_configs[1],
            self.non_compliant_cluster_configs[2],
        ]
        mock_vc_vsan_vmomi_client.get_vsan_cluster_health_config_for_cluster.side_effect = [
            self.create_vsan_cluster_proxy_mock_obj(self.non_compliant_cluster_configs[0]),
            self.create_vsan_cluster_proxy_mock_obj(self.non_compliant_cluster_configs[1]),
            self.create_vsan_cluster_proxy_mock_obj(self.non_compliant_cluster_configs[2]),
        ]
        mock_vc_vsan_vmomi_client.get_vsan_config_by_key_for_cluster.side_effect = [
            vim.option.OptionValue(
                key="enableinternetaccess", value=self.non_compliant_cluster_configs[0]["internet_access_enabled"]
            ),
            vim.option.OptionValue(
                key="enableinternetaccess", value=self.non_compliant_cluster_configs[1]["internet_access_enabled"]
            ),
            vim.option.OptionValue(
                key="enableinternetaccess", value=self.non_compliant_cluster_configs[2]["internet_access_enabled"]
            ),
        ]
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_remediate_get_failed(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_error = Exception("Get exception while remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.side_effect = expected_error
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    def test_remediate_set_failed(self, mock_vc_vsan_vmomi_client, mock_vc_context):
        expected_error = Exception("Setting cluster proxy config failed")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vsan_vmomi_client.get_vsan_health_system.side_effect = expected_error
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster.side_effect = [
            self.non_compliant_cluster_configs[0],
            self.non_compliant_cluster_configs[1],
            self.non_compliant_cluster_configs[2],
        ]
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_cluster_proxy_config)
        assert result == expected_result
