# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

# constants
VLAN_KEY = "vlan"
DESIRED_KEY = "reserved_vlan_ids_to_exclude"
SWITCH_NAME_KEY = "switch_name"
PORT_GROUP_NAME_KEY = "port_group_name"
NSX_BACKING_TYPE = "nsx"


class DVPortGroupReservedVlanExclusionConfig(BaseController):
    """Manage DV Port group Reserved Vlan exclusion config with get and set methods.

    | Config Id - 1202
    | Config Title - Configure all port groups to VLAN values not reserved by upstream physical switches.

    """

    metadata = ControllerMetadata(
        name="dvpg_excluded_reserved_vlan_policy",  # controller name
        path_in_schema="compliance_config.vcenter.dvpg_excluded_reserved_vlan_policy",  # path in the schema to this
        # controller's definition.
        configuration_id="1202",  # configuration id as defined in compliance kit.
        title="Configure all port groups to VLAN values not reserved by upstream physical switches.",  # controller title
        # as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in
        # ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """Get DV Port group Reserved Vlan exclusion config for all applicable port groups.

        | Sample get call output

        .. code-block:: json

            [
              {
                "switch_name": "DSwitch-test",
                "port_group_name": "DPortGroup-test",
                "vlan": 1
              },
              {
                "switch_name": "DSwitch-test",
                "port_group_name": "DPortGroup",
                "vlan": ["1-100", "105", "200-250"]
              },
              {
                "switch_name": "SDDC-Dswitch-Private",
                "port_group_name": "SDDC-DPortGroup-vMotion",
                "vlan": 1
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of port group and their vlan configs and a list of error messages.
        :rtype: tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = self.__get_all_dv_port_vlan_configs(vc_vmomi_client)
            logger.debug(
                f"Retrieved DV Port group Reserved Vlan exclusion config for all applicable port groups" f" {result}"
            )
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """Set vlan config for DV port groups excluding reserved vlan in the configuration.

        | Sample desired state

        .. code-block:: json

            {
              "reserved_vlan_id_to_exclude": 1
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values containing reserved vlan id to be excluded from port group configurations.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        logger.info(consts.REMEDIATION_SKIPPED_MESSAGE)
        status = RemediateStatus.SKIPPED
        return status, errors

    def __get_vlan_config_for_non_nsx_non_uplink_dv_port_groups(self, vc_vmomi_client: VcVmomiClient) -> List[Tuple]:
        """Helper function to retrieve vlan configurations for non-nsx and non-uplink dv port groups.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of tuple with non-nsx, non-uplink dv_pg_refs and their vlan configurations.
        :rtype: List
        """
        vlan_config_non_nsx_non_uplink_dv_port_group_refs = []
        all_dv_port_group_refs = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualPortgroup)
        logger.info(f"Retrieved DV port groups {all_dv_port_group_refs}")

        for dv_pg in all_dv_port_group_refs:
            is_uplink_port_group = hasattr(dv_pg.config, "uplink") and getattr(dv_pg.config, "uplink")
            is_nsx_backed = getattr(dv_pg.config, "backingType", "") == NSX_BACKING_TYPE
            # skip all uplink and nsx backed port groups
            if not is_uplink_port_group and not is_nsx_backed:
                vlan_config = getattr(getattr(dv_pg.config, "defaultPortConfig", None), "vlan", None)
                vlan_config_non_nsx_non_uplink_dv_port_group_refs.append((dv_pg, vlan_config))
        return vlan_config_non_nsx_non_uplink_dv_port_group_refs

    def __is_reserved_vlan_in_range(self, vlan_range: vim.NumericRange, reserved_vlan_ids: List):
        """Check if a list of reserved vlan values lie in range of vlan trunk range.

        :param vlan_range: vLan range configured for a dv port group.
        :type vlan_range:vim.NumericRange
        :param reserved_vlan_ids: list of reserved vlan ids to check if they lie within given vlan range
        :type reserved_vlan_id: list
        :return:
        """
        logger.info(f"Check if reserved vlan is part of vlan range {vlan_range}")
        start = vlan_range.start
        end = vlan_range.end
        for reserved_vlan_id in reserved_vlan_ids:
            if start <= reserved_vlan_id <= end:
                return True
        return False

    def __get_all_dv_port_vlan_configs(self, vc_vmomi_client: VcVmomiClient) -> List:
        """Get all non-nsx, non-uplink DV Port groups and their vlan configurations.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of tuple of
        :rtype: List
        """
        non_nsx_non_uplink_dv_port_groups = self.__get_vlan_config_for_non_nsx_non_uplink_dv_port_groups(
            vc_vmomi_client
        )
        logger.debug(f"Retrieved Non-NSX & Non-uplink port group refs {non_nsx_non_uplink_dv_port_groups}")

        dv_pg_vlan_configs = []
        for dv_pg_ref, vlan_config in non_nsx_non_uplink_dv_port_groups:
            port_group_vlan_config = {}
            has_switch_name_config = hasattr(dv_pg_ref.config, "distributedVirtualSwitch") and hasattr(
                dv_pg_ref.config.distributedVirtualSwitch, "name"
            )
            port_group_vlan_config[SWITCH_NAME_KEY] = (
                dv_pg_ref.config.distributedVirtualSwitch.name if has_switch_name_config else ""
            )
            port_group_vlan_config[PORT_GROUP_NAME_KEY] = dv_pg_ref.name

            # check vlan type
            is_vlan_type = isinstance(vlan_config, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec)
            is_vlan_trunk_type = isinstance(vlan_config, vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec)
            is_pvt_vlan_type = isinstance(vlan_config, vim.dvs.VmwareDistributedVirtualSwitch.PvlanSpec)

            if is_vlan_type:
                port_group_vlan_config[VLAN_KEY] = getattr(vlan_config, "vlanId")
            elif is_vlan_trunk_type:
                trunk_vlan_range = []
                vlan_ranges = vlan_config.vlanId
                for vlan_range in vlan_ranges:
                    start = vlan_range.start
                    end = vlan_range.end
                    if start == end:
                        trunk_vlan_range.append(str(start))
                    else:
                        trunk_vlan_range.append(f"{start}-{end}")
                port_group_vlan_config[VLAN_KEY] = trunk_vlan_range
            elif is_pvt_vlan_type:
                port_group_vlan_config[VLAN_KEY] = getattr(vlan_config, "pvlanId")
            dv_pg_vlan_configs.append(port_group_vlan_config)
        logger.info(f"Retrieved vlan configs for non-nsx & non-uplink port groups {dv_pg_vlan_configs}")
        return dv_pg_vlan_configs

    def __get_non_compliant_vlan_configs(self, dv_pg_vlan_configs: List, desired_values: dict) -> List:
        """Get list of dv port groups with vlan configurations overlapping with reserved vlan ids.

        :param dv_pg_vlan_configs: List of non-uplink, non-nsx port groups.
        :type dv_pg_vlan_configs: List
        :param desired_values: Dict containing a list of reserved VLAN IDs to be excluded from port group configurations.
        :type desired_values: Dict
        :return: List of non-compliant vlan configs
        :rtype: List
        """
        non_compliant_dv_port_group_configs = []
        reserved_vlans_to_exclude = desired_values.get(DESIRED_KEY)
        for dv_pg_vlan_config in dv_pg_vlan_configs:
            vlan_config = dv_pg_vlan_config[VLAN_KEY]
            # vlan trunk spec will be in list format Ex:["1-200", "205", "300-350"]
            if isinstance(vlan_config, List):
                for vlan_range in vlan_config:
                    # Trunk vlan can have ranges like "1-100"
                    if isinstance(vlan_range, str) and "-" in vlan_range:
                        ranges = vlan_range.split("-")
                        start = int(ranges[0])
                        end = int(ranges[1])
                        numeric_range = vim.NumericRange(start=start, end=end)
                        if self.__is_reserved_vlan_in_range(numeric_range, reserved_vlans_to_exclude):
                            non_compliant_dv_port_group_configs.append(dv_pg_vlan_config)
                            break
                    # Trunk ranges might also have single numeric values like "200"
                    else:
                        if int(vlan_range) in reserved_vlans_to_exclude:
                            non_compliant_dv_port_group_configs.append(dv_pg_vlan_config)
                            break
            elif isinstance(vlan_config, int):
                if vlan_config in reserved_vlans_to_exclude:
                    non_compliant_dv_port_group_configs.append(dv_pg_vlan_config)
        return non_compliant_dv_port_group_configs

    def check_compliance(self, context: VcenterContext, desired_values: dict) -> Dict:
        """Check compliance of all dv port groups against reserved vlan ids to be excluded from configuration.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Dict containing reserved VLAN IDs to be excluded from port group configurations.
        :type desired_values: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        all_dv_pg_vlan_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_port_groups = self.__get_non_compliant_vlan_configs(all_dv_pg_vlan_configs, desired_values)
        logger.info(f"Non compliant port groups {non_compliant_port_groups}")

        if non_compliant_port_groups:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_port_groups,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
