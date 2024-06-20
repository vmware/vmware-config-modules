# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import requests

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class DnsConfig(BaseController):
    """Manage DNS config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for vRealize Suite LCM DNS control

    """

    metadata = ControllerMetadata(
        name="dns",  # controller name
        path_in_schema="compliance_config.vrslcm.dns",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for vRealize Suite LCM DNS control",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VRSLCM],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    http_headers = None

    def _call_dns_api(self, hostname: str, http_method: str, name: str = None, server: str = None) -> dict:
        """
        Call DNS API.

        :param hostname: Hostname of the server.
        :type hostname: str
        :param name: DNS server name.
        :type name: str
        :param server: DNS server IP.
        :type server: str
        :param http_method: the http operation (GET/POST/DELETE).
        :type http_method: str
        :return: response body
        :rtype: dict
        """
        logger.info(f"Calling dns server api operation: {http_method} name: {name} server: {server}")
        if name and server:
            request_body = {"name": name, "hostName": server}
        else:
            request_body = None

        if not self.http_headers:
            self.http_headers = aria_auth.get_http_headers()
        dns_query_response = requests.request(
            http_method,
            f"https://{hostname}/lcm/lcops/api/v2/settings/dns",
            headers=self.http_headers,
            data=json.dumps(request_body),
            verify=False,
            timeout=60,
        )
        dns_query_response.raise_for_status()
        dns_query_response_body = dns_query_response.json()
        logger.debug(f"DNS query response body: {dns_query_response_body}")
        return dns_query_response_body

    def get(self, context: VrslcmContext) -> Tuple[Dict, List[Any]]:
        """
        Get DNS config from VrsLcm.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: vRealize suite LCM context
        :type context: VrslcmContext
        :return: Tuple of Dict containing dns servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting DNS servers.")
        errors = []
        try:
            dns_query_response = self._call_dns_api(context.hostname, "GET")
            logger.debug(f"DNS query response: {dns_query_response}")
            dns_servers = []
            for dns_server_item in dns_query_response:
                dns_servers.append(dns_server_item.get("hostName"))
        except Exception as e:
            logger.exception(f"Exception retrieving dns values - {e}")
            errors.append(str(e))
            dns_servers = []
        return {"servers": dns_servers}, errors

    def check_compliance(self, context: VrslcmContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: vRealize suite LCM product context instance.
        :type context: VrslcmContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # vrslcm only needs servers for DNS control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values)

    def set(self, context: VrslcmContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set DNS config in vRealize suite LCM.
        This will delete any existing DNS entries and create the new desired ones as each DNS entry requires a unique name associated with it.

        | Sample desired state for DNS.

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: vRealize suite LCM context instance.
        :type context: VrslcmContext
        :param desired_values: Desired value for the DNS config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting DNS control config for audit.")
        errors = []
        try:
            dns_query_response = self._call_dns_api(context.hostname, "GET")
            logger.debug(f"Current DNS servers: {dns_query_response}")
            desired_dns_servers = desired_values.get("servers", [])
            logger.debug(f"Desired DNS servers: {desired_dns_servers}")

            for dns_server_item in dns_query_response:
                logger.info(f"Deleting DNS entry: {dns_server_item}")
                self._call_dns_api(context.hostname, "DELETE", dns_server_item["name"], dns_server_item["hostName"])

            for i in range(0, len(desired_dns_servers)):
                server = desired_dns_servers[i]
                # replicating the implementation from aslcm_dns salt module
                name = "dns" + (str(i) if i != 0 else "")
                logger.info(f"Adding DNS entry name: {name} server: {server}")
                self._call_dns_api(context.hostname, "POST", name, server)

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting dns value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: VrslcmContext, desired_values: Any) -> Dict:
        """Remediate current DNS configuration drifts.

        :param context: vRealize suite LCM context instance.
        :type context: VrslcmContext
        :param desired_values: Desired values for DNS control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # vrslcm only needs servers for DNS control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
