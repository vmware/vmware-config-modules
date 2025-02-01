from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.dvs_pg_netflow_config import DvsPortGroupNetflowConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestDvsPortGroupNetflowConfig:
    def setup_method(self):
        self.controller = DvsPortGroupNetflowConfig()
        self.compliant_dvs = [
            {"switch_name": "SwitchA", "ipfix_collector_ip": ""},
            {"switch_name": "SwitchB", "ipfix_collector_ip": ""},
            {"switch_name": "SwitchC", "ipfix_collector_ip": ""},
        ]
        self.non_compliant_dvs = [
            {"switch_name": "SwitchA", "ipfix_collector_ip": "10.0.0.250"},
            {"switch_name": "SwitchB", "ipfix_collector_ip": "10.0.0.250"},
            {"switch_name": "SwitchC", "ipfix_collector_ip": "10.0.0.250"},
        ]
        self.compliant_dv_pgs = [
            {"port_group_name": "dv_pg_PortGroup3", "ipfix_enabled": False},
            {"port_group_name": "dv_pg_PortGroup1", "ipfix_enabled": False},
            {"port_group_name": "dv_pg_PortGroup2", "ipfix_enabled": False},
        ]
        self.non_compliant_dv_pgs = [
            {"port_group_name": "dv_pg_PortGroup3", "ipfix_enabled": True},
            {"port_group_name": "dv_pg_PortGroup1", "ipfix_enabled": True},
            {"port_group_name": "dv_pg_PortGroup2", "ipfix_enabled": True},
        ]
        self.compliant_value = {
            "__GLOBAL__": {
                "ipfix_collector_ip": "",
                "ipfix_enabled": False
            }
        }
        self.non_compliant_value = {
            "switch_config": [
                {
                    'ipfix_collector_ip': '10.0.0.250',
                    'switch_name': 'SwitchA',
                },
                {
                    'ipfix_collector_ip': '10.0.0.250',
                    'switch_name': 'SwitchB',
                },
                {
                    'ipfix_collector_ip': '10.0.0.250',
                    'switch_name': 'SwitchC',
                },
            ],
            "portgroup_config": [
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup3',
                    'switch_name': 'SwitchA',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup1',
                    'switch_name': 'SwitchA',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup2',
                    'switch_name': 'SwitchA',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup3',
                    'switch_name': 'SwitchB',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup1',
                    'switch_name': 'SwitchB',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup2',
                    'switch_name': 'SwitchB',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup3',
                    'switch_name': 'SwitchC',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup1',
                    'switch_name': 'SwitchC',
                },
                {
                    'ipfix_enabled': True,
                    'port_group_name': 'dv_pg_PortGroup2',
                    'switch_name': 'SwitchC',
                },
            ]
        }
        self.all_ipfix_configs = {
            "switch_config": [
                {
                    'switch_name': 'SwitchA',
                    'ipfix_collector_ip': '',
                },
                {
                    'switch_name': 'SwitchB',
                    'ipfix_collector_ip': '',
                },
                {
                    'switch_name': 'SwitchC',
                    'ipfix_collector_ip': '',
                }
            ],
            'portgroup_config': [
                {
                    'ipfix_enabled': False,
                    'port_group_name': 'dv_pg_PortGroup3',
                    'switch_name': 'SwitchA',
                },
                {
                    'ipfix_enabled': False,
                    'port_group_name': 'dv_pg_PortGroup1',
                    'switch_name': 'SwitchA',
                },
                {
                    'ipfix_enabled': False,
                    'port_group_name': 'dv_pg_PortGroup2',
                    'switch_name': 'SwitchA',
                },
                {
                   'ipfix_enabled': False,
                   'port_group_name': 'dv_pg_PortGroup3',
                   'switch_name': 'SwitchB',
                },
                {
                   'ipfix_enabled': False,
                   'port_group_name': 'dv_pg_PortGroup1',
                   'switch_name': 'SwitchB',
                },
                {
                    'ipfix_enabled': False,
                    'port_group_name': 'dv_pg_PortGroup2',
                    'switch_name': 'SwitchB',
                },
                {
                    'ipfix_enabled': False,
                    'port_group_name': 'dv_pg_PortGroup3',
                    'switch_name': 'SwitchC',
                },
                {
                    'ipfix_enabled': False,
                    'port_group_name': 'dv_pg_PortGroup1',
                    'switch_name': 'SwitchC',
                },
                {
                    'ipfix_enabled': False,
                    'port_group_name': 'dv_pg_PortGroup2',
                    'switch_name': 'SwitchC',
                },
            ],
        }
        # Pyvmomi type MagicMock objects
        compliant_pg_obj = [
            self.get_dv_port_group_mock_obj(pg_spec) for pg_spec in self.compliant_dv_pgs
        ]
        self.compliant_dvs_pyvmomi_mocks = [
            self.create_dv_switch_mock_obj(dvs_spec, compliant_pg_obj) for dvs_spec in self.compliant_dvs
        ]
        non_compliant_pg_obj = [
            self.get_dv_port_group_mock_obj(pg_spec) for pg_spec in self.non_compliant_dv_pgs
        ]
        self.non_compliant_dvs_pyvmomi_mocks = [
            self.create_dv_switch_mock_obj(dvs_spec, non_compliant_pg_obj) for dvs_spec in self.non_compliant_dvs
        ]

        # Bad mock to induce error
        bad_pg_obj = [
            self.get_dv_port_group_mock_obj(pg_spec, bad_mock=True) for pg_spec in self.non_compliant_dv_pgs
        ]
        self.dv_pg_mock_pyvmomi_bad_object = [
            self.create_dv_switch_mock_obj(dvs_spec, bad_pg_obj, bad_mock=True) for dvs_spec in self.non_compliant_dvs
        ]

    def get_dv_port_group_mock_obj(self, pg_spec, bad_mock=False):
        """
        Create mock object for DV port group based on port group spec
        :param pg_spec:
        :param bad_mock:
        :return:
        """

        dv_pg_mock = MagicMock()
        dv_pg_mock.name = pg_spec.get("port_group_name")
        dv_pg_mock.config = MagicMock()
        dv_pg_mock.config.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
        if not bad_mock:
            dv_pg_mock.config.configVersion = "24"
        dv_pg_mock.config.defaultPortConfig.ipfixEnabled = vim.BoolPolicy()
        dv_pg_mock.config.defaultPortConfig.ipfixEnabled.value = pg_spec.get("ipfix_enabled")
        setattr(dv_pg_mock, "ReconfigureDVPortgroup_Task", MagicMock(return_value=True))
        return dv_pg_mock

    def create_dv_switch_mock_obj(self, dv_spec, pg_obj, bad_mock=False):
        dvs_mock = MagicMock()
        dvs_mock.name = dv_spec.get("switch_name")
        dvs_mock.config = MagicMock()
        dvs_mock.config.ipfixConfig = MagicMock()
        dvs_mock.config.ipfixConfig.collectorIpAddress = dv_spec.get("ipfix_collector_ip")
        if not bad_mock:
            dvs_mock.config.configVersion = "24"
        setattr(dvs_mock, "ReconfigureDvs_Task", MagicMock(return_value=True))
        dvs_mock.portgroup = pg_obj
        return dvs_mock

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = self.all_ipfix_configs
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dvs_pyvmomi_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.all_ipfix_configs
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get DV PG config")

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == {}
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.compliant_dvs_pyvmomi_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to set Forged transmits policy")

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dvs_pyvmomi_mocks
        mock_vc_vmomi_client.wait_for_task.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        expected_get_object_result = self.compliant_dvs_pyvmomi_mocks
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_get_object_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = self.controller._get_non_compliant_configs(
            self.non_compliant_value,
            self.compliant_value)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: desired_configs,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.non_compliant_dvs_pyvmomi_mocks
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_skipped_already_desired(self, mock_vc_vmomi_client, mock_vc_context):
        expected_get_object_result = self.compliant_dvs_pyvmomi_mocks
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_get_object_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = self.controller._get_non_compliant_configs(
            self.non_compliant_value,
            self.compliant_value)
        current_value = self.non_compliant_dvs_pyvmomi_mocks
        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: desired_configs,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = current_value
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Get exception while remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception('For "configVersion" expected type str, but got MagicMock')
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.dv_pg_mock_pyvmomi_bad_object
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
