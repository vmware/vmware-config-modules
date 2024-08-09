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
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))

USERS_TO_BE_IGNORED = ["nsx-user", "da-user", "nsxuser", "mux_user", "lldpVim-user"]


class LockdownModeExceptionUsers(BaseController):
    """ESXi controller to get/set exception user list for lockdown mode.

    | Config Id - 125
    | Config Title - The ESXi host must verify the exception users list for lockdown mode.

    """

    metadata = ControllerMetadata(
        name="lockdown_mode_exception_users",  # controller name
        path_in_schema="compliance_config.esxi.lockdown_mode_exception_users",
        # path in the schema to this controller's definition.
        configuration_id="125",  # configuration id as defined in compliance kit.
        title="The ESXi host must verify the exception users list for lockdown mode",
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
        """Get lockdown mode exception users list for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of lockdown mode exception users list and a list of errors if any..
        :rtype: Tuple
        """
        logger.info("Getting lockdown mode exception users list for esxi host.")
        errors = []
        lockdown_mode_exception_users = []
        try:
            lockdown_mode_exception_users = context.host_ref.configManager.hostAccessManager.QueryLockdownExceptions()
            logger.debug(f"Lockdown mode exception users for the esxi host: {lockdown_mode_exception_users}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return lockdown_mode_exception_users, errors

    def set(self, context: HostContext, desired_values: list) -> Tuple[RemediateStatus, List[str]]:
        """Set lockdown mode exception users list for esxi host. These users should be valid users which are
        already configured on the host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: List of lockdown mode exception users.
        :type desired_values: list
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting lockdown mode exception users list for esxi host.")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            context.host_ref.configManager.hostAccessManager.UpdateLockdownExceptions(desired_values)
            logger.debug(f"Updated exception users with: {desired_values}")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context: HostContext, desired_values: list) -> Dict:
        """Check compliance of current configuration against provided desired values.
        USERS_TO_BE_IGNORED will be filtered out from current and desired values before running check compliance.

        :param context: Product context instance.
        :type context: HostContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: list
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance for lockdown mode exception users.")

        current_values, errors = self.get(context=context)
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # Ignore the users listed in USERS_TO_BE_IGNORED for check compliance
        desired_values = [user for user in desired_values if user not in USERS_TO_BE_IGNORED]
        current_values = [user for user in current_values if user not in USERS_TO_BE_IGNORED]

        # If no errors seen, compare the current and desired values. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_users, desired_users = Comparator.get_non_compliant_configs(current_values, desired_values)
        if current_users or desired_users:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_users,
                consts.DESIRED: desired_users,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
