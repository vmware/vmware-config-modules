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
SWITCH_NAME_KEY = "switch_name"
PORT_GROUP_NAME_KEY = "port_group_name"
VLAN_TYPE_TRUNKING = "VLAN trunking"
VLAN_RANGES = "vlan_ranges"
VLAN_INFO = "vlan_info"
VLAN_TYPE = "vlan_type"


class DVPortGroupVlanTrunkingConfig(BaseController):
    """DV Port group Vlan trunking config get and set methods.

    | Config Id - 1227
    | Config Title - The vCenter Server must not configure VLAN Trunking unless Virtual Guest
                     Tagging (VGT) is required and authorized.

    """

    metadata = ControllerMetadata(
        name="dvpg_vlan_trunking_authorized_check",  # controller name
        path_in_schema="compliance_config.vcenter.dvpg_vlan_trunking_authorized_check",  # path in the schema to this
        # controller's definition.
        configuration_id="1227",  # configuration id as defined in compliance kit.
        title="The vCenter Server must not configure VLAN Trunking unless Virtual Guest Tagging (VGT) is required and authorized.",  # controller title
        # as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """Get DV Port group Native Vlan exclusion config for all applicable port groups.

        | Sample get call output

        .. code-block:: json

            [
              {
                switch_name: "SDDC-Dswitch-Private",
                port_group_name: "SDDC-DPortGroup-VSAN",
                vlan_info: {
                  vlan_type: "VLAN trunking",
                  vlan_ranges:[
                    { start: 0, end: 90},
                    { start: 120, end: 200}
                  ]
                }
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
            result = self._get_all_dv_port_vlan_trunking_configs(vc_vmomi_client)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """Set vlan config for DV port groups to remediate trunking vlan in the configuration.

        | Sample desired state

        .. code-block:: json

            [
              {
                switch_name: "SDDC-Dswitch-Private",
                port_group_name: "SDDC-DPortGroup-VSAN",
                vlan_info: {
                  vlan_type: "VLAN trunking",
                  vlan_ranges:[
                    { start: 0, end: 90},
                    { start: 120, end: 200}
                  ]
                }
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values containing vlan trunking configs.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        logger.info(consts.REMEDIATION_SKIPPED_MESSAGE)
        status = RemediateStatus.SKIPPED
        return status, errors

    def _is_vlan_trunking_ranges_compliant(self, vlan_ranges, desired_vlan_ranges) -> bool:
        for vlan_range in vlan_ranges:
            vlan_in_desired_range = False
            for desired_vlan_range in desired_vlan_ranges:
                if (
                    vlan_range.get("start") >= desired_vlan_range["start"]
                    and vlan_range.get("end") <= desired_vlan_range["end"]
                ):
                    vlan_in_desired_range = True
            if not vlan_in_desired_range:
                return False
        return True

    def _get_desired_value_map(self, desired_values):
        desired_config_map = {}
        for desired_value in desired_values:
            switch_name = desired_value.get(SWITCH_NAME_KEY)
            port_group_name = desired_value.get(PORT_GROUP_NAME_KEY)
            key = (switch_name, port_group_name)
            desired_config_map[key] = {
                VLAN_INFO: desired_value.get(VLAN_INFO),
            }
        return desired_config_map

    def _get_vlan_ranges(self, vlan_range_configs):
        vlan_ranges = []
        for vlan_range_config in vlan_range_configs:
            vlan_range = {}
            vlan_range["start"] = vlan_range_config.start
            vlan_range["end"] = vlan_range_config.end
            vlan_ranges.append(vlan_range)
        return vlan_ranges

    def _get_dv_pg_vlan_config(self, pg_vlan_config, desired_config_map) -> Dict:
        """compare pg vlan config with desired config

        :param pg_vlan_config: Dict containing port group vlan trunking config.
        :type pg_vlan_config: Dict
        :param desired_config_map: Dict containing VLAN ID a specific port group.
        :type desired_config_map: Dict
        :return: List of non-compliant vlan trunking configs
        :rtype: List
        """
        switch_name = pg_vlan_config[SWITCH_NAME_KEY]
        port_group_name = pg_vlan_config[PORT_GROUP_NAME_KEY]
        key = (switch_name, port_group_name)
        # check if path name in desired config.
        vlan_config = pg_vlan_config[VLAN_INFO][VLAN_RANGES]
        desired_vlan_config = desired_config_map[key].get(VLAN_INFO) if key in desired_config_map else None

        # check if vlan config matches what in desired config
        if desired_vlan_config and desired_vlan_config.get(VLAN_TYPE) == VLAN_TYPE_TRUNKING:
            if self._is_vlan_trunking_ranges_compliant(vlan_config, desired_vlan_config.get(VLAN_RANGES)):
                return None

        return pg_vlan_config

    def _get_non_compliant_dv_port_vlan_configs(self, pg_vlan_trunking_configs, desired_values) -> List:
        """Get all non compliant vlan trunking configurations.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of tuple of non compliant configurations
        :rtype: List
        """
        non_compliant_dv_pg_configs = []
        desired_config_map = self._get_desired_value_map(desired_values)

        for pg_vlan_trunking_config in pg_vlan_trunking_configs:
            non_compliant_dv_pg_config = self._get_dv_pg_vlan_config(pg_vlan_trunking_config, desired_config_map)
            if non_compliant_dv_pg_config is not None:
                non_compliant_dv_pg_configs.append(non_compliant_dv_pg_config)

        return non_compliant_dv_pg_configs

    def _get_vlan_config_for_non_uplink_dv_port_groups(self, vc_vmomi_client: VcVmomiClient) -> List[Tuple]:
        """Helper function to retrieve vlan configurations for non-uplink dv port groups.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of tuple with non-uplink dv_pg_refs and their vlan configurations.
        :rtype: List
        """
        vlan_config_non_uplink_dv_port_group_refs = []
        all_dv_port_group_refs = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualPortgroup)

        for dv_pg in all_dv_port_group_refs:
            is_uplink_port_group = hasattr(dv_pg.config, "uplink") and getattr(dv_pg.config, "uplink")
            # skip all uplink port groups
            if not is_uplink_port_group:
                vlan_config = getattr(getattr(dv_pg.config, "defaultPortConfig", None), "vlan", None)
                vlan_config_non_uplink_dv_port_group_refs.append((dv_pg, vlan_config))
        return vlan_config_non_uplink_dv_port_group_refs

    def _get_all_dv_port_vlan_trunking_configs(self, vc_vmomi_client: VcVmomiClient) -> List:
        """Get all non-uplink DV Port groups and their vlan configurations.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of tuple of
        :rtype: List
        """
        non_uplink_dv_port_groups = self._get_vlan_config_for_non_uplink_dv_port_groups(vc_vmomi_client)
        logger.debug(f"Retrieved Non-uplink port group refs {non_uplink_dv_port_groups}")

        dv_pg_vlan_configs = []
        for dv_pg_ref, vlan_config in non_uplink_dv_port_groups:
            port_group_vlan_config = {}
            # check vlan type
            is_vlan_trunk_type = isinstance(vlan_config, vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec)
            if is_vlan_trunk_type:
                port_group_vlan_config = {}
                has_switch_name_config = hasattr(dv_pg_ref.config, "distributedVirtualSwitch") and hasattr(
                    dv_pg_ref.config.distributedVirtualSwitch, "name"
                )
                port_group_vlan_config[SWITCH_NAME_KEY] = (
                    dv_pg_ref.config.distributedVirtualSwitch.name if has_switch_name_config else ""
                )
                port_group_vlan_config[PORT_GROUP_NAME_KEY] = dv_pg_ref.name
                port_group_vlan_config[VLAN_INFO] = {}
                port_group_vlan_config[VLAN_INFO][VLAN_TYPE] = VLAN_TYPE_TRUNKING
                port_group_vlan_config[VLAN_INFO][VLAN_RANGES] = self._get_vlan_ranges(vlan_config.vlanId)
                dv_pg_vlan_configs.append(port_group_vlan_config)
        logger.debug(f"Retrieved vlan trunking configs for non-uplink port groups {dv_pg_vlan_configs}")
        return dv_pg_vlan_configs

    def check_compliance(self, context: VcenterContext, desired_values: dict) -> Dict:
        """Check compliance for all dv port groups if vlan trunking is in configuration.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Dict containing VLAN trunking configs  to be excluded checked.
        :type desired_values: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        all_dv_pg_vlan_trunking_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_vlan_trunking_configs = self._get_non_compliant_dv_port_vlan_configs(
            all_dv_pg_vlan_trunking_configs, desired_values
        )
        logger.info(f"Non compliant port groups {non_compliant_vlan_trunking_configs}")

        if non_compliant_vlan_trunking_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_vlan_trunking_configs,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
