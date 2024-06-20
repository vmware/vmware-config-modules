import json
from typing import List

from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import GLOBAL
from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import IS_DEDICATED_VLAN
from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import OVERRIDES
from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import PORT_GROUP_NAME
from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import SWITCH_NAME
from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import VLAN_INFO
from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import VMOTION
from config_modules_vmware.controllers.vcenter.vmotion_port_group_config import VMotionPortGroupConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestVMotionPortGroupConfig:
    def setup_method(self):
        self.controller = VMotionPortGroupConfig()
        self.desired_configs = {
            GLOBAL: {
                IS_DEDICATED_VLAN: True
            },
            OVERRIDES: [
                {
                    SWITCH_NAME: "Switch1",
                    PORT_GROUP_NAME: "PortGroup1",
                    VLAN_INFO: {"vlan_type": "VLAN", "vlan_id": 5}
                }
            ]
        }
        self.current_vmotion_portgroups = [
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup1",
                "is_dedicated_vlan": True,
                "ports": [
                    {
                        "host_name": "host1",
                        "device": "vmk1",
                        "tcp_ip_stack": "vmotion"
                    },
                    {
                        "host_name": "host2",
                        "device": "vmk2",
                        "tcp_ip_stack": "vmotion"
                    }
                ],
                "vlan_info": {
                    "vlan_type": "VLAN",
                    "vlan_id": 5
                }
            },
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup2",
                "is_dedicated_vlan": False,
                "ports": [
                    {
                        "host_name": "host1",
                        "device": "vmk3",
                        "tcp_ip_stack": "vmotion"
                    },
                    {
                        "host_name": "host2",
                        "device": "vmk4",
                        "tcp_ip_stack": "defaultTcpipStack"
                    }
                ],
                "vlan_info": {
                    "vlan_type": "VLAN trunking",
                    "vlan_range": [
                        {
                            "start": 10,
                            "end": 100
                        },
                        {
                            "start": 105,
                            "end": 110
                        },
                        {
                            "start": 200,
                            "end": 250
                        }
                    ]
                }
            }
        ]
        self.context_mock = MagicMock()
        self.dv_pgs = [
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup1",
                "vlan": 5,
            },
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup2",
                "vlan": ["10-100", "105-110", "200-250"],
            },
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup3",
                "pvlanId": 300,
            }
        ]

        dvs_1_mock = MagicMock()
        dvs_1_mock.portgroup = [self.get_dv_port_group_mock_obj(pg_spec) for pg_spec in self.dv_pgs]
        dvs_1_mock.name = 'Switch1'

        self.port_group_1_ports = [self.get_port_mock_obj(host_name='host1', device_name='vmk1'),
                                   self.get_port_mock_obj(host_name='host2', device_name='vmk2')]
        self.port_group_2_ports = [self.get_port_mock_obj(host_name='host1', device_name='vmk3'),
                                   self.get_port_mock_obj(host_name='host2', device_name='vmk4')]
        self.port_group_3_ports = [self.get_port_mock_obj(host_name='host1', device_name='vmk5')]
        self.ports = self.port_group_1_ports
        self.context_mock.vc_vmomi_client.return_value.get_objects_by_vimtype.return_value = [dvs_1_mock]

    def get_dv_port_group_mock_obj(self, pg_spec, create_bad_mock=False):
        """
        Create mock object for DV port group based on port group spec
        """
        dv_pg_mock = MagicMock()
        dv_pg_mock.name = pg_spec.get("port_group_name")
        dv_pg_mock.config = MagicMock()
        dv_pg_mock.config.uplink = False
        dv_pg_mock.config.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
        vlan_config = pg_spec.get("vlan")

        if isinstance(vlan_config, List):
            dv_pg_mock.config.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec()
            vlan_ranges = []
            for vlan in vlan_config:
                if "-" in vlan:
                    ranges = vlan.split("-")
                    start = int(ranges[0])
                    end = int(ranges[1])
                    vlan_range = vim.NumericRange(start=start, end=end)
                    vlan_ranges.append(vlan_range)
                else:
                    vlan_id = vim.NumericRange(start=int(vlan), end=int(vlan))
                    vlan_ranges.append(vlan_id)
            # for vlan in vlan_ranges:
            dv_pg_mock.config.defaultPortConfig.vlan.vlanId = vlan_ranges
        elif isinstance(vlan_config, int):
            dv_pg_mock.config.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
            dv_pg_mock.config.defaultPortConfig.vlan.vlanId = vlan_config
        else:
            pvt_vlan_config = pg_spec.get("pvlanId")
            dv_pg_mock.config.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.PvlanSpec()
            dv_pg_mock.config.defaultPortConfig.vlan.pvlanId = pvt_vlan_config

        if not create_bad_mock:
            dv_pg_mock.config.configVersion = "24"
        dv_pg_mock.config.distributedVirtualSwitch.name = pg_spec.get("switch_name")
        return dv_pg_mock

    def get_port_mock_obj(self, host_name, device_name):
        mock_port = vim.dvs.DistributedVirtualPort()
        connectee_mock = vim.dvs.PortConnectee()
        host_mock = MagicMock(spec=vim.HostSystem)
        host_mock.name = host_name
        connectee_mock.connectedEntity = host_mock
        connectee_mock.nicKey = device_name
        mock_port.connectee = connectee_mock
        return mock_port

    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config.VMotionPortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config.VMotionPortGroupConfig._get_port_tcp_ip_stack")
    def test_get_success(self, mock_get_tcp_ip_stack, mock_get_dv_ports):
        mock_get_tcp_ip_stack.side_effect = [VMOTION, VMOTION,
                                             VMOTION, 'defaultTcpipStack',
                                             'defaultTcpipStack']
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports]
        result, errors = self.controller.get(self.context_mock)
        assert result == self.current_vmotion_portgroups
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_get_failed(self, mock_vc_context):
        mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == ["Test exception"]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_set_skipped(self, mock_vc_context):
        status, errors = self.controller.set(mock_vc_context, self.desired_configs)

        # Assert expected results.
        assert status == RemediateStatus.SKIPPED
        assert errors == [consts.REMEDIATION_SKIPPED_MESSAGE]

    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config.VMotionPortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config."
           "VMotionPortGroupConfig._get_port_tcp_ip_stack")
    def test_check_compliance_compliant(self, mock_get_tcp_ip_stack, mock_get_dv_ports):
        mock_get_tcp_ip_stack.side_effect = [VMOTION, VMOTION,
                                             'defaultTcpipStack', 'defaultTcpipStack',
                                             'defaultTcpipStack']
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports]
        result = self.controller.check_compliance(self.context_mock, self.desired_configs)
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config.VMotionPortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config."
           "VMotionPortGroupConfig._get_port_tcp_ip_stack")
    def test_check_compliance_non_compliant(self, mock_get_tcp_ip_stack, mock_get_dv_ports):
        mock_get_tcp_ip_stack.side_effect = [VMOTION, VMOTION, VMOTION, 'defaultTcpipStack', 'defaultTcpipStack']
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports]
        result = self.controller.check_compliance(self.context_mock, self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: [
                {
                    'is_dedicated_vlan': False,
                    'ports': [{'host_name': 'host2', 'device': 'vmk4', 'tcp_ip_stack': 'defaultTcpipStack'}],
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2'
                }
            ],
            consts.DESIRED: [
                {
                    'is_dedicated_vlan': True,
                    'ports': [{'host_name': 'host2', 'device': 'vmk4', 'tcp_ip_stack': 'vmotion'}],
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2'
                }
            ]
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_check_compliance_failed(self, mock_vc_context):
        mock_vc_context.vc_vmomi_client.side_effect = Exception("Test exception")
        result = self.controller.check_compliance(mock_vc_context, self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ["Test exception"]
        }
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config.VMotionPortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.vmotion_port_group_config."
           "VMotionPortGroupConfig._get_port_tcp_ip_stack")
    def test_remediation_skipped(self, mock_get_tcp_ip_stack, mock_get_dv_ports):
        mock_get_tcp_ip_stack.side_effect = [VMOTION, VMOTION, VMOTION, 'defaultTcpipStack', 'defaultTcpipStack']
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports]
        result = self.controller.remediate(self.context_mock, self.desired_configs)

        # Assert expected results.
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE],
            consts.CURRENT: [{
                    'is_dedicated_vlan': False,
                    'ports': [{'host_name': 'host2', 'device': 'vmk4', 'tcp_ip_stack': 'defaultTcpipStack'}],
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2'
                }],
            consts.DESIRED: [
                {
                    'is_dedicated_vlan': True,
                    'ports': [{'host_name': 'host2', 'device': 'vmk4', 'tcp_ip_stack': 'vmotion'}],
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2'
                }
            ]
        }
        assert result == expected_result

    def test_get_port_tcp_ip_stack(self):
        host_mock = MagicMock(spec=vim.HostSystem)
        host_mock.name = 'host1'
        mock_vnic_1 = vim.host.VirtualNic()
        mock_vnic_1.device = 'vmk1'
        mock_vnic_1.spec = vim.host.VirtualNic.Specification()
        mock_vnic_1.spec.netStackInstanceKey = VMOTION
        mock_vnic_2 = vim.host.VirtualNic()
        mock_vnic_2.device = 'vmk2'
        mock_vnic_2.spec = vim.host.VirtualNic.Specification()
        mock_vnic_2.spec.netStackInstanceKey = 'defaultTcpipStack'
        host_mock.config.network.vnic = [mock_vnic_1, mock_vnic_2]

        device = 'vmk1'
        hosts_nic_port_cache = {}

        result = self.controller._get_port_tcp_ip_stack(host_mock, device, hosts_nic_port_cache)

        assert result == VMOTION
        assert hosts_nic_port_cache == {('host1', 'vmk1'): 'vmotion', ('host1', 'vmk2'): 'defaultTcpipStack'}
