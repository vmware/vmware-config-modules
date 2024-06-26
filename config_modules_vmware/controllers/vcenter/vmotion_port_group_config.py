# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from copy import deepcopy
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

SWITCH_NAME = "switch_name"
PORT_GROUP_NAME = "port_group_name"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"
IS_DEDICATED_VLAN = "is_dedicated_vlan"
VLAN_INFO = "vlan_info"
PORTS = "ports"
VMOTION = "vmotion"


class VMotionPortGroupConfig(BaseController):
    """Class for vmotion port groups vlan isolation config with get and set methods.

    Remediation is not supported as it involves addition/deletion of ports in the port group along with VLAN changes,
    it could have unwanted impact. Any drifts should be analyzed based on compliance report and manually remediated.

    | Config Id - 0000
    | Config Title - All vMotion traffic on distributed switches must be isolated from other traffic types.

    """

    metadata = ControllerMetadata(
        name="dvpg_vmotion_traffic_isolation",  # controller name
        path_in_schema="compliance_config.vcenter.dvpg_vmotion_traffic_isolation",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="All vMotion traffic on distributed switches must be isolated from other traffic types.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def __init__(self):
        super().__init__()
        self.all_port_groups_in_vcenter = set()

    @staticmethod
    def _get_port_tcp_ip_stack(host: vim.HostSystem, device: str, hosts_nic_port_cache: dict):
        """Helper method to get_tcp_ip_stack for the particular port on the host.

        :param host: Host object.
        :type host: vim.HostSystem
        :param device: VM kernel port adapter device name,
        :type device: str
        :param hosts_nic_port_cache: Host_nics to port mapping cache.
        :type hosts_nic_port_cache: dict
        :return: VM kernel TCP/IP stack type.
        :rtype: str
        """
        result = ""
        for vnic in host.config.network.vnic:
            if vnic.device == device:
                result = vnic.spec.netStackInstanceKey
            host_nic_key = (host.name, vnic.device)
            hosts_nic_port_cache[host_nic_key] = vnic.spec.netStackInstanceKey
        return result

    @staticmethod
    def _get_dv_ports(dvs, port_keys):
        criteria = vim.dvs.PortCriteria()
        criteria.portKey = port_keys
        dv_ports = dvs.FetchDVPorts(criteria)
        return dv_ports

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """Get vmotion distributed port groups vlan configurations for the vCenter.

        | Sample get output

        .. code-block:: json

            [
              {
                "switch_name": "Switch1",
                "port_group_name": "PG1",
                "is_dedicated_vlan": true,
                "ports": [
                  {
                    "host_name": "esxi-3.vrack.vsphere.local",
                    "device": "vmk5",
                    "tcp_ip_stack": "vmotion"
                  },
                  {
                    "host_name": "esxi-4.vrack.vsphere.local",
                    "device": "vmk3",
                    "tcp_ip_stack": "vmotion"
                  }
                ],
                  "vlan_info": {
                    "vlan_type": "VLAN",
                    "vlan_id": 130
                  }
              },
              {
                "switch_name": "Switch1",
                "port_group_name": "PG2",
                "is_dedicated_vlan": false,
                "ports": [
                  {
                    "host_name": "esxi-3.vrack.vsphere.local",
                     "device": "vmk1",
                     "tcp_ip_stack": "defaultTcpipStack"
                  }
                ],
                  "vlan_info": {
                    "vlan_type": "VLAN",
                    "vlan_id": 170
                  }
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: A tuple containing a dictionary to store vmotion port groups data and a list of error messages if any.
        :rtype: Tuple
        """

        logger.info("Getting all vmotion port groups info.")
        errors = []
        result = []
        try:
            all_dv_switches = context.vc_vmomi_client().get_objects_by_vimtype(vim.DistributedVirtualSwitch)
            vmotion_port_groups = dict()
            hosts_nic_port_cache = dict()
            vlans_counts = dict()
            for dvs in all_dv_switches:
                for port_group_obj in dvs.portgroup:
                    # Uplink port groups are to be excluded in determining isolation of vMotion port groups
                    if port_group_obj.config.uplink:
                        logger.debug(f"Ignore uplink port group: {port_group_obj.name}")
                        continue
                    ports_data = []
                    pg_name = port_group_obj.name
                    self.all_port_groups_in_vcenter.add((dvs.name, pg_name))
                    is_pg_vmotion = False
                    port_keys = port_group_obj.portKeys
                    dv_ports = self._get_dv_ports(dvs, port_keys)
                    vlan_spec = port_group_obj.config.defaultPortConfig.vlan
                    # Check vlan configuration for the port and also build a map of vlans_counts.
                    # This would be used for checking overlapping of the port group vlan with others.
                    if isinstance(vlan_spec, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec):
                        vlan_id = vlan_spec.vlanId
                        vlan_info = {"vlan_type": "VLAN", "vlan_id": vlan_id}
                        vlans_counts[vlan_id] = vlans_counts.get(vlan_id, 0) + 1
                    elif isinstance(vlan_spec, vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec):
                        ranges = []
                        for item in vlan_spec.vlanId:
                            ranges.append({"start": item.start, "end": item.end})
                        vlan_info = {"vlan_type": "VLAN trunking", "vlan_range": ranges}

                        # Max range can be 0-4094, and no range would be overlapping within ranges list.
                        # so max lookups limited to 4095 and same for memory usage.
                        for vlan_range in ranges:
                            start_vlan = vlan_range["start"]
                            end_vlan = vlan_range["end"]
                            for vlan in range(start_vlan, end_vlan + 1):
                                vlans_counts[vlan] = vlans_counts.get(vlan, 0) + 1
                    elif isinstance(vlan_spec, vim.dvs.VmwareDistributedVirtualSwitch.PvlanSpec):
                        vlan_id = vlan_spec.pvlanId
                        vlan_info = {"vlan_type": "Private VLAN", "vlan_id": vlan_id}
                        vlans_counts[vlan_id] = vlans_counts.get(vlan_id, 0) + 1
                    else:
                        vlan_info = None

                    for dv_port in dv_ports:
                        # Only check for VM Kernel ports
                        if not dv_port.connectee or not isinstance(dv_port.connectee.connectedEntity, vim.HostSystem):
                            continue
                        host = dv_port.connectee.connectedEntity
                        device = dv_port.connectee.nicKey
                        host_nic_key = (host.name, device)
                        tcp_ip_stack = hosts_nic_port_cache.get(host_nic_key)
                        if tcp_ip_stack is None:
                            tcp_ip_stack = self._get_port_tcp_ip_stack(host, device, hosts_nic_port_cache)
                            hosts_nic_port_cache[host_nic_key] = tcp_ip_stack

                        ports_data.append({"host_name": host.name, "device": device, "tcp_ip_stack": tcp_ip_stack})
                        if tcp_ip_stack == VMOTION:
                            is_pg_vmotion = True

                    if is_pg_vmotion:
                        portgroup_data = {VLAN_INFO: vlan_info, PORTS: ports_data}
                        if dvs.name in vmotion_port_groups:
                            vmotion_port_groups[dvs.name][pg_name] = portgroup_data
                        else:
                            vmotion_port_groups[dvs.name] = {pg_name: portgroup_data}

            # Iterate over all vmotion port groups candidates and create entries in result with
            # all required keys including IS_DEDICATED_VLAN.
            for switch_name, portgroups in vmotion_port_groups.items():
                for portgroup_name, details in portgroups.items():
                    vlan_info = details[VLAN_INFO]
                    # IF vlan_type is not VLAN or is overlapping with any other port group's VLAN,
                    # set is_dedicated as False, otherwise True
                    if vlan_info is None or vlan_info["vlan_type"] != "VLAN":
                        is_dedicated_vlan = False
                    elif "vlan_id" not in vlan_info or vlans_counts.get(vlan_info["vlan_id"], 0) != 1:
                        is_dedicated_vlan = False
                    else:
                        is_dedicated_vlan = True
                    logger.debug(
                        f"Adding {portgroup_name} in switch {switch_name} as candidate vMotion port group "
                        f"to run check compliance on."
                    )
                    result.append(
                        {
                            SWITCH_NAME: switch_name,
                            PORT_GROUP_NAME: portgroup_name,
                            IS_DEDICATED_VLAN: is_dedicated_vlan,
                            PORTS: details[PORTS],
                            VLAN_INFO: details[VLAN_INFO],
                        }
                    )

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))

        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """Set method is not implemented as this control requires user intervention to remediate.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired value for vmotion port groups.
        :type desired_values: dict
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        :rtype: Tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def _get_non_compliant_configs(self, vmotion_port_groups: List, desired_values: Dict) -> Tuple[List, List]:
        """Helper method to get non_compliant configs in the current and report current configs and desired configs.

        :param vmotion_port_groups: Candidate portgroups which have atleast one vmotion port.
        :type vmotion_port_groups: List
        :param desired_values: Desired value for vmotion port groups.
        :type desired_values: dict
        :return: Return tuple of non_compliance vmotion port groups as current_configs, desired_configs
        :rtype: Tuple[list, list]
        """
        overrides = desired_values.get(OVERRIDES, [])
        global_desired_value = desired_values.get(GLOBAL, {})

        overrides_map = {}
        for override in overrides:
            switch_name = override.get(SWITCH_NAME)
            port_group_name = override.get(PORT_GROUP_NAME)
            key = (switch_name, port_group_name)
            # Check if port group exists else raise exception to report non-existence of this port group.
            if key not in self.all_port_groups_in_vcenter:
                raise Exception(
                    f"Port group provided in desired config overrides does not "
                    f"exist {port_group_name} in switch {switch_name}"
                )
            overrides_map[key] = {
                IS_DEDICATED_VLAN: override.get(IS_DEDICATED_VLAN, global_desired_value.get(IS_DEDICATED_VLAN)),
                VLAN_INFO: override.get(VLAN_INFO),
            }
        current_port_groups_configs = []
        desired_port_groups_configs = []

        for pg in vmotion_port_groups:
            switch_name = pg.get(SWITCH_NAME)
            port_group_name = pg.get(PORT_GROUP_NAME)
            key = (switch_name, port_group_name)
            pg_current = {}
            pg_desired = {}
            if key in overrides_map:
                # compare keys: is dedicated_vlan, vlan_info and check if all ports are with vmotion
                if pg.get(IS_DEDICATED_VLAN) != overrides_map[key].get(IS_DEDICATED_VLAN):
                    pg_current[IS_DEDICATED_VLAN] = pg.get(IS_DEDICATED_VLAN)
                    pg_desired[IS_DEDICATED_VLAN] = overrides_map[key].get(IS_DEDICATED_VLAN)
                if pg.get(VLAN_INFO) != overrides_map[key].get(VLAN_INFO):
                    pg_current[VLAN_INFO] = pg.get(VLAN_INFO)
                    pg_desired[VLAN_INFO] = overrides_map[key].get(VLAN_INFO)
                    pg_desired[VLAN_INFO]["vlan_type"] = "VLAN"

            else:
                if GLOBAL in desired_values and pg.get(IS_DEDICATED_VLAN) != desired_values[GLOBAL].get(
                    IS_DEDICATED_VLAN
                ):
                    pg_current[IS_DEDICATED_VLAN] = pg.get(IS_DEDICATED_VLAN)
                    pg_desired[IS_DEDICATED_VLAN] = global_desired_value.get(IS_DEDICATED_VLAN)

            if GLOBAL in desired_values or key in overrides_map:
                current_ports = []
                desired_ports = []
                for port in pg.get(PORTS):
                    # If port is not vmotion type, append to current, desired to report in check compliance.
                    if port.get("tcp_ip_stack") != VMOTION:
                        current_ports.append(port)
                        desired_port = deepcopy(port)
                        desired_port["tcp_ip_stack"] = VMOTION
                        desired_ports.append(desired_port)

                if current_ports or desired_ports:
                    pg_current[PORTS] = current_ports
                    pg_desired[PORTS] = desired_ports

                # If there is any drift in the port group add switch_name and portgroup_name to the portgroup
                # and append to current, desired port groups configs to be reported in check compliance.
                if pg_current or pg_desired:
                    pg_current[SWITCH_NAME] = switch_name
                    pg_current[PORT_GROUP_NAME] = port_group_name
                    pg_desired[SWITCH_NAME] = switch_name
                    pg_desired[PORT_GROUP_NAME] = port_group_name
                    current_port_groups_configs.append(pg_current)
                    desired_port_groups_configs.append(pg_desired)

        return current_port_groups_configs, desired_port_groups_configs

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """Check compliance of all vmotion distributed port groups vlan isolation configuration.

        | Sample desired values

        .. code-block:: json

            {
                "__GLOBAL__": {
                    "is_dedicated_vlan": true
                },
                "__OVERRIDES__": [
                    {
                        "switch_name": "Switch1",
                        "port_group_name": "PG2",
                        "is_dedicated_vlan": true,
                        "vlan_info": {
                            "vlan_id": 131,
                            "vlan_type": "VLAN"
                        }
                    }
                ]
            }

        | Sample check compliance response

        .. code-block:: json

            {
                "status": "NON_COMPLIANT",
                "current": [
                    {
                        "is_dedicated_vlan": false,
                        "vlan_info": {
                            "vlan_type": "VLAN",
                            "vlan_id": 130
                        },
                        "switch_name": "Switch1",
                        "port_group_name": "PG2"
                    },
                    {
                        "is_dedicated_vlan": false,
                        "ports": [
                            {
                                "host_name": "esxi-4.vrack.vsphere.local",
                                "device": "vmk4",
                                "tcp_ip_stack": "defaultTcpipStack"
                            },
                            {
                                "host_name": "esxi-5.vrack.vsphere.local",
                                "device": "vmk4",
                                "tcp_ip_stack": "defaultTcpipStack"
                            },
                            {
                                "host_name": "esxi-5.vrack.vsphere.local",
                                "device": "vmk5",
                                "tcp_ip_stack": "defaultTcpipStack"
                            }
                        ],
                        "switch_name": "Switch1",
                        "port_group_name": "PG1"
                    }
                ],
                "desired": [
                    {
                        "is_dedicated_vlan": true,
                        "vlan_info": {
                            "vlan_id": 131,
                            "vlan_type": "VLAN"
                        },
                        "switch_name": "Switch1",
                        "port_group_name": "PG2"
                    },
                    {
                        "is_dedicated_vlan": true,
                        "ports": [
                            {
                                "host_name": "esxi-4.vrack.vsphere.local",
                                "device": "vmk4",
                                "tcp_ip_stack": "vmotion"
                            },
                            {
                                "host_name": "esxi-5.vrack.vsphere.local",
                                "device": "vmk4",
                                "tcp_ip_stack": "vmotion"
                            },
                            {
                                "host_name": "esxi-5.vrack.vsphere.local",
                                "device": "vmk5",
                                "tcp_ip_stack": "vmotion"
                            }
                        ],
                        "switch_name": "Switch1",
                        "port_group_name": "PG1"
                    }
                ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for vmotion port groups.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance for control-vmotion traffic isolation")
        vmotion_port_groups, errors = self.get(context=context)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # Iterate over desired_values and compare with current
        # If overrides are present in desired values, then use that data
        # Form switch_name[pg_name] desired values and one global desired_values
        # If switch_name[pg_name] present in current, then compare that else compare with global desired_values

        current_configs, desired_configs = self._get_non_compliant_configs(
            vmotion_port_groups=vmotion_port_groups, desired_values=desired_values
        )
        if current_configs or desired_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_configs,
                consts.DESIRED: desired_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
