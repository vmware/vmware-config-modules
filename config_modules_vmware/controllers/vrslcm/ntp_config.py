import json
import logging
from typing import Dict, Tuple, List, Any

import requests

from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.aria_suite import aria_auth, aria_consts
from config_modules_vmware.framework.utils.comparator import Comparator
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
import time

logger = LoggerAdapter(logging.getLogger(__name__))


class NtpConfig(BaseController):
    """Manage NTP config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for vRealize Suite LCM NTP control

    """

    metadata = ControllerMetadata(
        name="ntp",  # controller name
        path_in_schema="compliance_config.vrslcm.ntp",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for vRealize Suite LCM NTP control",
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

    def _call_ntp_api(self, hostname: str, http_method: str, name: str = None, server: str = None) -> dict:
        """
        Call NTP API.

        :param hostname: Hostname of the server.
        :type hostname: str
        :param name: NTP server name.
        :type name: str
        :param server: NTP server IP.
        :type server: str
        :param http_method: the http operation (GET/POST/DELETE).
        :type http_method: str
        :return: response body
        :rtype: dict
        """
        logger.info(f"Calling ntp server api operation: {http_method} name: {name} server: {server}")
        if name and server:
            request_body = {"name": name, "hostName": server}
        else:
            request_body = None

        if not self.http_headers:
            self.http_headers = aria_auth.get_http_headers()
        ntp_query_response = requests.request(
            http_method,
            f"https://{hostname}/lcm/lcops/api/v2/settings/ntp-servers",
            headers=self.http_headers,
            data=json.dumps(request_body),
            verify=False,
            timeout=60,
        )
        ntp_query_response.raise_for_status()
        ntp_query_response_body = ntp_query_response.json()
        logger.debug(f"NTP query response body: {ntp_query_response_body}")
        return ntp_query_response_body

    def _get_environment_product_ntp_values(self, hostname: str, http_method: str, child_product: str) -> bool:
        """
        Call environment API.

        :param hostname: Hostname of the server.
        :type hostname: str
        :param http_method: the http operation (GET/POST/DELETE).
        :type http_method: str
        :param child_product: the child product to process, default vrslcm.
        :type child_product: str
        :return: response body
        :rtype: dict
        """

        logger.info(f"_get_environment_product_ntp_values: hostname: {hostname}, http_method: {http_method}, child_product: {child_product}")

        if not self.http_headers:
            self.http_headers = aria_auth.get_http_headers()
        ntp_query_response = requests.request(
            http_method,
            f"https://{hostname}/lcm/lcops/api/v2/environments?status=COMPLETED",
            headers=self.http_headers,
            data="",
            verify=False,
            timeout=60
        )
        ntp_query_response.raise_for_status()
        ntp_query_response_body = ntp_query_response.json()

        ntp_list = ["PRODUCT_NOT_FOUND"]
        child_appliance_hostnames = []
        for environment in ntp_query_response_body:
            for product in environment["products"]:
                if product["id"] == child_product.lower():
                    logger.info(f"child_product found! {child_product}")

                    #get child appliance names
                    for node in product["nodes"]:
                        logger.info(f"node_in_nodes: {node['properties']['hostName']} ")
                        child_appliance_hostnames.append(node["properties"]["hostName"])

                    if 'ntp' in product["properties"]:
                        logger.info(f"ntp settings found at product level!")
                        ntp_list = product["properties"]["ntp"].split(",")
                        break
                    elif 'ntp' in environment["infrastructure"]["properties"]:
                        #some vrslcm instances are not returning ntp instances at product level.  grabbing from environment
                        logger.info(f"ntp settings not found at product level, getting from infrastructure.properties!")
                        ntp_list = environment["infrastructure"]["properties"]["ntp"].split(",")   
                        break
                    else:
                        logger.info(f"ntp servers not found at product or environment level!")
                        ntp_list = ["ntp not found!"]

            logger.info(f"ntp_list: {ntp_list}")
            logger.info(f"child_appliance_hostnames: {child_appliance_hostnames}")
        return ntp_list, child_appliance_hostnames

    def _set_ntp_values_for_product(self, hostname: str, child_product: str, desired_values: dict) -> dict:
        """
        Call environment API.

        :param hostname: Hostname of the server.
        :type hostname: str
        :param name: child product
        :type name: str
        :param desired_values: Desired value for the NTP config. Dict with keys "servers".
        :type desired_values: dict
        :return: response body
        :rtype: dict
        """
        product_found = False
        child_product = child_product.lower()
        logger.info(f"_set_ntp_values_for_product: hostname: {hostname}, child_product: {child_product}")

        if not self.http_headers:
            self.http_headers = aria_auth.get_http_headers()
        ntp_query_response = requests.request(
            "GET",
            f"https://{hostname}/lcm/lcops/api/v2/environments?status=COMPLETED",
            headers=self.http_headers,
            data="",
            verify=False,
            timeout=60
        )
        ntp_query_response.raise_for_status()
        ntp_query_response_body = ntp_query_response.json()
        logger.info(f"Environment NTP query response body: {ntp_query_response_body}")

        environmentId = ""
        for environment in ntp_query_response_body:
            for product in environment["products"]:
                if product["id"] == child_product:
                    product_found = True
                    environment_name = environment["environmentName"]
                    logger.info(f"environment: {environment_name} found for child_product: {child_product}")
                    environmentId = environment["environmentId"]
                    break

        if product_found is True:
            request_body =  {
                                "ntpServers": ",".join(desired_values),
                                "preValidate": False,
                                "timeSyncMode": "ntp"
                            }

            logger.info(f"request_body: {json.dumps(request_body)}")

            update_response = requests.request(
                "POST",
                f"https://{hostname}/lcm/lcops/api/v2/environments/{environmentId}/products/{child_product}/ntpConfig",
                headers=self.http_headers,
                data=json.dumps(request_body),
                verify=False,
                timeout=60
            )

            update_response_body = update_response.json()
            request_id = update_response_body['requestId']
            logger.info(f"request_id: {request_id}")

            self._wait_for_request(hostname, request_id)
        else:
            logger.info(f"child product: '{child_product}' not found!")

        return product_found

    def _wait_for_request(self, hostname: str, request_id: str):
        if not self.http_headers:
            self.http_headers = aria_auth.get_http_headers()

        for x in range(0, aria_consts.REQUEST_STATUS_WAIT_RETRY_NUMBER):
            time.sleep(aria_consts.REQUEST_STATUS_WAIT_TIME)
            request_query_response = requests.request(
                "GET",
                f"https://{hostname}/lcm/request/api/v2/requests/{request_id}",
                headers=self.http_headers,
                data="",
                verify=False,
                timeout=60
            )

            request_query_response = request_query_response.json()
            state = request_query_response['state']
            logger.info(f"state: {state}")
            if request_query_response['state'] == "COMPLETED":
                return True
            elif request_query_response['state'] == "FAILED":
                raise f"vrslcm request failed to set ntp"

        raise f"_wait_for_request timeout with waiting for {aria_consts.REQUEST_STATUS_WAIT_TIME} x {aria_consts.REQUEST_STATUS_WAIT_RETRY_NUMBER} of times"


    def get(self, context: VrslcmContext, desired_values: Any) -> Tuple[Dict, List[Any]]:
        """
        Get NTP config from VrsLcm.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["time.corp"]
            }

        :param context: vRealize suite LCM context
        :type context: VrslcmContext
        :param desired_values: Desired value for the NTP config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of Dict containing ntp servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting NTP servers.")
        errors = []
        child_appliance_hostnames = []
        child_product = ""
        try:
            child_product = desired_values.get("child_product", "VRSLCM")
            logger.info(f"child_product: {child_product}")
            
            if child_product == "VRSLCM":
                ntp_query_response = self._call_ntp_api(context.hostname, "GET")
                logger.info(f"NTP query response: {ntp_query_response}")
                ntp_servers = []
                for ntp_server_item in ntp_query_response:
                    ntp_servers.append(ntp_server_item.get("hostName"))
            else:
                ntp_query_response, child_appliance_hostnames = self._get_environment_product_ntp_values(context.hostname, "GET", child_product)
                logger.info(f"NTP query response: {ntp_query_response}")
                ntp_servers = []
                ntp_servers = ntp_query_response

        except Exception as e:
            logger.exception(f"Exception retrieving ntp values - {e}")
            errors.append(str(e))
            ntp_servers = []
        return {"servers": ntp_servers}, errors, child_appliance_hostnames

    def check_compliance(self, context: VrslcmContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance.")
        child_appliance_hostnames = []
        current_value, errors, child_appliance_hostnames = self.get(context=context, desired_values=desired_values)

        logger.info(current_value.get("servers", []))

        if current_value.get("servers", []) == ["PRODUCT_NOT_FOUND"]:
            child_product = {desired_values.get("child_product", "VRSLCM")}
            errors = [f"{child_product} child product does not exist in VRSLCM Instance"]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}

        desired_values = {"servers": desired_values.get("servers", [])}

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_non_compliant_configs, desired_non_compliant_configs = Comparator.get_non_compliant_configs(
            current_value, desired_values, comparator_option=self.comparator_option, instance_key=self.instance_key
        )
        if current_non_compliant_configs or desired_non_compliant_configs:
            if len(child_appliance_hostnames) > 0:
                result = {
                    consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                    consts.CURRENT: current_non_compliant_configs,
                    consts.DESIRED: desired_non_compliant_configs,   
                    aria_consts.CHILD_APPLIANCES: child_appliance_hostnames        
                }
            else:
                result = {
                    consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                    consts.CURRENT: current_non_compliant_configs,
                    consts.DESIRED: desired_non_compliant_configs,       
                }               

        else:
            if len(child_appliance_hostnames) > 0:
                result = {
                        consts.STATUS: ComplianceStatus.COMPLIANT,    
                        aria_consts.CHILD_APPLIANCES: child_appliance_hostnames,
                    }
            else:
                result = {
                        consts.STATUS: ComplianceStatus.COMPLIANT,   
                    }                

        return result

    def set(self, context: VrslcmContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set NTP config in vRealize suite LCM.
        This will delete any existing NTP entries and create the new desired ones as each NTP entry requires a unique name associated with it.

        | Sample desired state for NTP.

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: vRealize suite LCM context instance.
        :type context: VrslcmContext
        :param desired_values: Desired value for the NTP config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting NTP control config for audit.")
        errors = []
        try:

            desired_ntp_servers = desired_values.get("servers", [])
            logger.debug(f"Desired NTP servers: {desired_ntp_servers}")

            child_product = desired_values.get("child_product", "VRSLCM")
            logger.info(f"child_product: {child_product}")
            
            if child_product == "VRSLCM":
                ntp_query_response = self._call_ntp_api(context.hostname, "GET")
                logger.debug(f"Current NTP servers: {ntp_query_response}")

                for ntp_server_item in ntp_query_response:
                    logger.info(f"Deleting NTP entry: {ntp_server_item}")
                    self._call_ntp_api(context.hostname, "DELETE", ntp_server_item["name"], ntp_server_item["hostName"])

                for i in range(0, len(desired_ntp_servers)):
                    server = desired_ntp_servers[i]
                    # replicating the implementation from aslcm_ntp salt module
                    name = "ntp" + (str(i) if i != 0 else "")
                    logger.info(f"Adding NTP entry name: {name} server: {server}")
                    self._call_ntp_api(context.hostname, "POST", name, server)
            else:
                if self._set_ntp_values_for_product(context.hostname, child_product, desired_ntp_servers) is False: 
                    status = RemediateStatus.SKIPPED
                    errors = [f"{child_product}: product does not exist in VRSLCM Instance"]
                    return status, errors
                        
            #check if the updates remediated the drift.  
            check_compliance_val = self.check_compliance(context, desired_values)
            if check_compliance_val.get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Failed to update NTP servers")

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting ntp value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: VrslcmContext, desired_values: Any) -> Dict:
        """Remediate current configuration drifts.

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Running remediation.")

        # Call check compliance and check for current compliance status.
        compliance_response = self.check_compliance(context=context, desired_values=desired_values)

        child_appliances = compliance_response.get(aria_consts.CHILD_APPLIANCES, [])
        logger.info(f"remediation child_appliances: {child_appliances}")

        if (
            compliance_response.get(consts.STATUS) == ComplianceStatus.FAILED
            or compliance_response.get(consts.STATUS) == ComplianceStatus.ERROR
        ):
            # For compliance_status as "FAILED" or "ERROR", return FAILED with errors.
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: compliance_response.get(consts.ERRORS, []), aria_consts.CHILD_APPLIANCES: child_appliances}

        elif compliance_response.get(consts.STATUS) == ComplianceStatus.COMPLIANT:
            # For compliant_status as "COMPLIANT", return remediation as skipped.
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT], aria_consts.CHILD_APPLIANCES: child_appliances}

        elif compliance_response.get(consts.STATUS) == ComplianceStatus.SKIPPED:
            # For compliance_status as "SKIPPED", return remediation as SKIPPED since no remediation was performed.
            return {
                consts.STATUS: RemediateStatus.SKIPPED,
                consts.ERRORS: ["Remediation Skipped as Check compliance is SKIPPED"],
            }

        elif compliance_response.get(consts.STATUS) != ComplianceStatus.NON_COMPLIANT:
            # Raise exception for unexpected compliance status (other than FAILED, COMPLIANT, NON_COMPLIANT).
            raise Exception("Error during remediation. Unexpected compliant status found.")

        # Configs are non_compliant, call set to remediate them.
        status, errors = self.set(context=context, desired_values=desired_values)
        if not errors:
            if len(child_appliance_hostnames) > 0:
                result = {
                    consts.STATUS: status,
                    consts.OLD: compliance_response.get(consts.CURRENT),
                    consts.NEW: compliance_response.get(consts.DESIRED),
                    aria_consts.CHILD_APPLIANCES: child_appliances,
                }     
            else:
                result = {
                    consts.STATUS: status,
                    consts.OLD: compliance_response.get(consts.CURRENT),
                    consts.NEW: compliance_response.get(consts.DESIRED),
                }                            
        else:
            if status == RemediateStatus.SKIPPED:
                # ADD SKIPPED RESPONSE
                if len(child_appliance_hostnames) > 0:
                    result = {
                        consts.STATUS: RemediateStatus.SKIPPED,
                        consts.ERRORS: errors,
                        consts.CURRENT: compliance_response.get(consts.CURRENT),
                        consts.DESIRED: compliance_response.get(consts.DESIRED),
                        aria_consts.CHILD_APPLIANCES: child_appliances,
                    }
                else:
                    result = {
                        consts.STATUS: RemediateStatus.SKIPPED,
                        consts.ERRORS: errors,
                        consts.CURRENT: compliance_response.get(consts.CURRENT),
                        consts.DESIRED: compliance_response.get(consts.DESIRED),
                    }


            else:
                result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors, aria_consts.CHILD_APPLIANCES: child_appliances}
        return result