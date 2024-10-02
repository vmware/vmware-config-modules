import json
from typing import List

from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import ALLOW_MIX_TRAFFIC_TYPE
from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import GLOBAL
from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import IPBasedStoragePortGroupConfig
from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import IS_DEDICATED_VLAN
from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import OVERRIDES
from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import PORT_GROUP_NAME
from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import SWITCH_NAME
from config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config import VLAN_INFO
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestIPBasedStoragePortGroupConfig:
    def setup_method(self):
        self.controller = IPBasedStoragePortGroupConfig()
        self.desired_configs = {
            GLOBAL: {
                IS_DEDICATED_VLAN: True,
                ALLOW_MIX_TRAFFIC_TYPE: False
            },
            OVERRIDES: [
                {
                    ALLOW_MIX_TRAFFIC_TYPE: False,
                    SWITCH_NAME: "Switch1",
                    PORT_GROUP_NAME: "PortGroup1",
                    IS_DEDICATED_VLAN: True
                },
                {
                    SWITCH_NAME: "Switch1",
                    PORT_GROUP_NAME: "PortGroup2",
                    IS_DEDICATED_VLAN: True
                }
            ]
        }
        self.desired_configs2 = {
            GLOBAL: {
                IS_DEDICATED_VLAN: True
            },
            OVERRIDES: [
                {
                    IS_DEDICATED_VLAN: False,
                    SWITCH_NAME: "Switch1",
                    PORT_GROUP_NAME: "PortGroup1"
                },
                {
                    SWITCH_NAME: "Switch1",
                    PORT_GROUP_NAME: "PortGroup2",
                    IS_DEDICATED_VLAN: True
                }
            ]
        }
        self.incorrect_desired_configs = {
            GLOBAL: {
                IS_DEDICATED_VLAN: True
            },
            OVERRIDES: [
                {
                    IS_DEDICATED_VLAN: False,
                    SWITCH_NAME: "Switch3",
                    PORT_GROUP_NAME: "PortGroup5"
                },
                {
                    SWITCH_NAME: "Switch1",
                    PORT_GROUP_NAME: "PortGroup2",
                    IS_DEDICATED_VLAN: True
                }
            ]
        }
        self.current_vsan_portgroups = [
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup1",
                "is_dedicated_vlan": True,
                "ports": [
                    {
                        "host_name": "host1",
                        "device": "vmk1",
                        "services": ["vsan"]
                    },
                    {
                        "host_name": "host2",
                        "device": "vmk2",
                        "services": ["vsan"]
                    }
                ]
            },
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup2",
                "is_dedicated_vlan": True,
                "ports": [
                    {
                        "host_name": "host1",
                        "device": "vmk3",
                        "services": ["vsan"]
                    },
                    {
                        "host_name": "host2",
                        "device": "vmk4",
                        "services": ["vmotion"]
                    }
                ]
            }
        ]
        self.current_vsan_portgroups_all_traffic = [
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup1",
                "is_dedicated_vlan": True,
                "ports": [
                    {
                        "host_name": "host1",
                        "device": "vmk1",
                        "services": ["vmotion"]
                    },
                    {
                        "host_name": "host2",
                        "device": "vmk2",
                        "services": ["vmotion"]
                    }
                ]
            },
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup2",
                "is_dedicated_vlan": True,
                "ports": [
                    {
                        "host_name": "host1",
                        "device": "vmk3",
                        "services": ["vsan"]
                    },
                    {
                        "host_name": "host2",
                        "device": "vmk4",
                        "services": ["vmotion"]
                    }
                ]
            }
        ]
        self.current_vsan_portgroups_skip_uplink = [
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup1",
                "is_dedicated_vlan": True,
                "ports": [
                    {
                        "host_name": "host1",
                        "device": "vmk1",
                        "services": ["vsan"]
                    },
                    {
                        "host_name": "host2",
                        "device": "vmk2",
                        "services": ["vsan"]
                    }
                ]
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
                "vlan": 6,
            },
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup3",
                "pvlanId": 300,
            },
            {
                "switch_name": "Switch1",
                "port_group_name": "PortGroup4",
                "vlan": ["10-100", "105-110", "200-250"],
            }
        ]

        dvs_1_mock = MagicMock()
        dvs_1_mock.portgroup = [self.get_dv_port_group_mock_obj(pg_spec) for pg_spec in self.dv_pgs]
        dvs_1_mock.name = 'Switch1'
        self.dvs = dvs_1_mock

        self.port_group_1_ports = [self.get_port_mock_obj(host_name='host1', device_name='vmk1'),
                                   self.get_port_mock_obj(host_name='host2', device_name='vmk2')]
        self.port_group_2_ports = [self.get_port_mock_obj(host_name='host1', device_name='vmk3'),
                                   self.get_port_mock_obj(host_name='host2', device_name='vmk4')]
        self.port_group_3_ports = [self.get_port_mock_obj(host_name='host1', device_name='vmk5')]
        self.port_group_4_ports = [self.get_port_mock_obj(host_name='host1', device_name='vmk6', connectee=False)]
        self.ports = self.port_group_1_ports
        self.context_mock.vc_vmomi_client.return_value.get_objects_by_vimtype.return_value = [dvs_1_mock]
        self.nfs_portgroup_compliant_obj = self.get_port_group_mock_obj(dvs_1_mock.portgroup, "Switch1", "PortGroup1")
        self.nfs_portgroup_non_compliant_obj = self.get_port_group_mock_obj(dvs_1_mock.portgroup, "Switch1", "PortGroup3")
        self.portgroup_2_obj = self.get_port_group_mock_obj(dvs_1_mock.portgroup, "Switch1", "PortGroup2")
        self.iscsi_compliant_vmknics = ["vmk3", "vmk4"]
        self.iscsi_non_compliant_vmknics = ["vmk5"]
        self.vsan_cluster_configs = [
            {
                "datacenter_name": "SDDC-Datacenter",
                "cluster_name": "SDDC-Cluster-1",
            },
            {
                "datacenter_name": "SDDCt-Datacenter",
                "cluster_name": "SDDC-Cluster-2",
            },
            {
                "datacenter_name": "test-Datacenter",
                "cluster_name": "SDDC-Cluster-1",
            }
        ]
        self.all_vsan_enabled_mock_cluster_refs = \
            self.create_mock_objs_all_vsan_clusters(self.vsan_cluster_configs)

    def get_port_group_mock_obj(self, portgroup_objs, switch_name, port_group_name):
        for port_group_obj in portgroup_objs:
            if port_group_obj.name == port_group_name and port_group_obj.config.distributedVirtualSwitch.name == switch_name:
                return port_group_obj
        return None

    def get_dv_port_group_mock_obj(self, pg_spec, create_bad_mock=False):
        """
        Create mock object for DV port group based on port group spec
        """
        dv_pg_mock = MagicMock()
        dv_pg_mock.name = pg_spec.get("port_group_name")
        dv_pg_mock.portKeys = pg_spec.get("port_group_name")
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

    def get_port_mock_obj(self, host_name, device_name, connectee=True):
        mock_port = vim.dvs.DistributedVirtualPort()
        if connectee:
            connectee_mock = vim.dvs.PortConnectee()
            host_mock = MagicMock(spec=vim.HostSystem)
            host_mock.name = host_name
            connectee_mock.connectedEntity = host_mock
            connectee_mock.nicKey = device_name
        else:
            connectee_mock = None
        mock_port.connectee = connectee_mock
        return mock_port

    def create_mock_objs_all_vsan_clusters(self, cluster_specs):
        """
        Create pyvmomi like mock object for all clusters
        :param cluster_specs:
        :return:
        """
        all_vsan_cluster_refs = []
        for cluster_spec in cluster_specs:
            cluster_ref = MagicMock()
            cluster_ref.name = cluster_spec.get("cluster_name")
            cluster_ref.parent.parent.name = cluster_spec.get("datacenter_name")
            all_vsan_cluster_refs.append(cluster_ref)
        return all_vsan_cluster_refs

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_enabled_services")
    def test_get_success(self, mock_get_enabled_services, mock_get_dv_ports):
        mock_get_enabled_services.side_effect = [['vsan'], ['vsan'],
                                             ['vsan'], ['vmotion'],
                                             ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        result, errors = self.controller.get(self.context_mock)
        assert result == self.current_vsan_portgroups
        assert errors == []

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_enabled_services")
    def test_get_success_skip_uplink(self, mock_get_enabled_services, mock_get_dv_ports):
        mock_get_enabled_services.side_effect = [['vsan'], ['vsan'],
                                             ['vmotion'], ['vmotion'],
                                             ['vmotion'], ['management']]
        self.portgroup_2_obj.config.uplink = True
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_3_ports, self.port_group_4_ports]
        result, errors = self.controller.get(self.context_mock)
        assert result == self.current_vsan_portgroups_skip_uplink
        assert errors == []

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_enabled_services")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_iscsi_vmknics")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_nfs_networks")
    def test_get_success_all_traffic(self, mock_get_nfs_networks, mock_get_iscsi_vmknics, mock_get_enabled_services, mock_get_dv_ports):
        mock_get_enabled_services.side_effect = [['vmotion'], ['vmotion'],
                                             ['vsan'], ['vmotion'],
                                             ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        mock_get_nfs_networks.return_value = [self.nfs_portgroup_compliant_obj]
        mock_get_iscsi_vmknics.return_value = self.iscsi_compliant_vmknics
        result, errors = self.controller.get(self.context_mock)
        assert result == self.current_vsan_portgroups_all_traffic
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

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config."
           "IPBasedStoragePortGroupConfig._get_enabled_services")
    def test_check_compliance_compliant(self, mock_enabled_services, mock_get_dv_ports):
        mock_enabled_services.side_effect = [['vsan'], ['vsan'],
                                             ['vmotion'], ['vmotion'],
                                             ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        result = self.controller.check_compliance(self.context_mock, self.desired_configs)
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config."
           "IPBasedStoragePortGroupConfig._get_enabled_services")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_iscsi_vmknics")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_nfs_networks")
    def test_check_compliance_compliant_all_traffic(self, mock_get_nfs_networks, mock_get_iscsi_vmknics, mock_enabled_services, mock_get_dv_ports):
        mock_enabled_services.side_effect = [['vsan'], ['vsan'],
                                             ['vsan'], ['vsan'],
                                             ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        mock_get_nfs_networks.return_value = [self.nfs_portgroup_compliant_obj]
        mock_get_iscsi_vmknics.return_value = self.iscsi_compliant_vmknics
        result = self.controller.check_compliance(self.context_mock, self.desired_configs)
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config."
           "IPBasedStoragePortGroupConfig._get_enabled_services")
    def test_check_compliance_non_compliant(self, mock_enabled_services, mock_get_dv_ports):
        mock_enabled_services.side_effect = [['vsan'], ['vsan'], ['vsan'], ['vmotion'], ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        result = self.controller.check_compliance(self.context_mock, self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: [
                {
                    'ports': [{'host_name': 'host2', 'device': 'vmk4', 'services': ['vmotion']}],
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2',
                    'allow_mix_traffic_type': False,
                }
            ],
            consts.DESIRED: [
                {
                    '__GLOBAL__': {
                        'is_dedicated_vlan': True,
                        'allow_mix_traffic_type': False,
                    },
                },
                {
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2',
                    'allow_mix_traffic_type': False,
                }
            ]
        }
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config."
           "IPBasedStoragePortGroupConfig._get_enabled_services")
    def test_check_compliance_non_compliant2(self, mock_enabled_services, mock_get_dv_ports):
        mock_enabled_services.side_effect = [['vsan'], ['vsan'], ['vsan'], ['vmotion'], ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        result = self.controller.check_compliance(self.context_mock, self.desired_configs2)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: [
                {
                     'is_dedicated_vlan': True,
                     'port_group_name': 'PortGroup1',
                     'switch_name': 'Switch1',
                }
            ],
            consts.DESIRED: [
                {
                    '__GLOBAL__': {
                        'is_dedicated_vlan': True,
                    },
                },
                {
                    'is_dedicated_vlan': False,
                    'port_group_name': 'PortGroup1',
                    'switch_name': 'Switch1',
                }
            ]
        }
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config."
           "IPBasedStoragePortGroupConfig._get_enabled_services")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_iscsi_vmknics")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_nfs_networks")
    def test_check_compliance_non_compliant_all_traffic(self, mock_get_nfs_networks, mock_get_iscsi_vmknics, mock_enabled_services, mock_get_dv_ports):
        mock_enabled_services.side_effect = [['vsan'], ['vsan'], ['vsan'], ['vmotion'], ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        mock_get_nfs_networks.return_value = [self.nfs_portgroup_non_compliant_obj]
        mock_get_iscsi_vmknics.return_value = self.iscsi_non_compliant_vmknics
        result = self.controller.check_compliance(self.context_mock, self.desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: [
                {
                    'ports': [{'host_name': 'host2', 'device': 'vmk4', 'services': ['vmotion']}],
                    'allow_mix_traffic_type': False,
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2'
                },
                {
                    'is_dedicated_vlan': False,
                    'ports': [{'host_name': 'host1', 'device': 'vmk5', 'services': ['vmotion']}],
                    'allow_mix_traffic_type': False,
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup3'
                }
            ],
            consts.DESIRED: [
                {
                    '__GLOBAL__': {
                        'is_dedicated_vlan': True,
                        'allow_mix_traffic_type': False,
                    },
                },
                {
                    'allow_mix_traffic_type': False,
                    'switch_name': 'Switch1',
                    'port_group_name': 'PortGroup2'
                },
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

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config."
           "IPBasedStoragePortGroupConfig._get_enabled_services")
    def test_check_compliance_failed2(self, mock_enabled_services, mock_get_dv_ports):
        mock_enabled_services.side_effect = [['vsan'], ['vsan'], ['vsan'], ['vmotion'], ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports, self.port_group_4_ports]
        result = self.controller.check_compliance(self.context_mock, self.incorrect_desired_configs)
        expected_result = {
            consts.STATUS: ComplianceStatus.FAILED,
            consts.ERRORS: ["Port group provided in desired config overrides does not exist PortGroup5 in switch Switch3"]
        }
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config.IPBasedStoragePortGroupConfig._get_dv_ports")
    @patch("config_modules_vmware.controllers.vcenter.ip_based_storage_port_group_config."
           "IPBasedStoragePortGroupConfig._get_enabled_services")
    def test_remediation_skipped(self, mock_enabled_services, mock_get_dv_ports):
        mock_enabled_services.side_effect = [['vsan'], ['vsan'], ['vsan'], ['vmotion'], ['vmotion'], ['management']]
        mock_get_dv_ports.side_effect = [self.port_group_1_ports, self.port_group_2_ports, self.port_group_3_ports]
        result = self.controller.remediate(self.context_mock, self.desired_configs)

        # Assert expected results.
        expected_result = {
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE],
        }
        assert result == expected_result

    def test_get_enabled_services(self):
        host_mock = MagicMock(spec=vim.HostSystem)
        host_mock.name = 'host1'

        vnic1_mgr_config = vim.host.VirtualNicManager.NetConfig()
        vnic1_mgr_config.selectedVnic = ['VirtualNic-vmk1']
        vnic1_mgr_config.nicType = 'vsan'
        vnic2_mgr_config = vim.host.VirtualNicManager.NetConfig()
        vnic2_mgr_config.selectedVnic = ['VirtualNic-vmk2']
        vnic2_mgr_config.nicType = 'vmotion'
        vnic3_mgr_config = vim.host.VirtualNicManager.NetConfig()
        vnic3_mgr_config.selectedVnic = ['VirtualNic-vmk1']
        vnic3_mgr_config.nicType = 'management'

        host_mock.config.virtualNicManagerInfo.netConfig = [vnic1_mgr_config, vnic2_mgr_config, vnic3_mgr_config]

        device = 'vmk1'
        hosts_nic_port_cache = {}
        result = self.controller._get_enabled_services(host_mock, device, hosts_nic_port_cache)
        assert result == ['vsan', 'management']
        assert hosts_nic_port_cache == {('host1', 'vmk1'): ['vsan', 'management'], ('host1', 'vmk2'): ['vmotion']}

        device = 'vmk2'
        hosts_nic_port_cache = {}
        result = self.controller._get_enabled_services(host_mock, device, hosts_nic_port_cache)
        assert result == ['vmotion']
        assert hosts_nic_port_cache == {('host1', 'vmk1'): ['vsan', 'management'], ('host1', 'vmk2'): ['vmotion']}

    def test_get_enabled_services2(self):
        host_mock = MagicMock(spec=vim.HostSystem)
        host_mock.name = 'host1'

        vnic1_mgr_config = vim.host.VirtualNicManager.NetConfig()
        vnic1_mgr_config.selectedVnic = ['VirtualNic-vmk1']
        vnic1_mgr_config.nicType = 'vsan'
        vnic2_mgr_config = vim.host.VirtualNicManager.NetConfig()
        vnic2_mgr_config.selectedVnic = ['VirtualNic-nonexistnic2']
        vnic2_mgr_config.nicType = 'vmotion'

        host_mock.config.virtualNicManagerInfo.netConfig = [vnic1_mgr_config, vnic2_mgr_config]

        device = 'vmk2'
        hosts_nic_port_cache = {}
        error = None
        try:
            result = self.controller._get_enabled_services(host_mock, device, hosts_nic_port_cache)
        except Exception as e:
            error = str(e)

        assert error == "Incorrect selected vnic!!"

    def test_get_dv_ports(self):
        dvs = self.dvs
        setattr(dvs, "FetchDVPorts", MagicMock(return_value=self.ports))
        result = self.controller._get_dv_ports(dvs, "port_keys")
        assert result == self.ports

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_get_iscsi_vmknics(self, mock_vc_context, mock_vc_vsan_vmomi_client):
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        iscsi_config = MagicMock()
        iscsi_config.enable = True
        iscsi_config.defaultConfig.networkInterface = "vmk1"
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_config_for_cluster.return_value = iscsi_config
        iscsi_target = MagicMock()
        iscsi_target.networkInterface = "vmk2"
        iscsi_targets = [iscsi_target]
        cluster_iscsi_targets = MagicMock()
        setattr(cluster_iscsi_targets, "GetIscsiTargets", MagicMock(return_value=iscsi_targets))
        mock_vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster.return_value = cluster_iscsi_targets

        result = self.controller._get_iscsi_vmknics(mock_vc_context)
        assert result == {"vmk1", "vmk2"}

    @patch("config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client.VcVsanVmomiClient")
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_get_nfs_portgroups(self, mock_vc_context, mock_vc_vsan_vmomi_client):
        mock_vc_vsan_vmomi_client.get_all_vsan_enabled_clusters.return_value = self.all_vsan_enabled_mock_cluster_refs
        mock_vc_context.vc_vsan_vmomi_client.return_value = mock_vc_vsan_vmomi_client
        vsan_configs = MagicMock()
        vsan_configs.fileServiceConfig.network = self.nfs_portgroup_compliant_obj
        vsan_config_system = MagicMock()
        setattr(vsan_config_system, "VsanClusterGetConfig", MagicMock(return_value=vsan_configs))
        mock_vc_vsan_vmomi_client.get_vsan_cluster_config_system.return_value = vsan_config_system
        result = self.controller._get_nfs_networks(mock_vc_context)
        assert result == {self.nfs_portgroup_compliant_obj}
