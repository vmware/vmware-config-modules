import logging
from typing import Dict, Tuple, List, Any
import requests
import json
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

class AllowOnlyDefaultRoute(BaseController):
    """Manage allowed inbound routes .
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - allow only default route on BGP peers with ToRs 

    """

    metadata = ControllerMetadata(
        name="allow_only_default_route",  # controller name
        path_in_schema="compliance_config.nsxt_manager.allow_only_default_route",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate the allowed inbound routes on Tier-0 gaeways",  # controller title as defined in compliance kit.
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
        


    
    def _get_locale_service(self, context: NSXTManagerContext, gatewayId):

        #get locale_services
        nsx_request = requests.get(
            f"https://localhost/policy/api/v1/infra/tier-0s/{gatewayId}/locale-services/",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")

        if(nsx_request_body['result_count'] > 1):
            raise Exception(f"Found multiple locale-services for gateway {gatewayId}. Max 1")
        else:
            locale_service_id = nsx_request_body['results'][0]['id']
        return locale_service_id

    def _getLocalAddrForEBGP(self, context: NSXTManagerContext, gatewayId, eBGPSegments):
        addresses = []
        locale_service_id = self._get_locale_service(context,gatewayId)
        uri = f"/infra/tier-0s/{gatewayId}/locale-services/{locale_service_id}/interfaces"
        #uri = f"/infra/tier-0s/{gatewayId}/locale-services/default/interfaces"
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

    def _compare_list_of_dicts(self, list1, list2, path=""):
        """
        Compares two lists of dictionaries and finds added, removed, and modified elements.
        
        :param list1: First list of dictionaries
        :param list2: Second list of dictionaries
        :param path: Key path for nested fields (used for recursion)
        :return: Dictionary with added, removed, and modified items
        """
	
        changes = {"added": [], "removed": [], "modified": []}
        
        sorted_list1 = sorted(list1, key=lambda x: str(x))
        sorted_list2 = sorted(list2, key=lambda x: str(x))
        
        #create dict sorted by keys
        set1 = {json.dumps(d, sort_keys=True) for d in sorted_list1}
        set2 = {json.dumps(d, sort_keys=True) for d in sorted_list2}

        # Detect modified dictionaries
        diff_desired = set2 - set1
        diff_current = set1 - set2

        #update changes
        changes["diff_desired"] = [json.loads(d) for d in diff_desired]
        changes["diff_current"] = [json.loads(d) for d in diff_current]
    
        return changes


    def _deep_compare(self, context: NSXTManagerContext, dict1, dict2, path=""):
        """
        Recursively compares two dictionaries and returns differences.
        
        :param dict1: First dictionary
        :param dict2: Second dictionary
        :param path: Key path for nested fields (used for recursion)
        :return: Dictionary of changed fields with old and new values
        """
        changes = {}
        all_keys = set(dict1.keys()).union(set(dict2.keys()))

        for key in all_keys:
            new_path = f"{path}.{key}" if path else key

            #check if dict1 is mssing key in dict2
            if key not in dict1:       
                changes[new_path] = {"old": None, "new": dict2[key]}
            #check if dict2 is mssing key in dict1
            elif key not in dict2:
                changes[new_path] = {"old": dict1[key], "new": None}
            #if key is a dict call compare              
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):              
                nested_changes = deep_compare(dict1[key], dict2[key], new_path)
                if nested_changes:
                    changes.update(nested_changes)
            #items are lists
            elif isinstance(dict1[key], list) and isinstance(dict2[key], list):
                #if all list items are dicts call compare_list_of_dicts
                if all(isinstance(item,dict) for item in dict1[key]) and all(isinstance(item,dict) for item in dict2[key]):
                    list_changes = self._compare_list_of_dicts(dict1[key], dict2[key], new_path)
                    if list_changes:
                        changes[new_path] = list_changes
                #list items are not dicts. compare directly
                else:
                    sorted_list1 = sorted(dict1[key])
                    sorted_list2 = sorted(dict2[key])

                    if sorted_list1 != sorted_list2:
                        changes[new_path] = {"old": dict1[key], "new": dict2[key]}
        
            elif dict1[key] != dict2[key]:
                changes[new_path] = {"old": dict1[key], "new": dict2[key]}

        return changes

    def _getdiff(self, context: NSXTManagerContext, current_values, desired_values):
        desired_noncompliant = []
        current_noncompliant = []

        #loop through  current values for GW
        for current_item in current_values:
            current_gw = current_item["gateway"]
            #find GW in generated list of desired values
            for desired_item in desired_values:
                if desired_item["gateway"] == current_gw:
                    #desired_gw = desired_item
                    break                 
            result = self._deep_compare(context, current_item, desired_item)
         
            if len(result["route_maps"]["diff_desired"]) or len(result["route_maps"]["diff_current"]) > 0:
                current_noncompliant.append({"gateway": current_gw, "route_maps": result["route_maps"]["diff_current"]})
                desired_noncompliant.append({"gateway": current_gw, "route_maps": result["route_maps"]["diff_desired"]})

        return current_noncompliant, desired_noncompliant
    
    
    def _filter_keys(self, data, keys_to_ignore):
        if isinstance(data, dict):
            return{
                k: self._filter_keys(v, keys_to_ignore)
                for k, v in data.items()
                if k not in keys_to_ignore
            }
        elif isinstance(data, list):
            return [self._filter_keys(item, keys_to_ignore) for item in data]
        else:
            return data

    
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
        bgpSegments = desired_values.get("inbound_segments",[])
        route_maps =  desired_values.get("route_maps")
        desired_values = []
        
        
        #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
        errors = []
        if not nsx_utils.isLeader(context):
            errors = [nsx_utils.ERROR_MSG_NOT_VIP]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
      
        try:
            #get list of Tier-0 gateways
            t0_list = self._get_valid_tier0s(context)
          
            #used to dynamically build desired values from the route map input which shoudl be same for all interfaces
            gw_interfaces = {}
            for t0_gw in t0_list:
               
                inboundRouteMaps = []
                peering_addresses = []
                t0_id = t0_gw['id']
                logger.info(f"Checking ip prefix lists on gateway {t0_id}")
        
                #Skip any ingress/egress gateways. Control does not apply
                if "egress" in t0_id.lower() or "ingress" in t0_id.lower() or "egw" in t0_id.lower():
                    continue
                              
                #get the local interface addresses that are peering with the bgp segments
                localAddrForEBGP = self._getLocalAddrForEBGP(context,t0_id,bgpSegments)                
        
                #Get list of BGP neighbors on gateway     
                locale_service_id = self._get_locale_service(context,t0_id)                
                bgpNeighbors = self._nsx_get_request(context, f"/infra/tier-0s/{t0_id}/locale-services/{locale_service_id}/bgp/neighbors")     
               
                #loop through neighbors and get the route map and prefix list config only for interfaces
                #that match the local addresses found to be peering with the eBGP segments            
                for  neighbor in bgpNeighbors["results"]:                              
                    #get only neighbors that are peering with the list of segments
                    isExternalBGP = False
                    #check the source address of the peer
                    for sourceAddress in neighbor["source_addresses"]:
                        if sourceAddress in localAddrForEBGP or t0_id == "gateway-t0-ingress":
                            isExternalBGP = True
                            logger.debug(f"Fabric BGP peer found: {neighbor['neighbor_address']}")
                            break                                           
                    
                    if not isExternalBGP:
                        continue  #bgp peer is not peering with an eBGP segment. skip

                    #get the inbound route filters for the peer config
                    #if no inbound route filter this is a finding
                    if  ("in_route_filters" not in neighbor):
                        inboundRouteMaps.append({})
                    else:    
                        for filter in neighbor["in_route_filters"]:
                            uri = filter
                            #get the route maps
                            routeMap = self._nsx_get_request(context,uri)

                            for entry in routeMap["entries"]:
                                prefixes = []
                                for prefix_uri in entry["prefix_list_matches"]:
                                    #get the prefix list for the route map
                                    prefixList = self._nsx_get_request(context, prefix_uri)
                                    prefixes.append({"name": prefixList['id'], "prefixes": prefixList['prefixes']} )    
                                    #prefixes.append({"prefixes": prefixList['prefixes']} )                               
                                #add route map/prefix list config to the list
                                inboundRouteMaps.append({"name": routeMap['id'], "source_address": sourceAddress, "neighbor_address": neighbor["neighbor_address"], "action": entry['action'], "prefix_lists" : prefixes})
                        
                    #add the source and neighbor address to the list for building desired value config
                    peering_addresses.append({"source_address":sourceAddress, "neighbor_address" : neighbor['neighbor_address']  })
            
                #update map of gateway id to peering addresses
                gw_interfaces[t0_id] = peering_addresses
                current_value.append({"gateway": t0_gw['id'], "route_maps": inboundRouteMaps})

                #dynamically generate desired_value by adding the desired route map/prefix list config to each interface of the GW in the
                #desired_values dict
                desired_route_maps = []                    
                for item in route_maps:  
                    #get the addresses
                    for addresses in peering_addresses:
                        new_rm = dict(item)
                        new_rm['source_address'] = addresses.get('source_address')
                        new_rm['neighbor_address'] = addresses.get('neighbor_address')
                        desired_route_maps.append(new_rm)                      
                desired_values.append({"gateway": t0_id, "route_maps": desired_route_maps})
                
            logger.debug(f"current values: {current_value}") 
            logger.debug(f"desired values: {desired_values}")
                            
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
        logger.info(f"errors: {errors}") 
        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        try:
            #Filter out name key for comparison as name does not matter, the route-map and prefix-list values do.
            #Candidate for refactoring the input value schema in future
            filtered_current = self._filter_keys(current_value, "name")
            filtered_desired = self._filter_keys(desired_values, "name")
            current_non_compliant_configs, desired_non_compliant_configs = self._getdiff(context, filtered_current, filtered_desired)
        except Exception as e:
            raise Exception(f"Error getting drift bretween current and desired values: {e}")
        
        
        if current_non_compliant_configs or desired_non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_non_compliant_configs,
                consts.DESIRED: desired_non_compliant_configs,
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
    
