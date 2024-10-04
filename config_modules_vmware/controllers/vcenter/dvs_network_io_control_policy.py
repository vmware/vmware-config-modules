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

# Constants
DESIRED_KEY = "network_io_control_status"
SWITCH_NAME = "switch_name"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"


class DVSNetworkIOControlPolicy(BaseController):
    """Manage DV Switch Network I/O control policy with get and set methods.

    | Config Id - 409
    | Config Title - The vCenter Server must manage excessive bandwidth and Denial of Service (DoS) attacks by enabling
        Network I/O Control (NIOC).

    """

    metadata = ControllerMetadata(
        name="dvs_network_io_control",  # controller name
        path_in_schema="compliance_config.vcenter.dvs_network_io_control",  # path in the schema to this controller's definition.
        configuration_id="409",  # configuration id as defined in compliance kit.
        title="The vCenter Server must manage excessive bandwidth and Denial of Service (DoS) attacks by enabling Network I/O Control (NIOC).",
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
        Get DVS Network I/O control policy for all DV switches.

        | Sample get output

        .. code-block:: json

            [
              {
                "switch_name": "SwitchB",
                "network_io_control_status": false
              },
              {
                "switch_name": "SwitchC",
                "network_io_control_status": true
              },
              {
                "switch_name": "SwitchA",
                "network_io_control_status": false
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of DV switch network I/O control policy and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = self.__get_all_dv_switch_network_io_control_policy(vc_vmomi_client)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set Network I/O control policy for all DV switches.

        | Sample desired state

        .. code-block:: json

            {
              "__GLOBAL__": {
                "network_io_control_status": false
              },
              "__OVERRIDES__": [
                {
                  "switch_name": "Switch-A",
                  "network_io_control_status": false
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for enabling/disabling Network I/O control policy.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            self.__set_network_io_control_policy_for_all_dv_switches(vc_vmomi_client, desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def __get_all_dv_switch_network_io_control_policy(self, vc_vmomi_client: VcVmomiClient) -> List[Dict]:
        """
        Get Network I/O control policy for all DV Switches.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of Network I/O control policy for all DV switches.
        :rtype: List
        :return:
        """
        dv_switch_network_io_control_configs = []
        all_dv_switches = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualSwitch)

        for dvs in all_dv_switches:
            network_io_control_status = {
                SWITCH_NAME: dvs.name,
                DESIRED_KEY: dvs.config.networkResourceManagementEnabled,
            }
            dv_switch_network_io_control_configs.append(network_io_control_status)
        return dv_switch_network_io_control_configs

    def __set_network_io_control_policy_for_all_dv_switches(
        self, vc_vmomi_client: VcVmomiClient, desired_values: Dict
    ) -> None:
        """
        Enable or disable Network I/O control policy for all dv switches.

        | Recommended value for network I/O control: true | enabled

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :param desired_values: Desired values for Network I/O control policy.
        :type desired_values: Dict
        :return:
        :rtype: None
        """
        desired_global_network_io_control_value = desired_values.get(GLOBAL, {}).get(DESIRED_KEY)
        overrides = desired_values.get(OVERRIDES, [])
        # desired_network_io_control_value = desired_values.get(DESIRED_KEY)
        all_switch_refs = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualSwitch)

        for dvs_ref in all_switch_refs:
            # Check if there are overrides for the current DVS
            override_health_check_value = next(
                (switch.get(DESIRED_KEY) for switch in overrides if switch[SWITCH_NAME] == dvs_ref.name),
                None,
            )
            current_network_io_control_value = dvs_ref.config.networkResourceManagementEnabled
            desired_network_io_control_value = (
                override_health_check_value
                if override_health_check_value is not None
                else desired_global_network_io_control_value
            )

            if current_network_io_control_value == desired_network_io_control_value:
                logger.info(
                    f"DV switch {dvs_ref.name} already has desired network I/O control config," f" skipping remediation"
                )
            else:
                logger.info(
                    f"Setting network I/O control config {desired_network_io_control_value} on DV "
                    f"switch {dvs_ref.name}"
                )
                dvs_ref.EnableNetworkResourceManagement(desired_network_io_control_value)

    def __get_non_compliant_configs(self, switch_configs: List, desired_values: Dict) -> List:
        """
        Get all non-compliant items for the given desired state spec.

        :return:
        :meta private:
        """
        non_compliant_items = []
        # convert to dictionary for easy access
        configs_by_switch_name = {config.get(SWITCH_NAME): config for config in switch_configs}

        global_desired_value = desired_values.get(GLOBAL, {}).get(DESIRED_KEY)
        overrides = desired_values.get(OVERRIDES, [])

        # Check global non-compliance
        non_compliant_global = [config for config in switch_configs if config.get(DESIRED_KEY) != global_desired_value]
        if non_compliant_global:
            non_compliant_items.extend(non_compliant_global)

        # Remove non-compliant override config if exists from global
        for override in overrides:
            override_switch_name = override.get(SWITCH_NAME)
            for config in non_compliant_global:
                if config.get(SWITCH_NAME) == override_switch_name:
                    non_compliant_items.remove(config)

        # Check overrides for non-compliance
        for switch_override in overrides:
            switch_name = switch_override.get(SWITCH_NAME)
            desired_value = switch_override.get(DESIRED_KEY)

            # Find the configuration for the current switch
            config = configs_by_switch_name.get(switch_name)
            if config and config.get(DESIRED_KEY) != desired_value:
                non_compliant_items.append(config)
        return non_compliant_items

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Check compliance of Network I/O control policy for all DV switches.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for network I/O control policy.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        dv_switch_network_io_control_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs = self.__get_non_compliant_configs(dv_switch_network_io_control_configs, desired_values)

        if non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Remediate configuration drifts by applying desired values.

        | Sample desired state for remediation.

        .. code-block:: json

            {
              "__GLOBAL__": {
                "network_io_control_status": false
              },
              "__OVERRIDES__": [
                {
                  "switch_name": "Switch-A",
                  "network_io_control_status": false
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for Network I/O control for DV switches.
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
        else:
            errors = result[consts.ERRORS]
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        status, errors = self.set(context=context, desired_values=desired_values)

        if not errors:
            result = {consts.STATUS: status, consts.OLD: non_compliant_configs, consts.NEW: desired_values}
        else:
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result
