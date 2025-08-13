import json
import logging
from typing import Dict, Tuple, List, Any

import requests

from config_modules_vmware.framework.auth.contexts.vro_context import VroContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


class NtpConfig(BaseController):
    """Manage NTP config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for VRO NTP control

    """

    metadata = ControllerMetadata(
        name="ntp",  # controller name
        path_in_schema="compliance_config.vro.ntp",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for VRO NTP control",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[VroContext.ProductEnum.VRO],  # product from enum in VroContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    http_headers = None

    @staticmethod
    def _update_ntp_servers(ntp_servers: Any) -> bool:
        """
        Add NTP server.
        :param server: NTP server.
        :type server: str
        :return: True
        :rtype: bool
        """
        cmd_response = ""

        ntp_servers_string = ','.join(map(repr,ntp_servers))

        cmd_text = "vracli ntp systemd --local --set {ntp_servers_string}".format(ntp_servers_string=ntp_servers_string) 
        logger.info("running command: " + cmd_text)

        utils.run_shell_cmd(cmd_text)
        return True

    def get(self, context: VroContext) -> Tuple[Dict, List[Any]]:
        """
        Get NTP config from vro.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["time.amer.net"]
            }

        :param context: vRealize suite VRO context
        :type context: VroContext
        :return: Tuple of Dict containing ntp servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting NTP servers.")
        errors = []
        ntp_servers = []
        try:
            cmd_response = utils.run_shell_cmd("vracli ntp show-config")[0] 

            response_lines = cmd_response.split("\n")
            for response_line in response_lines:
                if "ntp_servers: " in response_line:
                    string_list = response_line.split(":")[1].strip().replace("'", '"')
                    ntp_servers = json.loads(string_list)
                    break  
        except Exception as e:
            logger.exception(f"Exception retrieving ntp values - {e}")
            errors.append(str(e))
            ntp_servers = []
        return {"servers": ntp_servers}, errors

    def check_compliance(self, context: VroContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: VRO product context instance.
        :type context: VroContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # vro only needs servers for NTP control
        logger.info("Checking compliance")
        desired_servers = desired_values.get("servers", [])
        logger.info(f"desired_values.get {desired_servers}")
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values)

    def set(self, context: VroContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set NTP config in VRO.
        This will delete any existing NTP entries and create the new desired ones as each NTP entry requires a unique name associated with it.

        | Sample desired state for NTP.

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: VRO context instance.
        :type context: VroContext
        :param desired_values: Desired value for the NTP config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting NTP control config for audit.")
        errors = []
        try:
            current_ntp_servers, get_errors = self.get(context)
            if get_errors:
                raise Exception(f"Exception getting current NTP servers: {get_errors[0]}")

            current_ntp_servers = current_ntp_servers.get("servers", [])
            desired_ntp_servers = desired_values.get("servers", [])

            logger.debug(f"Current VRO NTP servers: {current_ntp_servers}")
            logger.debug(f"Desired VRO NTP servers: {desired_ntp_servers}")

            #if desired ntp server is empty, disable ntp
            if len(desired_ntp_servers) == 0:
                logger.debug(f"no desired ntp servers, doing nothing")
            else:
                cmd_response = self._update_ntp_servers(desired_ntp_servers)    

            if self.check_compliance(context, desired_values).get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Failed to update NTP servers")

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting ntp value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: VroContext, desired_values: Any) -> Dict:
        """Remediate current NTP configuration drifts.

        :param context: VRO context instance.
        :type context: VroContext
        :param desired_values: Desired values for NTP control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # vro only needs servers for NTP control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
