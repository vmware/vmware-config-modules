import logging
from typing import Dict, Tuple, List, Any
import requests
from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.nsxt import nsxt_consts
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList
from config_modules_vmware.framework.utils.comparator import Comparator
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils

logger = LoggerAdapter(logging.getLogger(__name__))

class AntiPrefixFloodProtection(BaseController):
    """Manage allowed inbound routes .
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - allow only default route on BGP peers with ToRs 

    """

    metadata = ControllerMetadata(
        name="anti_prefix_flood_protection",  # controller name
        path_in_schema="compliance_config.nsxt_manager.anti_prefix_flood_protection",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="only specific routes are shared",  # controller title as defined in compliance kit.
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
    )

    http_headers = {'Content-Type': 'application/json'}
    

    def __init__(self):
        super().__init__()
        self.comparator_option = ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON
        self.instance_key = "gateway"
    
    def _nsx_get_request(self,context: NSXTManagerContext, uri) -> dict:
        
        nsx_request = requests.get(
            url="https://localhost" + nsxt_consts.POLICY_API_URI + uri,
            headers=self.http_headers,           
            auth=(context._username, context._password) ,
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return  nsx_request_body

  
    def _get_tier0s(self,context: NSXTManagerContext) -> dict:
        response = self._nsx_get_request(context,
            "/infra/tier-0s",
        )        
        return  response['results']
    
    def _get_valid_tier0s(self,context: NSXTManagerContext) -> list:
        all_t0s = self._get_tier0s(context)
        valid_t0s = []

        for t0_gw in all_t0s:
            logger.info(f"Checking gateway: {t0_gw['id']} for connected segments and/or tier-1 gateways")
            t0_gw_path = t0_gw['path']
            search = f"/search/query?query=(resource_type:segment AND connectivity_path:\"{t0_gw_path}\") OR (resource_type:tier1 AND tier0_path:\"{t0_gw_path}\")"
            logger.info(f"search: {search}")
            response = self._nsx_get_request(context,
                        search,
                        )
            logger.info(f"search response: {response}")
            if response['result_count'] != 0:
                valid_t0s.append(t0_gw)
            else:
                logger.info(f"Skipping gw {t0_gw['id']}. No connected segments or Tier-1 GWs.")
        return valid_t0s
    
    
    def _getLocalAddrForEBGP(self, context: NSXTManagerContext, gatewayId, eBGPSegments):
        addresses = []
        uri = "/infra/tier-0s/" + gatewayId + "/locale-services/default/interfaces"
        response = self._nsx_get_request(context,
            uri      
        )
                
        #get northbound address bound to the eBGP segments. Ignore any other address as these are southbound tenant interefaces or other use.
        interfaces = response
        for interface in interfaces["results"]:            
            segment = interface["segment_path"].split("/infra/segments/")[1]
            logging.debug(f"found segment {segment}")
            if segment in eBGPSegments:
                for subnet in interface["subnets"]:
                    logging.debug(f"found subnet {subnet}")
                    for address in subnet["ip_addresses"]:
                        logging.debug(f"found address {address}")
                        addresses.append(address)
        return addresses
    
    def _dict_in_list(self,target_dict, dict_list):
        for d in dict_list:
            logging.debug(f"Checking if dict {target_dict} matches {d}")
            if d == target_dict:
                return True
        return False
    
    def get(self, context: NSXTManagerContext, template: dict = None) -> Tuple[Any, List[str]]:
        pass                      

    def set(self, context: NSXTManagerContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}


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
        errors = []       
        current_value = []
        disallowed_prefixes = desired_values.get("disallowed_prefixes")
        desired_values = []
        disallowed_values = []
        no_out_filters = []

        
        #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
        if not nsx_utils.isLeader(context):
            errors = [nsx_utils.ERROR_MSG_NOT_VIP]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
      
        try:
            #get list of Tier-0 gateways
            t0_list = self._get_valid_tier0s(context)           
       
            for t0_gw in t0_list:
                t0_id = t0_gw['id']
                logger.info(f"Checking gateway {t0_id}")

                #Skip any ingress/egress gateways. Control does not apply
                t0_match = t0_id.lower()
                if "egress" in t0_match or "ingress" in t0_match or "egw" in t0_match:
                    continue
                                   
                #Get locale services path
                localePathResults = self._nsx_get_request(context, f"/infra/tier-0s/{t0_id}/locale-services")
                logger.info(f"localePathResults: {localePathResults}")
                if localePathResults["result_count"] > 1:
                    raise Exception(f"Gateway {t0_id} has more than one locale-service defined. Unable to continue")
                else:
                    localePath = localePathResults["results"][0]["path"]

                bgpPath = f"{localePath}/bgp/neighbors"
                logger.info(f"localePath: {localePath}")
                logger.info(f"bgpPath: {bgpPath}")
                #Get list of BGP neighbors on gateway     
                bgpNeighbors = self._nsx_get_request(context, bgpPath)     

                #loop through neighbors and get the outbound route maps and prefixes  
                for  neighbor in bgpNeighbors["results"]:            
                    logging.debug(f"neighor: {neighbor}")                      
                    neighbor_address = neighbor["neighbor_address"]
                    source_addresses = neighbor["source_addresses"]
                    #if no outbound route filter this is a fiding
                    if not "out_route_filters" in neighbor:
                        no_out_filters.append({"gateway": t0_id, "source_address": source_addresses, "neighbor_address": neighbor_address})
                        logger.info(f"No outbound route filter for gateway {t0_id} and neighbor {neighbor_address} ")
                        continue
                                             

                    for out_filter in neighbor["out_route_filters"]:                     
                        ##Get the associated route map details
                        uri = out_filter
                        routeMap = self._nsx_get_request(context,uri)
                        logger.info(f"route_map: {routeMap}")
                        for entry in routeMap["entries"]:
                            logger.info(f"entry: {entry}")
                            #only check ones with action PERMIT.
                            if entry['action'] == "PERMIT":
                                logger.info(f"Checking route map entry {entry['prefix_list_matches']} with action {entry['action']}")
                                for prefix_uri in entry["prefix_list_matches"]:
                                    #get the prefix list for the route map
                                    prefixList = self._nsx_get_request(context, prefix_uri)  
                                    logging.debug(f"prefixList: {prefixList}")                              
                                    for prefix in prefixList["prefixes"]:
                                        prefix_check = {"action": prefix["action"],"network": prefix["network"] }
                                        if(self._dict_in_list(prefix_check, disallowed_prefixes)):                                    
                                            logging.error(f"Disallowed route found! {prefix_check}")
                                            disallowed_values.append({"gateway": t0_id, "source_address": source_addresses, "neighbor_address": neighbor_address, "route map": routeMap['id'], "prefix": prefix})
                            else:
                                logger.info(f"Skipping route map entry {entry['prefix_list_matches']} with action {entry['action']}")
                                                

            desired_values = f"No outbound prefixes matching: {disallowed_prefixes}. No Missing outbound route filters."    
            logger.debug(f"current values: {current_value}") 
            logger.debug(f"desired values: {desired_values}")
                           
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
        logger.info(f"errors: {errors}") 
        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

      
        if len(disallowed_values) > 0 or len (no_out_filters) > 0:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: f"Disallowed prefixes: {disallowed_values} Missing outbound filters:  {no_out_filters}",
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result                     

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current urpf mode  configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for urpf mode config.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """

        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
    
