import json
import logging
from typing import Dict, Tuple, List, Any

import requests, time

from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.aria_suite import vrli_agent_utils
from config_modules_vmware.framework.clients.common import consts

logger = logging.getLogger(__name__)

class SyslogConfig(BaseController):
    """Manage SYSLOG config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for sddc manager SYSLOG control

    """

    metadata = ControllerMetadata(
        name="syslog",  # controller name
        path_in_schema="compliance_config.monitoring.syslog",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for SDDC_MANAGER SYSLOG control",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[SDDCManagerContext.ProductEnum.SDDC_MANAGER],  # product from enum in SDDCManagerContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    http_headers = None

    def get(self, context: SDDCManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get SYSLOG config from SDDC.

        | Sample get output

        .. code-block:: json

            {
              "syslog": {"hostName":"127.0.0.1","portNumber":"9000","protocol":"CFAPI"}
            }

        :param context: SDDC context
        :type context: SDDCManagerContext
        :return: Tuple of Dict containing syslog servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting SYSLOG servers.")
        errors = []
        try:
            syslog_servers = []
            syslog_servers, errors = vrli_agent_utils.get_vrli_agent_config()
        
        except Exception as e:
            logger.exception(f"Exception retrieving syslog value - {e}")
            errors.append(str(e))
            syslog_servers = []

        return {"servers": syslog_servers}, errors

    def check_compliance(self, context: SDDCManagerContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: SDDC product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # sddc only needs servers for SYSLOG control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values)

    def set(self, context: SDDCManagerContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set SYSLOG config in SDDC.
        This will delete any existing SYSLOG entries and create the new desired ones as each SYSLOG entry requires a unique name associated with it.

        | Sample desired state for SYSLOG.

        .. code-block:: json

            {
              "syslog": {"hostName":"127.0.0.1","portNumber":"9000","protocol":"CFAPI"}
            }

        :param context: SDDC Manager context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired value for the SYSLOG config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting SYSLOG control config for audit.")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            status, errors = vrli_agent_utils.set_vrli_agent_config(desired_values)

        except Exception as e:
            logger.exception(f"Exception setting syslog value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: SDDCManagerContext, desired_values: Any) -> Dict:
        """Remediate current SYSLOG configuration drifts.

        :param context: SDDC_MANAGER context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for SYSLOG control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # sddc manager only needs servers for SYSLOG control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
