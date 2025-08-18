import json
import logging
from typing import Dict, Tuple, List, Any

import requests

from config_modules_vmware.framework.auth.contexts.vidm_context import VidmContext
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
    | Config Title - Placeholder title for VIDM DNS control

    """

    metadata = ControllerMetadata(
        name="dns",  # controller names
        path_in_schema="compliance_config.vidm.dns",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for VIDM DNS control",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[VidmContext.ProductEnum.VIDM],  # product from enum in VidmContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    http_headers = None

    @staticmethod
    def _update_dns(dns_servers: List[Any]) -> bool:
        """
        Add DNS server.
        :param server: DNS server.
        :type server: str
        :return: True
        :rtype: bool
        """
        logger.info(f"Adding dns servers {dns_servers}")
        logger.info("performing backup of /etc/resolv.conf")
        utils.run_shell_cmd(f"cp /etc/resolv.conf /etc/resolv_backup.conf.bak")

        logger.info("updating /etc/resolv.conf")

        fileArray = open("/etc/resolv.conf", "r")

        with open("/etc/resolv.conf", "r") as f:
            lines = f.readlines()
        with open("/etc/resolv.conf", "w") as f:
            for line in lines:
                if line.startswith("#"):
                    f.write(line)
            
            for dns_server in dns_servers:
                f.write("nameserver " + dns_server + "\n")   
            f.close()

        return True

    def get(self, context: VidmContext) -> Tuple[Dict, List[Any]]:
        """
        Get DNS config from vidm.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: VIDM context
        :type context: VidmContext
        :return: Tuple of Dict containing dns servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting DNS servers.")
        errors = []
        try:
            dns_name_array = []
            fileArray = open("/etc/resolv.conf", "r")
            for dnsline in fileArray.readlines():  
                if dnsline.startswith("nameserver"):
                    logger.info("dnsline find carriage return: " + str(dnsline.index("\n")))
                    dns_name_array.append(dnsline.replace("nameserver ", "").replace("\n", ""))

            logger.info(f"dns_name_array: {dns_name_array}")

        except Exception as e:
            logger.exception(f"Exception retrieving dns value - {e}")
            errors.append(str(e))
            dns_name_array = []

        return {"servers": dns_name_array}, errors

    def check_compliance(self, context: VidmContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: VIDM product context instance.
        :type context: VidmContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # vidm only needs servers for DNS control
        desired_servers = desired_values.get("servers", [])
        logger.info(f"desired_values.get {desired_servers}")
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values)

    def set(self, context: VidmContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set DNS config in VIDM.
        This will delete any existing DNS entries and create the new desired ones as each DNS entry requires a unique name associated with it.

        | Sample desired state for DNS.

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: VIDM context instance.
        :type context: VidmContext
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

            logger.debug(f"Current VIDM DNS servers: {current_dns_servers}")
            logger.debug(f"Desired VIDM DNS servers: {desired_dns_servers}")

            if (current_dns_servers != desired_dns_servers):
                self._update_dns(desired_dns_servers)

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting dns value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: VidmContext, desired_values: Any) -> Dict:
        """Remediate current DNS configuration drifts.

        :param context: VIDM context instance.
        :type context: VidmContext
        :param desired_values: Desired values for DNS control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # vidm only needs servers for DNS control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
