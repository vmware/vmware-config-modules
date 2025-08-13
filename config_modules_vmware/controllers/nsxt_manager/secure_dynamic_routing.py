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
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils


logger = LoggerAdapter(logging.getLogger(__name__))

class SecureDynamicRouting(BaseController):
    """Check if BGP secret is set when peering with the fabric.
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - BGP secret set to protect peering between DCF fabric and NSX-T layer.

    """

    metadata = ControllerMetadata(
        name="secure_dynamic_routing",  # controller name
        path_in_schema="compliance_config.nsxt_manager.secure_dynamic_routing",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="BGP secret is set",  # controller title as defined in compliance kit.
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
            url="https://localhost" + nsxt_consts.MP_API_URI + uri,
            headers=self.http_headers,           
            auth=(context._username, context._password) ,
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        return  nsx_request_body

  
    def _get_t0_logical_routers(self,context: NSXTManagerContext) -> dict:
        response = self._nsx_get_request(context,
            "/logical-routers?router_type=TIER0",
        )        
        return  response['results']
    
    def get(self, context: NSXTManagerContext) -> Tuple[Any, List[str]]:
        errors = []       
        current_values = []

        try:
            #get list of Tier-0 gateways
            t0_list = self._get_t0_logical_routers(context)           
    
            for t0_gw in t0_list:
                t0_id = t0_gw['id']
                t0_display_name = t0_gw['display_name']
                logger.info(f"Checking gateway {t0_id}")
                                
                #Get list of BGP neighbors on gateway    
                uri = f"/logical-routers/{t0_id}/routing/bgp/neighbors" 
                bgpNeighbors = self._nsx_get_request(context, uri)     

                #loop through neighbors and get the outbound route maps and prefixes  
                for neighbor in bgpNeighbors["results"]:  
                    neighbor_address = neighbor["neighbor_address"]
                    source_addresses = neighbor["source_addresses"] 
                    neighbor_id = neighbor['id']         
                    logging.debug(f"neighor: {neighbor}")   
                    uri = f"/logical-routers/{t0_id}/routing/bgp/neighbors/{neighbor_id}?action=show-sensitive-data"   
                    bgp_config = self._nsx_get_request(context, uri)                 
                    current_values.append({"gateway": t0_display_name, "source_address": source_addresses, "neighbor_address": neighbor_address, "bgp_config": bgp_config})
                
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))   
        return current_values, errors                   

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
        current_values = []
        desired_values = []
        disallowed_values = []

        try:
            #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
            if not nsx_utils.isLeader(context):
                errors = [nsx_utils.ERROR_MSG_NOT_VIP]
                return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
           
            current_values,errors = self.get(context=context)
            
            #check each cBGP config for empty password or non-existent password key
            for config in current_values:
                if "password" not in config['bgp_config'] or not config['bgp_config']['password']:
                    logging.debug(f"Peer {config['bgp_config']['id']} has no password configured.")
                    disallowed_values.append({"gateway": config['gateway'], "source_address": config['source_address'], "neighbor_address": config['neighbor_address'], "password_set": False})                                               

            desired_values = f"All BGP peering should have a password set"    
                           
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
        logger.info(f"errors: {errors}") 
        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}
      
        if len(disallowed_values) > 0:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: disallowed_values,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result                     

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current configuration drifts.

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
    
