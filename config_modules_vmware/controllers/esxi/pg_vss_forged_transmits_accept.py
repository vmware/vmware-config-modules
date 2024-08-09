# Copyright 2024 Broadcom. All Rights Reserved.
import logging
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
FORGED_TRANSMITS_ACCEPT = "forged_transmits_accept"


class PgVssForgedTransmitsAccept(BaseController):
    """ESXi controller to get/set forged transmits security policy configuration on vSS portgroup.

    | Config Id - 160
    | Config Title - All port groups on standard switches must be configured to reject forged transmits.

    """

    metadata = ControllerMetadata(
        name="pg_vss_forged_transmits_accept",  # controller name
        path_in_schema="compliance_config.esxi.pg_vss_forged_transmits_accept",
        # path in the schema to this controller's definition.
        configuration_id="160",  # configuration id as defined in compliance kit.
        title="All port groups on standard switches must be configured to reject forged transmits",
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

    def _get_non_compliant_configs(self, all_vss_pg_forged_transmits_configs, desired_values: bool) -> List:
        """Helper method to get non_compliant configs in the current and report current configs and desired configs.

        :param desired_values: Desired value for forged transmits on pg on vss.
        :type desired_values: bool
        :return: Return a list of non_compliance forged transmits configs on pg on vss as current_configs.
        :rtype: list
        """

        non_compliant_configs = [
            vss_pg_forged_transmits_config
            for vss_pg_forged_transmits_config in all_vss_pg_forged_transmits_configs
            if vss_pg_forged_transmits_config[FORGED_TRANSMITS_ACCEPT] != desired_values
        ]

        return non_compliant_configs

    def get(self, context: HostContext) -> Tuple[list, List[str]]:
        """Get vSS portgroup forged transmits security policy configuration for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of a list of all pg vss configs and a list of errors if any..
        :rtype: Tuple
        """
        logger.info("Getting vSS portgroup forged transmits security policy configuration for esxi.")
        all_vss_pg_forged_transmits_configs = []
        errors = []
        try:
            all_vss = context.host_ref.config.network.vswitch
            for vss in all_vss:
                forged_transmits = vss.spec.policy.security.forgedTransmits
                vss_forged_transmits = {VSWITCH_NAME: vss.name, FORGED_TRANSMITS_ACCEPT: forged_transmits}
                all_vss_pg_forged_transmits_configs.append(vss_forged_transmits)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return all_vss_pg_forged_transmits_configs, errors

    def set(self, context: HostContext, desired_values: bool) -> Tuple[RemediateStatus, List[str]]:
        """Set vSS portgroup forged transmits security policy configuration for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: True to accept or False to reject.
        :type desired_values: bool
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting vSS portgroup forged transmits security policy configuration for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            all_vss = context.host_ref.config.network.vswitch
            for vss in all_vss:
                forged_transmits = vss.spec.policy.security.forgedTransmits
                if forged_transmits != desired_values:
                    vss.spec.policy.security.forgedTransmits = desired_values
                    context.host_ref.configManager.networkSystem.UpdateVirtualSwitch(
                        vswitchName=vss.name, spec=vss.spec
                    )
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context: HostContext, desired_values: bool) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: ESX context instance.
        :type context: HostContext
        :param desired_values: True to accept or False to reject forged transmits policy.
        :type desired_values: bool
        :return: Dict of status and list of current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance for forged transmits security policy configs on pg on vss")
        all_vss_pg_forged_transmits_configs, errors = self.get(context=context)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs = self._get_non_compliant_configs(
            all_vss_pg_forged_transmits_configs=all_vss_pg_forged_transmits_configs, desired_values=desired_values
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
