# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.vcenter.utils.vc_port_group_utils import (
    get_all_non_uplink_non_nsx_port_group_and_security_configs,
)
from config_modules_vmware.controllers.vcenter.utils.vc_port_group_utils import (
    get_non_compliant_security_policy_configs,
)
from config_modules_vmware.controllers.vcenter.utils.vc_port_group_utils import PortGroupSecurityConfigEnum
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
DESIRED_KEY = "allow_mac_address_change"
NSX_BACKING_TYPE = "nsx"
SWITCH_NAME = "switch_name"
PORT_GROUP_NAME = "port_group_name"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"


class DVPortGroupMacAddressChangePolicy(BaseController):
    """Manage DV Port group MAC address change policy with get and set methods.

    | Config Id - 407
    | Config Title - The vCenter Server must set the distributed port group MAC Address Change policy to reject.

    """

    metadata = ControllerMetadata(
        name="dvpg_mac_address_change_policy",  # controller name
        path_in_schema="compliance_config.vcenter.dvpg_mac_address_change_policy",  # path in the schema to this controller's definition.
        configuration_id="407",  # configuration id as defined in compliance kit.
        title="The vCenter Server must set the distributed port group MAC Address Change policy to reject.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """
        Get DV Port group MAC address change policy for all port groups.

        | Sample get call output

        .. code-block:: json

            [
              {
                "switch_name": "SwitchB",
                "port_group_name": "dv_pg_PortGroup3",
                "allow_mac_address_change": false
              },
              {
                "switch_name": "SwitchC",
                "port_group_name": "dv_pg_PortGroup1",
                "allow_mac_address_change": true
              },
              {
                "switch_name": "SwitchA",
                "port_group_name": "dv_pg_PortGroup2",
                "allow_mac_address_change": false
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of port group and their MAC address change policy and a list of error messages.
        :rtype: tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = self.__get_all_dv_port_mac_address_change_policy(vc_vmomi_client)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """
        Set DV Port group MAC address change policy for all port groups.

        | Recommended DV port group MAC address change policy: false | reject.
        | Sample desired state

        .. code-block:: json

            {
              "__GLOBAL__": {
                "allow_mac_address_change": false
              },
              "__OVERRIDES__": [
                {
                  "switch_name": "Switch-A",
                  "port_group_name": "dv_pg_PortGroup1",
                  "allow_mac_address_change": true
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the enabling or disabling MAC address change policy on port groups.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            self.__set_mac_address_change_policy_for_non_compliant_dv_port_groups(vc_vmomi_client, desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def __get_all_dv_port_mac_address_change_policy(self, vc_vmomi_client: VcVmomiClient) -> List:
        """
        Get all DV Port groups and their MAC address change policies.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of MAC address change policies for all DV port groups.
        :rtype: List
        """
        all_dv_port_groups = get_all_non_uplink_non_nsx_port_group_and_security_configs(
            vc_vmomi_client, PortGroupSecurityConfigEnum.MAC_CHANGES
        )

        mac_address_change_policies = []
        for dv_pg, mac_address_change_config in all_dv_port_groups:
            has_switch_name_config = hasattr(dv_pg.config, "distributedVirtualSwitch") and hasattr(
                dv_pg.config.distributedVirtualSwitch, "name"
            )
            mac_address_change_policies.append(
                {
                    SWITCH_NAME: dv_pg.config.distributedVirtualSwitch.name if has_switch_name_config else "",
                    PORT_GROUP_NAME: dv_pg.name,
                    DESIRED_KEY: mac_address_change_config,
                }
            )

        return mac_address_change_policies

    def __set_mac_address_change_policy_for_non_compliant_dv_port_groups(
        self, vc_vmomi_client: VcVmomiClient, desired_values: Dict
    ) -> None:
        """
        Set MAC address change policy for all non-compliant DV port groups.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :param desired_values: Desired values for MAC address change policy.
        :type desired_values: Dict
        :return:
        :rtype: None
        """
        desired_global_mac_address_change_value = desired_values.get(GLOBAL, {}).get(DESIRED_KEY)
        overrides = desired_values.get(OVERRIDES, [])
        all_dv_port_groups = get_all_non_uplink_non_nsx_port_group_and_security_configs(
            vc_vmomi_client, PortGroupSecurityConfigEnum.MAC_CHANGES
        )

        for dv_pg, current_mac_address_change_policy in all_dv_port_groups:
            dv_switch_name = getattr(dv_pg.config.distributedVirtualSwitch, "name")
            port_group_name = getattr(dv_pg, "name")

            # Check if there are overrides for the current DV Port group
            override_mac_address_change = next(
                (
                    override.get(DESIRED_KEY)
                    for override in overrides
                    if override[SWITCH_NAME] == dv_switch_name and override[PORT_GROUP_NAME] == port_group_name
                ),
                None,
            )
            desired_mac_address_change_policy = (
                override_mac_address_change
                if override_mac_address_change is not None
                else desired_global_mac_address_change_value
            )
            # re-configure only if current and desired values are not equal
            if current_mac_address_change_policy != desired_mac_address_change_policy:
                config_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
                config_spec.configVersion = dv_pg.config.configVersion
                config_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
                config_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()
                config_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(
                    value=desired_mac_address_change_policy
                )
                logger.info(
                    f"Setting MAC address change policy {desired_mac_address_change_policy}"
                    f" on port group {dv_pg.name}"
                )
                task = dv_pg.ReconfigureDVPortgroup_Task(spec=config_spec)
                vc_vmomi_client.wait_for_task(task=task)

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Check compliance of all dv port group's MAC address change policy.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for MAC address change policy.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        mac_address_change_policy_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs, desired_configs = get_non_compliant_security_policy_configs(
            mac_address_change_policy_configs, desired_values, DESIRED_KEY
        )

        if non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: desired_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Remediate configuration drifts.

        | Sample desired state for remediation.

        .. code-block:: json

            {
              "__GLOBAL__": {
                "allow_mac_address_change": false
              },
              "__OVERRIDES__": [
                {
                  "switch_name": "Switch-A",
                  "port_group_name": "dv_pg_PortGroup1",
                  "allow_mac_address_change": true
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for MAC address change policy.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running remediation")
        result = self.check_compliance(context, desired_values)

        if result[consts.STATUS] == ComplianceStatus.COMPLIANT:
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}
        elif result[consts.STATUS] == ComplianceStatus.NON_COMPLIANT:
            non_compliant_configs = result[consts.CURRENT]
            desired_configs = result[consts.DESIRED]
        else:
            errors = result[consts.ERRORS]
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        status, errors = self.set(context=context, desired_values=desired_values)

        if not errors:
            result = {consts.STATUS: status, consts.OLD: non_compliant_configs, consts.NEW: desired_configs}
        else:
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result
