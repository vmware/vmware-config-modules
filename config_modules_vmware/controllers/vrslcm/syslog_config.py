import json
import logging
from typing import Dict, Tuple, List, Any

import requests

from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

class SyslogConfig(BaseController):
    """Manage SYSLOG config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for vRealize Suite LCM SYSLOG control

    """

    metadata = ControllerMetadata(
        name="syslog",  # controller name
        path_in_schema="compliance_config.vrslcm.syslog",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for vRealize Suite LCM SYSLOG control",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[VrslcmContext.ProductEnum.VRSLCM],  # product from enum in VrslcmContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    http_headers = None

    def _call_syslog_api(self, hostname: str, http_method: str, server: str = None, port: int = None, protocol: str = None) -> dict:
        """
        Call SYSLOG API.

        :param hostname: Hostname of the server.
        :type hostname: str
        :param name: SYSLOG server name.
        :type name: str
        :param server: SYSLOG server IP.
        :type server: str
        :param http_method: the http operation (GET/POST/DELETE).
        :type http_method: str
        :return: response body
        :rtype: dict
        """
        body_template = {'hostname':'','port':0,'protocol':''}
        logger.info(f"Calling syslog server api operation: {http_method} server: {server} protocol: {protocol} port: {port}")
        if server and protocol and port:
            request_body = {"hostName":server,"portNumber":port,"protocol":protocol, "enabled":True,"bundleFilePath":"","sslTrustAcceptAny":True,"sslTrustAcceptTrusted":True,"sslCommonName":"","reconnect":"30","maxBufferSize":"2000"}
            logger.info("request_body: " + str(request_body))
        else:
            request_body = None

        if not self.http_headers:
            self.http_headers = aria_auth.get_http_headers()
        syslog_query_response = requests.request(
            http_method,
            f"https://{hostname}/lcm/lcops/api/v2/settings/log-insight-agent",
            headers=self.http_headers,
            data=json.dumps(request_body),
            verify=False,
            timeout=60,
        )
        syslog_query_response.raise_for_status()
        syslog_query_response_body = syslog_query_response.json()
        logger.info("syslog_query_response_body: " + str(syslog_query_response_body))
        logger.info("body_template: " + str(body_template))

        if http_method == "GET":
            body_template['hostname'] = syslog_query_response_body["hostName"]
            try:
                body_template['port'] = int(syslog_query_response_body["portNumber"])
            except Exception as e:
                body_template['port'] = 0
            body_template['protocol'] = syslog_query_response_body["protocol"]

        syslog_query_response_body = body_template

        logger.debug(f"SYSLOG query response body: {syslog_query_response_body}")
        return syslog_query_response_body

    def _convert_syslog_mapping(self, input: str) -> str:
        output = input
        if (input.lower() in ["udp", "tls", "tcp"]):
            output = "syslog"

        return output

    def get(self, context: VrslcmContext) -> Tuple[Dict, List[Any]]:
        """
        Get SYSLOG config from VrsLcm.

        | Sample get output

        .. code-block:: json

            {
              "syslog": {"hostName":"fqdn","portNumber":"9543","protocol":"CFAPI"}
            }

        :param context: vRealize suite LCM context
        :type context: VrslcmContext
        :return: Tuple of Dict containing syslog servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting SYSLOG syslog.")
        errors = []
        try:
            syslog_query_response = self._call_syslog_api(context.hostname, "GET")
            logger.info(f"SYSLOG query response: {syslog_query_response}")
            syslog_query_response
            syslog_servers = []
            syslog_servers.append(syslog_query_response)
        except Exception as e:
            logger.exception(f"Exception retrieving syslog values - {e}")
            errors.append(str(e))
            syslog_servers = []
        return {"servers": syslog_servers}, errors

    def check_compliance(self, context: VrslcmContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: vRealize suite LCM product context instance.
        :type context: VrslcmContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # vrslcm only needs servers for SYSLOG control
        # vrslcm only needs servers for SYSLOG control
        modified_desired_values = desired_values.get("servers", [])[0]
        #created a mapping, since the only supported protocols for VRSLCM are CFAPI and SYSLOG.  
        logger.info("modified_desired_values protocol: " + modified_desired_values["protocol"])
        modified_desired_values["protocol"] = self._convert_syslog_mapping(modified_desired_values["protocol"])
        logger.info("protocol: " + modified_desired_values["protocol"])

        desired_values = {"servers": [modified_desired_values]}
        return super().check_compliance(context, desired_values)

    def set(self, context: VrslcmContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set SYSLOG config in vRealize suite LCM.
        This will delete any existing SYSLOG entries and create the new desired ones as each SYSLOG entry requires a unique name associated with it.

        | Sample desired state for SYSLOG.

        .. code-block:: json

            {
              "syslog": {"hostName":"fqdn","portNumber":"9543","protocol":"CFAPI"}
            }

        :param context: vRealize suite LCM context instance.
        :type context: VrslcmContext
        :param desired_values: Desired value for the SYSLOG config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting SYSLOG control config for audit.")
        errors = []
        try:
            syslog_query_response = self._call_syslog_api(context.hostname, "GET")
            logger.debug(f"Current SYSLOG servers: {syslog_query_response}")
            desired_syslog_servers = desired_values.get("servers", [])[0]

            desired_syslog_servers["protocol"] = self._convert_syslog_mapping(desired_syslog_servers["protocol"])
            logger.debug(f"Desired SYSLOG servers: {desired_syslog_servers}")

            if (syslog_query_response != desired_syslog_servers):
                logger.info(f"Updating SYSLOG entry: {syslog_query_response} with : {desired_syslog_servers}")

                self._call_syslog_api(context.hostname, "POST", desired_syslog_servers["hostname"], desired_syslog_servers["port"], desired_syslog_servers["protocol"])

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting syslog value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: VrslcmContext, desired_values: Any) -> Dict:
        """Remediate current SYSLOG configuration drifts.

        :param context: vRealize suite LCM context instance.
        :type context: VrslcmContext
        :param desired_values: Desired values for SYSLOG control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # vrslcm only needs servers for SYSLOG control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
