import logging
from typing import Dict, Tuple, List, Any

from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class InactiveTimeoutWebuiConfig(BaseController):
    """Manage inactive timeout webui with get and set methods.
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - Manage inactive webui timeout.

    """

    metadata = ControllerMetadata(
        name="inactive_timeout_webui",  # controller name
        path_in_schema="compliance_config.nsxt_manager.inactive_timeout_webui",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Manage NSXT node UI timer desired Config.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[
            NSXTManagerContext.ProductEnum.NSXT_MANAGER
        ],  # product from enum in NSXTManagerContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsx_manager"],  # location where functional tests are run.
        #functional_test_targets=["nsx_manager", "nsx_edge"],  # location where functional tests are run.
    )

    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get UI timer config from NSX.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["time.vmware.com", "time.google.com"]
            }

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing ntp servers and a list of error messages.
        :rtype: Tuple

        """
        logger.info("Getting UI Timer.")
        errors = []
        uitimer = None
        try:
            command_output = utils.run_shell_cmd("su -c 'get service http' admin")[0]

            for item in command_output.split('\n'):
                if "Session timeout:" in item:
                    uitimer = item.split("Session timeout:")[1].replace (" ", "")
        except Exception as e:
            logger.exception(f"Exception retrieving uitimer value - {e}")
            errors.append(str(e))
        return {"timeout": int(uitimer)}, errors

    def check_compliance(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.
        [Note: This needs to be moved as part of framework input validation once available.]

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        
        #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
        errors = []
        if not nsx_utils.isLeader(context):
            errors = [nsx_utils.ERROR_MSG_NOT_VIP]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}

        return super().check_compliance(context, desired_values)

    def set(self, context: NSXTManagerContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set Web UI Timer value in NSX.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for UI timer.

        .. code-block:: json

            {
              "timeout": 1200
            }
set_session_timer = f"su -c 'set service http session-timeout {str(config)}' admin"   
    result = __salt__["cmd.run"](set_session_timer)
            


        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired value for web UI timer. Dict with key "timeout".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting WEB UI timeout value.")
        errors = []
        try:
            desired_timer = desired_values["timeout"]
            command_output = utils.run_shell_cmd(f"su -c 'set service http session-timeout {str(desired_timer)}' admin")
            if self.check_compliance(context, desired_values).get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Failed to update UI timeout")
            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting UI timer value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current UI timer drift.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for NTP control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # NSX ui timer
        return super().remediate(context, desired_values)
