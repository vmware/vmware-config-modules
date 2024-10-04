# Copyright 2024 VMware, Inc.  All rights reserved. -- VMware Confidential
import logging
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Set
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
ALLOW_MIX_TRAFFIC_TYPE = "allow_mix_traffic_type"
VLAN_INFO = "vlan_info"
PORTS = "ports"
NSX_BACKING_TYPE = "nsx"
VSAN_SERVICE = "vsan"
VSAN_WITNESS_SERVICE = "vsanWitness"


class IPBasedStoragePortGroupConfig(BaseController):
    """Class for ip based storage port groups vlan isolation config with get and set methods.

    Remediation is not supported as it involves different configurations on vsan, iscsi and NFS. Any drifts should
    be analyzed based on compliance report and manually remediated.

    | Config Id - 1225
    | Config Title - Isolate all IP-based storage traffic on distributed switches from other traffic types.

    """

    metadata = ControllerMetadata(
        name="ip_based_storage_port_group_config",  # controller name
        path_in_schema="compliance_config.vcenter.ip_based_storage_port_group_config",  # path in the schema to this controller's definition.
        configuration_id="1225",  # configuration id as defined in compliance kit.
        title="Isolate all IP-based storage traffic on distributed switches from other traffic types",  # controller title as defined in compliance kit.
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
    def _get_enabled_services(host: vim.HostSystem, device: str, hosts_nic_port_cache: dict) -> List:
        """Helper method to get_enabled_services for the particular port on the host.

        :param host: Host object.
        :type host: vim.HostSystem
        :param device: VM kernel port adapter device name,
        :type device: str
        :param hosts_nic_port_cache: Host_nics to port mapping cache.
        :type hosts_nic_port_cache: dict
        :return: List of enabled services on the VM Kernel.
        :rtype: list
        """
        services = list()
        for vnic_mgr_config in host.config.virtualNicManagerInfo.netConfig:
            selectedVnics = vnic_mgr_config.selectedVnic
            if selectedVnics:
                for vnic_name in selectedVnics:
                    pattern = r"VirtualNic-(vmk\d+)"
                    match = re.search(pattern, vnic_name)
                    if match:
                        vnic_device = match.group(1)
                    else:
                        raise Exception("Incorrect selected vnic!!")
                    if vnic_device == device:
                        services.append(vnic_mgr_config.nicType)
                    host_nic_key = (host.name, vnic_device)
                    if host_nic_key not in hosts_nic_port_cache:
                        hosts_nic_port_cache[host_nic_key] = [vnic_mgr_config.nicType]
                    elif vnic_mgr_config.nicType not in hosts_nic_port_cache[host_nic_key]:
                        hosts_nic_port_cache[host_nic_key].append(vnic_mgr_config.nicType)
        return services

    @staticmethod
    def _get_dv_ports(dvs, port_keys) -> List:
        """Get dvs ports data.

        :param dvs: distributed virtual switch.
        :type dvs: vim.DistributedVirtualSwitch
        :param port_keys: port keys.
        :type port_keys: string
        :return: a list of ports.
        :rtype: List
        """
        criteria = vim.dvs.PortCriteria()
        criteria.portKey = port_keys
        dv_ports = dvs.FetchDVPorts(criteria)
        return dv_ports

    def _get_iscsi_vmknics(self, context) -> Set:
        """Get iscsi binded vmknics.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: a set of iscsi binded vmknics.
        :rtype: Set
        """
        vmknics = set()
        vc_vsan_vmomi_client = context.vc_vsan_vmomi_client()
        # get all vsan enabled clusters
        all_vsan_enabled_clusters = vc_vsan_vmomi_client.get_all_vsan_enabled_clusters()
        for cluster_ref in all_vsan_enabled_clusters:
            # check vsan iscsi target service config (cluster level config)
            iscsi_config = vc_vsan_vmomi_client.get_vsan_iscsi_targets_config_for_cluster(cluster_ref)
            logger.debug(f"iscsi service config: {iscsi_config}")
            if iscsi_config and iscsi_config.enabled:
                vmknics.add(iscsi_config.defaultConfig.networkInterface)
                # check each individual targets
                cluster_iscsi_targets = vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster()
                iscsi_targets = cluster_iscsi_targets.GetIscsiTargets(cluster_ref)
                for iscsi_target in iscsi_targets:
                    vmknics.add(iscsi_target.networkInterface)
                    logger.debug(f"iscsi target: {iscsi_target}")

        return vmknics

    def _get_nfs_networks(self, context) -> Set:
        """Get NFS traffic portgroups.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: a set of NFS portgroups.
        :rtype: Set
        """
        vc_vsan_vmomi_client = context.vc_vsan_vmomi_client()
        vsan_config_system = vc_vsan_vmomi_client.get_vsan_cluster_config_system()
        logger.debug(f"vsan config system: {vsan_config_system}")
        portgroups = set()
        # get all vsan enabled clusters
        all_vsan_enabled_clusters = vc_vsan_vmomi_client.get_all_vsan_enabled_clusters()
        for cluster_ref in all_vsan_enabled_clusters:
            vsan_configs = vsan_config_system.VsanClusterGetConfig(cluster_ref)
            if vsan_configs and vsan_configs.fileServiceConfig:
                portgroup = vsan_configs.fileServiceConfig.network
                logger.debug(f"Portgroup used in NFS file service: {portgroup}")
                portgroups.add(portgroup)

        return portgroups

    def _get_portgroup_vlan_info(self, port_group_obj, vlans_counts) -> Dict:
        """Get portgroup vlan info.

        :param port_group_obj: portgroup object.
        :type port_group_obj: vim.dvs.DistributedVirtualPortgroup
        :return: vlan_info.
        :rtype: Dict
        """
        vlan_spec = port_group_obj.config.defaultPortConfig.vlan
        # Check vlan configuration for the port and also build a map of vlans_counts.
        # This would be used for checking overlapping of the port group vlan with others.
        if isinstance(vlan_spec, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec):
            vlan_id = vlan_spec.vlanId
            vlan_info = {"vlan_type": "VLAN", "vlan_id": vlan_id}
            vlans_counts[vlan_id] = vlans_counts.get(vlan_id, 0) + 1
        elif isinstance(vlan_spec, vim.dvs.VmwareDistributedVirtualSwitch.PvlanSpec):
            vlan_id = vlan_spec.pvlanId
            vlan_info = {"vlan_type": "Private VLAN", "vlan_id": vlan_id}
            vlans_counts[vlan_id] = vlans_counts.get(vlan_id, 0) + 1
        else:
            vlan_info = None
        return vlan_info

    def _check_ip_based_storage_traffic(
        self, dvs, port_group_obj, nfs_portgroups, iscsi_vmknics, hosts_nic_port_cache
    ) -> Tuple:
        """Check if portgroup is ip storage traffic and get ports data.

        :param dvs: distributed virtual switch.
        :type dvs: vim.DistributedVirtualSwitch
        :param port_group_obj: portgroup object.
        :type port_group_obj: vim.dvs.DistributedVirtualPortgroup
        :param nfs_portgroups: a set of portgroups used in NFS traffic.
        :type nfs_portgroups: set
        :param iscsi_vmknics: a set of vmknics used in iscsi traffic.
        :type iscsi_vmknics: set
        :param hosts_nic_port_cache: host nic port cache dictionary.
        :type hosts_nic_port_cache: dict
        :return: A tuple of ip based storage flag and ports data.
        :rtype: Tuple
        """
        logger.debug(f"Checking portgroup: {port_group_obj.name} for ip based storage traffic")
        is_pg_ip_based_storage = False
        ports_data = []
        port_keys = port_group_obj.portKeys
        dv_ports = self._get_dv_ports(dvs, port_keys)
        for dv_port in dv_ports:
            # Only check for VM Kernel ports
            if not dv_port.connectee or not isinstance(dv_port.connectee.connectedEntity, vim.HostSystem):
                continue
            host = dv_port.connectee.connectedEntity
            device = dv_port.connectee.nicKey
            host_nic_key = (host.name, device)
            services = hosts_nic_port_cache.get(host_nic_key)
            if services is None:
                services = self._get_enabled_services(host, device, hosts_nic_port_cache)
                logger.debug(f"vmk: {device} services: {services}")
                hosts_nic_port_cache[host_nic_key] = services
            ports_data.append({"host_name": host.name, "device": device, "services": services})
            if VSAN_SERVICE in services or VSAN_WITNESS_SERVICE in services:
                is_pg_ip_based_storage = True
                logger.debug(f"vsan service : {services} in portgroup: {port_group_obj.name}")
            # check if this vmknic used in iscsi even if service "vsan" not enabled
            elif device in iscsi_vmknics:
                is_pg_ip_based_storage = True
                logger.debug(f"iSCSI vmknics: {device} used in portgroup: {port_group_obj.name}")
        if not is_pg_ip_based_storage and port_group_obj in nfs_portgroups:
            # if portgroup used in NFS, no matter if VSAN service is enabled
            # on its member vmknics, it is considered ip based storage pg
            is_pg_ip_based_storage = True
            logger.debug(f"NFS portgroup: {port_group_obj.name}")
        return is_pg_ip_based_storage, ports_data

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """Get ip based storage distributed port groups vlan configurations for the vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: A tuple containing a dictionary to store ip based storage port groups data and a list of error messages if any.
        :rtype: Tuple
        """

        logger.info("Getting all ip based storage port groups info.")
        errors = []
        result = []
        try:
            # retrieve all distributed switches
            all_dv_switches = context.vc_vmomi_client().get_objects_by_vimtype(vim.DistributedVirtualSwitch)
            # retrieve all vmknics used in iscsi configurations
            iscsi_vmknics = self._get_iscsi_vmknics(context)
            logger.debug(f"Vmknics for iscsi: {iscsi_vmknics}")
            nfs_portgroups = self._get_nfs_networks(context)
            logger.debug(f"Portgroups used in NFS file service: {nfs_portgroups}")

            ip_based_storage_port_groups = dict()
            hosts_nic_port_cache = dict()
            vlans_counts = dict()
            for dvs in all_dv_switches:
                for port_group_obj in dvs.portgroup:
                    # skip nsx backed port and uplink port
                    is_nsx_backed = getattr(port_group_obj.config, "backingType", "") == NSX_BACKING_TYPE
                    is_uplink_port_group = getattr(port_group_obj.config, "uplink", False)
                    if is_nsx_backed or is_uplink_port_group:
                        continue

                    pg_name = port_group_obj.name
                    self.all_port_groups_in_vcenter.add((dvs.name, pg_name))

                    # get vlan info for this portgroup
                    vlan_info = self._get_portgroup_vlan_info(port_group_obj, vlans_counts)

                    # check if this portgroup is ip storage traffic based portgroup
                    # criterias to qualify for ip based storage traffic portgroup:
                    # 1). if the "service" of any vmknics in portgroup marked as "vsan" or "vsanWitness",
                    # 2). if any vmknics in the portgroup used by iscsi,
                    # 3). if the portgroup is used as "network" by NFS
                    is_pg_ip_based_storage, ports_data = self._check_ip_based_storage_traffic(
                        dvs, port_group_obj, nfs_portgroups, iscsi_vmknics, hosts_nic_port_cache
                    )
                    if is_pg_ip_based_storage:
                        portgroup_data = {VLAN_INFO: vlan_info, PORTS: ports_data}
                        ip_based_storage_port_groups.setdefault(dvs.name, {})[pg_name] = portgroup_data

            # Iterate over all ip based storage port groups candidates and create entries in result with
            # all required keys including IS_DEDICATED_VLAN.
            for switch_name, portgroups in ip_based_storage_port_groups.items():
                for portgroup_name, details in portgroups.items():
                    vlan_info = details[VLAN_INFO]
                    # IF vlan_type is not VLAN or is overlapping with any other port group's VLAN,
                    # set is_dedicated as False, otherwise True
                    if vlan_info is None or vlan_info.get("vlan_type") != "VLAN":
                        is_dedicated_vlan = False
                    elif "vlan_id" not in vlan_info or vlans_counts.get(vlan_info["vlan_id"], 0) != 1:
                        is_dedicated_vlan = False
                    else:
                        is_dedicated_vlan = True
                    logger.debug(
                        f"Adding {portgroup_name} in switch {switch_name} as candidate ip based storage port group "
                        f"to run check compliance on."
                    )
                    result.append(
                        {
                            SWITCH_NAME: switch_name,
                            PORT_GROUP_NAME: portgroup_name,
                            IS_DEDICATED_VLAN: is_dedicated_vlan,
                            PORTS: details[PORTS],
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
        :param desired_values: Desired value for ip based storage port groups.
        :type desired_values: dict
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        :rtype: Tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def _process_desired_values(self, desired_values: Dict) -> Tuple[dict, dict]:
        """Helper method to put desired values in map format.

        :param desired_values: Desired value for ip based storage  port groups.
        :type desired_values: dict
        :return: Return tuple of global desired values and a override map
        :rtype: Tuple[dict, dict]
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
                ALLOW_MIX_TRAFFIC_TYPE: override.get(
                    ALLOW_MIX_TRAFFIC_TYPE, global_desired_value.get(ALLOW_MIX_TRAFFIC_TYPE)
                ),
                VLAN_INFO: override.get(VLAN_INFO),
            }
        return global_desired_value, overrides_map

    def _get_non_compliant_configs(self, ip_based_storage_port_groups: List, desired_values: Dict) -> Tuple[List, List]:
        """Helper method to get non_compliant configs in the current and report current configs and desired configs.

        :param ip_based_storage_port_groups: Candidate portgroups which have atleast one ip based storage port.
        :type ip_based_storage_port_groups: List
        :param desired_values: Desired value for ip based storage  port groups.
        :type desired_values: dict
        :return: Return tuple of non_compliance ip based storage  port groups as current_configs, desired_configs
        :rtype: Tuple[list, list]
        """
        current_port_groups_configs = []
        desired_port_groups_configs = []
        errors = []
        try:
            global_desired_value, overrides_map = self._process_desired_values(desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            return current_port_groups_configs, desired_port_groups_configs, errors

        for pg in ip_based_storage_port_groups:
            switch_name = pg.get(SWITCH_NAME)
            port_group_name = pg.get(PORT_GROUP_NAME)
            key = (switch_name, port_group_name)
            pg_current = {}
            pg_desired = {}

            # check dedicated vlan for ip based storage traffic
            is_current_dedicated_vlan = pg.get(IS_DEDICATED_VLAN)
            if key in overrides_map:
                is_desired_dedicated_vlan = overrides_map[key].get(IS_DEDICATED_VLAN)
            else:
                is_desired_dedicated_vlan = desired_values.get(GLOBAL, {}).get(IS_DEDICATED_VLAN)
            if is_current_dedicated_vlan != is_desired_dedicated_vlan:
                pg_current = {IS_DEDICATED_VLAN: is_current_dedicated_vlan}
                pg_desired = {IS_DEDICATED_VLAN: is_desired_dedicated_vlan}

            # check all ports are with ip based storage traffic based on desired spec
            allow_mix_traffic_type = (
                overrides_map[key].get(ALLOW_MIX_TRAFFIC_TYPE)
                if key in overrides_map
                else global_desired_value.get(ALLOW_MIX_TRAFFIC_TYPE)
            )
            if allow_mix_traffic_type is not None and not allow_mix_traffic_type:
                current_ports = []
                for port in pg.get(PORTS):
                    # If port is not ip based storage type, append to current, desired to report in check compliance.
                    services = list(port.get("services"))
                    if services and not all(
                        service == VSAN_SERVICE or service == VSAN_WITNESS_SERVICE for service in services
                    ):
                        current_ports.append(port)

                if current_ports:
                    pg_current[PORTS] = current_ports

            # If there is any drift in the port group add switch_name and portgroup_name to the portgroup
            # and append to current, desired port groups configs to be reported in check compliance.
            if pg_current:
                pg_current[SWITCH_NAME] = switch_name
                pg_current[PORT_GROUP_NAME] = port_group_name
                if allow_mix_traffic_type is not None:
                    pg_current[ALLOW_MIX_TRAFFIC_TYPE] = allow_mix_traffic_type
                current_port_groups_configs.append(pg_current)
                if key in overrides_map:
                    pg_desired[SWITCH_NAME] = switch_name
                    pg_desired[PORT_GROUP_NAME] = port_group_name
                    if allow_mix_traffic_type is not None:
                        pg_desired[ALLOW_MIX_TRAFFIC_TYPE] = allow_mix_traffic_type
                    desired_port_groups_configs.append(pg_desired)

        # add "__GLOBAL__" portion of desired spec for non-compliant display if any drift found.
        if (current_port_groups_configs or desired_port_groups_configs) and global_desired_value:
            desired_port_groups_configs.insert(0, {"__GLOBAL__": global_desired_value})

        return current_port_groups_configs, desired_port_groups_configs, errors

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """Check compliance of all ip based storage distributed port groups vlan isolation configuration.

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
                        "switch_name": "Switch1",
                        "port_group_name": "PG2"
                    },
                    {
                        "is_dedicated_vlan": false,
                        "switch_name": "Switch1",
                        "port_group_name": "PG1"
                    }
                ],
                "desired": [
                    {
                        "is_dedicated_vlan": true,
                        "switch_name": "Switch1",
                        "port_group_name": "PG2"
                    },
                    {
                        "is_dedicated_vlan": true,
                        "switch_name": "Switch1",
                        "port_group_name": "PG1"
                    }
                ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for ip based stotage  port groups.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance for ip based storage traffic isolation")
        ip_based_storage_port_groups, errors = self.get(context=context)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # Iterate over desired_values and compare with current
        # If overrides are present in desired values, then use that data
        # Form switch_name[pg_name] desired values and one global desired_values
        # If switch_name[pg_name] present in current, then compare that else compare with global desired_values

        current_configs, desired_configs, errors = self._get_non_compliant_configs(
            ip_based_storage_port_groups=ip_based_storage_port_groups, desired_values=desired_values
        )
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}
        if current_configs or desired_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_configs,
                consts.DESIRED: desired_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context, desired_values) -> Dict:
        """Remediate is not implemented as this control requires manual intervention.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired value for the ip based storage port groups.
        :type desired_values: Dict
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        """
        logger.info("Running remediation for ip based storage traffic isolation")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        logger.info(f"{consts.REMEDIATION_SKIPPED_MESSAGE}")
        result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
        return result
