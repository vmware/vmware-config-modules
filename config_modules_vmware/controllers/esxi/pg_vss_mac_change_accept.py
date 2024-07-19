# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

VSWITCH_NAME = "vss_name"
MAC_CHANGE_ACCEPT = "mac_change_accept"


class PgVssMacChangeAccept(BaseController):
    """ESXi controller to get/set guest MAC address changes configuration on vSS portgroup.

    | Config Id - 161
    | Config Title - All port groups on standard switches must be configured to reject guest MAC address changes.

    """

    metadata = ControllerMetadata(
        name="pg_vss_mac_change_accept",  # controller name
        path_in_schema="compliance_config.esxi.pg_vss_mac_change_accept",
        # path in the schema to this controller's definition.
        configuration_id="161",  # configuration id as defined in compliance kit.
        title="All port groups on standard switches must be configured to reject guest MAC address changes.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: HostContext) -> Tuple[list, List[str]]:
        """Get vSS portgroup MAC change configuration for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of a list of all pg vss configs and a list of errors if any..
        :rtype: Tuple
        """
        logger.info("Getting vSS portgroup MAC change configuration for esxi.")
        all_vss_pg_mac_change_configs = []
        errors = []
        try:
            all_vss = context.host_ref.config.network.vswitch
            for vss in all_vss:
                mac_change = vss.spec.policy.security.macChanges
                vss_mac_change = {VSWITCH_NAME: vss.name, MAC_CHANGE_ACCEPT: mac_change}
                all_vss_pg_mac_change_configs.append(vss_mac_change)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return all_vss_pg_mac_change_configs, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set vSS portgroup MAC change configuration for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: boolean of True/False.
        :type desired_values: boolean
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting vSS portgroup MAC change configuration for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            all_vss = context.host_ref.config.network.vswitch
            for vss in all_vss:
                mac_change = vss.spec.policy.security.macChanges
                if mac_change != desired_values:
                    vss.spec.policy.security.macChanges = desired_values
                    context.host_ref.configManager.networkSystem.UpdateVirtualSwitch(
                        vswitchName=vss.name, spec=vss.spec
                    )
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def _get_non_compliant_configs(self, all_vss_pg_mac_change_configs, desired_values: bool) -> List:
        """Helper method to get non_compliant configs in the current and report current configs and desired configs.

        :param desired_values: Desired value for mac change on pg on vss.
        :type desired_values: boolean
        :return: Return a list of non_compliance mac change configs on pg on vss as current_configs.
        :rtype: list
        """

        non_compliant_configs = [
            vss_pg_mac_change_config
            for vss_pg_mac_change_config in all_vss_pg_mac_change_configs
            if vss_pg_mac_change_config[MAC_CHANGE_ACCEPT] != desired_values
        ]

        return non_compliant_configs

    def check_compliance(self, context: HostContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: ESX context instance.
        :type context: HostContext
        :param desired_values: Desired values for rulesets.
        :type desired_values: Any
        :return: Dict of status and list of current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance for mac change configs on pg on vss")
        all_vss_pg_mac_change_configs, errors = self.get(context=context)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs = self._get_non_compliant_configs(
            all_vss_pg_mac_change_configs=all_vss_pg_mac_change_configs, desired_values=desired_values
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
