import json
import logging
from typing import Dict, Tuple, List, Any

import requests

from config_modules_vmware.framework.auth.contexts.vro_context import VroContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


class DnsConfig(BaseController):
    """Manage DNS config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for VRO DNS control

    """

    metadata = ControllerMetadata(
        name="dns",  # controller name
        path_in_schema="compliance_config.vro.dns",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for VRO DNS control",
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
    def _update_dns(dns_servers: Dict) -> bool:
        """
        Add DNS server.
        :param server: DNS server.
        :type server: str
        :return: True
        :rtype: bool
        """
        logger.info(f"Adding dns servers {dns_servers}")
        cmd_response = ""
        dnsserver2 = ""

        dnsserver1 = dns_servers[0]

        if len(dns_servers) >= 2: 
            dnsserver2 = "," + dns_servers[1]

        cmd_text = f"vracli network dns set --servers {dnsserver1}{dnsserver2}".format(dnsserver1=dnsserver1, dnsserver2=dnsserver2) 
        logger.info(f"running command: {cmd_text}")

        utils.run_shell_cmd(cmd_text)

        return True

    def get(self, context: VroContext) -> Tuple[Dict, List[Any]]:
        """
        Get DNS config from vro.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: VRO context
        :type context: VroContext
        :return: Tuple of Dict containing dns servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting DNS servers.")
        errors = []
        try:
            dns_name_array = []
            cmd_text = "vracli network dns status" 
            logger.info(f"running command: {cmd_text}")
            cmd_response = utils.run_shell_cmd(cmd_text)[0]
            dns_config_lines = cmd_response.split("DNS configuration for node ")
            for dns_config_line in dns_config_lines:
                if context._hostname in dns_config_line:
                    parsed_response = dns_config_line.split(":")
                    string_list = parsed_response[1].strip().replace("'", '"')
                    dns_name_array = json.loads(string_list)
                    logger.info("dns_servers: " + str(dns_name_array))
                    break

            logger.info(f"dns_name_array: {dns_name_array}")

        except Exception as e:
            logger.exception(f"Exception retrieving dns value - {e}")
            errors.append(str(e))
            dns_name_array = []

        return {"servers": dns_name_array}, errors

    def check_compliance(self, context: VroContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: VRO product context instance.
        :type context: VroContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # vro only needs servers for DNS control
        desired_servers = desired_values.get("servers", [])
        logger.info(f"desired_values.get {desired_servers}")
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values)

    def set(self, context: VroContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set DNS config in VRO.
        This will delete any existing DNS entries and create the new desired ones as each DNS entry requires a unique name associated with it.

        | Sample desired state for DNS.

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: VRO context instance.
        :type context: VroContext
        :param desired_values: Desired value for the DNS config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting DNS control config for audit.")
        errors = []
        try:
            current_dns_servers, get_errors = self.get(context)
            if get_errors:
                raise Exception(f"Exception getting current DNS servers: {get_errors[0]}")

            current_dns_servers = current_dns_servers.get("servers", [])
            desired_dns_servers = desired_values.get("servers", [])

            logger.debug(f"Current VRO DNS servers: {current_dns_servers}")
            logger.debug(f"Desired VRO DNS servers: {desired_dns_servers}")

            self._update_dns(desired_dns_servers)

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting dns value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: VroContext, desired_values: Any) -> Dict:
        """Remediate current DNS configuration drifts.

        :param context: VRO context instance.
        :type context: VroContext
        :param desired_values: Desired values for DNS control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # vro only needs servers for DNS control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
