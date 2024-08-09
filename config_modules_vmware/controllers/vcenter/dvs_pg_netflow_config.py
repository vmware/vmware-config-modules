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
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

SWITCH_NAME = "switch_name"
PORT_GROUP_NAME = "port_group_name"
SWITCH_CONFIG = "switch_config"
PORTGROUP_CONFIG = "portgroup_config"
IPFIX_COLLECTOR_IP = "ipfix_collector_ip"
IPFIX_ENABLED = "ipfix_enabled"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"
SWITCH_OVERRIDE_CONFIG = "switch_override_config"
PORTGROUP_OVERRIDE_CONFIG = "portgroup_override_config"
NSX_BACKING_TYPE = "nsx"


class DvsPortGroupNetflowConfig(BaseController):
    """Class for dvs and portgroup netflow config with get and set methods.

    | Config Id - 417
    | Config Title -The vCenter Server must only send NetFlow traffic to authorized collectors.

    """

    metadata = ControllerMetadata(
        name="dvs_pg_netflow_config",  # controller name
        path_in_schema="compliance_config.vcenter.dvs_pg_netflow_config",  # path in the schema to this controller's definition.
        configuration_id="417",  # configuration id as defined in compliance kit.
        title="The vCenter Server must only send NetFlow traffic to authorized collectors.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def _get_desired_ipfix_collector_ip(self, desired_values, switch_name):
        """Get desired value for a specific switch.
        :param desired_values: Desired value for switches and port groups.
        :type desired_values: dict
        :param switch_name: switch name for desired value.
        :type switch_name: string
        :return: collector ip address.
        :rtype: string
        """

        global_desired_value = desired_values.get(GLOBAL, {}).get(IPFIX_COLLECTOR_IP, "")
        logger.debug(f"Global desired ipfix collector ip: {global_desired_value}")
        overrides = desired_values.get(OVERRIDES, {}).get(SWITCH_OVERRIDE_CONFIG, [])
        for override in overrides:
            switch_name_in_desired = override.get(SWITCH_NAME)
            logger.debug(
                f"Override config - switch name: {switch_name}, switch name in desired: {switch_name_in_desired}"
            )
            if switch_name == switch_name_in_desired:
                return override.get(IPFIX_COLLECTOR_IP)
        return global_desired_value

    def _get_desired_ipfix_enabled(self, desired_values, switch_name, portgroup_name):
        """Get desired value for a specific port group.
        :param desired_values: Desired value for switches and port groups.
        :type desired_values: dict
        :param switch_name: switch name for desired value.
        :type switch_name: string
        :return: True/False
        :rtype: boolean
        """

        global_desired_value = desired_values.get(GLOBAL, {}).get(IPFIX_ENABLED)
        overrides = desired_values.get(OVERRIDES, {}).get(PORTGROUP_OVERRIDE_CONFIG, [])
        for override in overrides:
            switch_name_in_desired = override.get(SWITCH_NAME)
            portgroup_name_in_desired = override.get(PORT_GROUP_NAME)
            if switch_name == switch_name_in_desired and portgroup_name == portgroup_name_in_desired:
                return override.get(IPFIX_ENABLED)
        return global_desired_value

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """Get all distributed switches for the vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: A tuple containing dict of all netflow related switch/portgroup configs and a list of error messages if any.
        :rtype: Tuple
        """

        errors = []
        all_ipfix_configs = {}
        try:
            all_dv_switches = context.vc_vmomi_client().get_objects_by_vimtype(vim.DistributedVirtualSwitch)
            for dvs in all_dv_switches:
                switch_config_item = {}
                ipfix_collector_ip = dvs.config.ipfixConfig.collectorIpAddress
                switch_config_item = {SWITCH_NAME: dvs.name, IPFIX_COLLECTOR_IP: ipfix_collector_ip}
                all_ipfix_configs.setdefault(SWITCH_CONFIG, []).append(switch_config_item)
                for port_group_obj in dvs.portgroup:
                    # skip nsx portgroup
                    is_nsx_backed = getattr(port_group_obj.config, "backingType", "") == NSX_BACKING_TYPE
                    if not is_nsx_backed:
                        pg_name = port_group_obj.name
                        ipfix_enabled = port_group_obj.config.defaultPortConfig.ipfixEnabled.value
                        portgroup_config_item = {
                            SWITCH_NAME: dvs.name,
                            PORT_GROUP_NAME: pg_name,
                            IPFIX_ENABLED: ipfix_enabled,
                        }
                        all_ipfix_configs.setdefault(PORTGROUP_CONFIG, []).append(portgroup_config_item)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))

        return all_ipfix_configs, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """Set method to configure ipfix configurations for all dvs and pgs..

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired value for switches and port groups.
        :type desired_values: dict
        :return: Tuple of status and errors if any
        :rtype: Tuple
        """

        errors = []
        status = RemediateStatus.SUCCESS
        vc_vmomi_client = context.vc_vmomi_client()

        try:
            all_dv_switches = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualSwitch)
            for dvs in all_dv_switches:
                desired_ipfix_collector_ip = self._get_desired_ipfix_collector_ip(desired_values, dvs.name)
                ipfix_collector_ip = dvs.config.ipfixConfig.collectorIpAddress
                logger.debug(
                    f"Switch: {dvs.name}, ipfix collector ip: {ipfix_collector_ip}, desired ipfix collector ip: {desired_ipfix_collector_ip}"
                )
                if (ipfix_collector_ip is not None and ipfix_collector_ip != desired_ipfix_collector_ip) or (
                    ipfix_collector_ip is None and desired_ipfix_collector_ip != ""
                ):
                    dvs.config.ipfixConfig.collectorIpAddress = desired_ipfix_collector_ip
                    config_spec = dvs.ConfigSpec()
                    config_spec.configVersion = dvs.config.configVersion
                    config_spec.ipfixConfig = dvs.config.ipfixConfig
                    config_spec.ipfixConfig.collectorIpAddress = desired_ipfix_collector_ip
                    logger.debug(f"Remediate Switch: {dvs.name}")
                    task = dvs.ReconfigureDvs_Task(spec=config_spec)
                    vc_vmomi_client.wait_for_task(task=task)
                for port_group_obj in dvs.portgroup:
                    # skip nsx portgroup
                    is_nsx_backed = getattr(port_group_obj.config, "backingType", "") == NSX_BACKING_TYPE
                    if not is_nsx_backed:
                        pg_name = port_group_obj.name
                        desired_ipfix_enabled = self._get_desired_ipfix_enabled(desired_values, dvs.name, pg_name)
                        ipfix_enabled = port_group_obj.config.defaultPortConfig.ipfixEnabled.value
                        logger.debug(
                            f"Portgroup: {pg_name}, ipfix enabled: {ipfix_enabled}, desired ipfix enabled: {desired_ipfix_enabled}"
                        )
                        if ipfix_enabled != desired_ipfix_enabled:
                            config_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
                            config_spec.configVersion = port_group_obj.config.configVersion
                            config_spec.defaultPortConfig = (
                                vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
                            )
                            config_spec.defaultPortConfig.ipfixEnabled = vim.BoolPolicy(value=desired_ipfix_enabled)
                            logger.debug(f"Remediate portgroup: {pg_name}")
                            task = port_group_obj.ReconfigureDVPortgroup_Task(spec=config_spec)
                            vc_vmomi_client.wait_for_task(task=task)

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED

        return status, errors

    def _get_non_compliant_configs(self, all_ipfix_configs, desired_values: Dict) -> Dict:
        """Helper method to get non_compliant configs in the current and report current configs and desired configs.

        :param desired_values: Desired value for switch and  port groups.
        :type desired_values: dict
        :return: Return non_compliance netflow configs dvs/pg as current_configs
        :rtype: dict
        """

        non_compliant_configs = {}
        switch_configs = all_ipfix_configs.get(SWITCH_CONFIG)
        for switch_config in switch_configs:
            switch_name = switch_config[SWITCH_NAME]
            desired_ipfix_collector_ip = self._get_desired_ipfix_collector_ip(desired_values, switch_name)
            ipfix_collector_ip = switch_config[IPFIX_COLLECTOR_IP]
            logger.debug(
                f"Switch: {switch_name}, ipfix collector ip: {ipfix_collector_ip}, desired ipfix collector ip: {desired_ipfix_collector_ip}"
            )
            if (ipfix_collector_ip is not None and ipfix_collector_ip != desired_ipfix_collector_ip) or (
                ipfix_collector_ip is None and desired_ipfix_collector_ip != ""
            ):
                non_compliant_switch_config_item = {SWITCH_NAME: switch_name, IPFIX_COLLECTOR_IP: ipfix_collector_ip}
                non_compliant_configs.setdefault(SWITCH_CONFIG, []).append(non_compliant_switch_config_item)

        portgroup_configs = all_ipfix_configs.get(PORTGROUP_CONFIG)
        for portgroup_config in portgroup_configs:
            pg_name = portgroup_config[PORT_GROUP_NAME]
            switch_name = portgroup_config[SWITCH_NAME]
            desired_ipfix_enabled = self._get_desired_ipfix_enabled(desired_values, switch_name, pg_name)
            ipfix_enabled = portgroup_config[IPFIX_ENABLED]
            logger.debug(
                f"Portgroup: {pg_name}, switch: {switch_name}, ipfix enabled: {ipfix_enabled}, desired ipfix enabled: {desired_ipfix_enabled}"
            )
            if ipfix_enabled != desired_ipfix_enabled:
                non_compliant_portgroup_config_item = {
                    SWITCH_NAME: switch_name,
                    PORT_GROUP_NAME: pg_name,
                    IPFIX_ENABLED: ipfix_enabled,
                }
                non_compliant_configs.setdefault(PORTGROUP_CONFIG, []).append(non_compliant_portgroup_config_item)

        return non_compliant_configs

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """Check compliance of all distributed switches and port groups for netflow configuration.

        | Sample desired values

        .. code-block:: json

            {
              "__GLOBAL__": {
                "ipfix_collector_ip": ""
                "ipfix_enabled": false
              },
              "__OVERRIDES__": {
                "switch_override_config": [
                  {
                    "switch_name": "SW1",
                    "ipfix_collector_ip": "10.0.0.250"
                  }
                ],
                "portgroup_override_config": [
                  {
                    "switch_name": "SW1",
                    "port_group_name": "PG1",
                    "ipfix_enabled": false
                  }
                ]
              }
            }

        | Sample check compliance response

        .. code-block:: json

            {
              "status": "NON_COMPLIANT",
              "current": [
                {
                  "switch_name": "Switch1",
                  "ipfix_collector_ip": "10.0.0.1"
                },
                {
                  "switch_name": "Switch1",
                  "port_group_name": "PG1"
                  "ipfix_enabled": true
                }
              ],
              "desired": {
                "__GLOBAL__": {
                  "ipfix_collector_ip": ""
                  "ipfix_enabled": false
                },
                "__OVERRIDES__": {
                  "switch_override_config": [
                    {
                      "switch_name": "SW1",
                      "ipfix_collector_ip": "10.0.0.250"
                    }
                  ],
                  "portgroup_override_config": [
                    {
                      "switch_name": "SW1",
                      "port_group_name": "PG1",
                      "ipfix_enabled": false
                    }
                  ]
                }
              }
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for netflow config for switches and  port groups.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance for switches and port groups")
        all_ipfix_configs, errors = self.get(context=context)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs = self._get_non_compliant_configs(
            all_ipfix_configs=all_ipfix_configs, desired_values=desired_values
        )
        if non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
