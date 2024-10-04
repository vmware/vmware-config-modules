from typing import List

from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.dv_pg_vlan_trunking_authorized import (
    DVPortGroupVlanTrunkingConfig
)
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

class TestDVPortGroupVlanTrunkingConfig:
    def setup_method(self):
        self.controller = DVPortGroupVlanTrunkingConfig()
        self.compliant_dv_pgs = [
            {
                "switch_name": "DSwitch-test1",
                "port_group_name": "DPortGroup-test",
                "vlan": 10,
                "uplink": True,
                "backing_type": "nsx",
            },
            {
                "switch_name": "DSwitch-test2",
                "port_group_name": "DPortGroup",
                "vlan": ["10-100", "105", "200-250"],
                "uplink": False,
                "backing_type": "standard"
            },
            {
                "switch_name": "DSwitch-test3",
                "port_group_name": "SDDC-DPortGroup-vMotion",
                "vlan": ["200"],
                "uplink": False,
                "backing_type": "standard"
            }
        ]
        self.compliant_get_values = [
            {
                "switch_name": "DSwitch-test2",
                "port_group_name": "DPortGroup",
                "vlan_info": {
                    "vlan_type": "VLAN trunking",
                    "vlan_ranges":[
                        {'start': 10, 'end': 100}, {'start': 105, 'end': 105}, {'start': 200, 'end': 250}
                    ]
                }
            },
            {
                "switch_name": "DSwitch-test3",
                "port_group_name": "SDDC-DPortGroup-vMotion",
                "vlan_info": {
                    "vlan_type": "VLAN trunking",
                    "vlan_ranges":[
                        {'start': 200, 'end': 200}
                    ]
                }
            }
        ]
        self.non_compliant_dv_pgs = [
            {
                "switch_name": "DSwitch-test2",
                "port_group_name": "DPortGroup",
                "vlan": ["1-10", "15-200", "201-202"],
                "uplink": False,
                "backing_type": "standard"
            },
            {
                "switch_name": "DSwitch-test3",
                "port_group_name": "SDDC-DPortGroup-vMotion",
                "vlan": ["1"],
                "uplink": False,
                "backing_type": "standard"
            }
        ]
        self.non_compliant_get_values = [
            {
                "switch_name": "DSwitch-test2",
                "port_group_name": "DPortGroup",
                "vlan_info": {
                    "vlan_type": "VLAN trunking",
                    "vlan_ranges":[
                        { "start": 1, "end": 10},
                        { "start": 15, "end": 200},
                        { "start": 201, "end": 202}
                    ]
                }
            },
            {
                "switch_name": "DSwitch-test3",
                "port_group_name": "SDDC-DPortGroup-vMotion",
                "vlan_info": {
                    "vlan_type": "VLAN trunking",
                    "vlan_ranges":[
                        { "start": 1, "end": 1}
                    ]
                }
            }
        ]
        self.compliant_value = [
            {
                "switch_name": "DSwitch-test2",
                "port_group_name": "DPortGroup",
                "vlan_info": {
                    "vlan_type": "VLAN trunking",
                    "vlan_ranges":[
                        { "start": 10, "end": 100},
                        { "start": 105, "end": 105},
                        { "start": 200, "end": 250}
                    ]
                }
            },
            {
                "switch_name": "DSwitch-test3",
                "port_group_name": "SDDC-DPortGroup-vMotion",
                "vlan_info": {
                    "vlan_type": "VLAN trunking",
                    "vlan_ranges":[
                        { "start": 200, "end": 200}
                    ]
                }
            },
        ]
        # Pyvmomi type MagicMock objects
        self.compliant_dv_pg_pyvmomi_mocks = [
            self.get_dv_port_group_mock_obj(pg_spec) for pg_spec in self.compliant_dv_pgs
        ]
        self.non_compliant_dv_pg_pyvmomi_mocks = [
            self.get_dv_port_group_mock_obj(pg_spec) for pg_spec in self.non_compliant_dv_pgs
        ]
        # Bad mock to induce error
        self.dv_pg_mock_pyvmomi_bad_object = [
            self.get_dv_port_group_mock_obj(pg_spec, create_bad_mock=True) for pg_spec in self.non_compliant_dv_pgs
        ]

    def get_dv_port_group_mock_obj(self, pg_spec, create_bad_mock=False):
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

        dv_pg_mock.config.uplink = pg_spec.get("uplink")
        dv_pg_mock.config.backingType = pg_spec.get("backing_type")
        if not create_bad_mock:
            dv_pg_mock.config.configVersion = "24"
        dv_pg_mock.config.distributedVirtualSwitch.name = pg_spec.get("switch_name")
        return dv_pg_mock

    def create_datacenter_mock(self, name):
        datacenter_mock = MagicMock()
        datacenter_mock.name = name
        return datacenter_mock

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = self.compliant_dv_pg_pyvmomi_mocks

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)

        assert result == self.compliant_get_values
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get DV PG config")

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        expected_get_object_result = self.compliant_dv_pg_pyvmomi_mocks
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_get_object_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs = self.non_compliant_get_values
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: self.compliant_value,
        }

        expected_get_object_result = self.non_compliant_dv_pg_pyvmomi_mocks
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = expected_get_object_result
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        print(result)
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
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        current_value = self.non_compliant_dv_pg_pyvmomi_mocks
        expected_result = {
            'errors': [consts.REMEDIATION_SKIPPED_MESSAGE],
            consts.STATUS: RemediateStatus.SKIPPED,
            consts.DESIRED: self.compliant_value,
            consts.CURRENT: self.non_compliant_get_values
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = current_value
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
