import logging
from typing import Dict, Tuple, List, Any

import requests
import ssl
import socket
import hashlib

from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class DnsForwarder(BaseController):
    """Manage NSX DNS forwarder configuration.
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - DNS forwarder config for NSX gateway 

    """

    metadata = ControllerMetadata(
        name="dos_protection_dns_forwarder",  # controller name
        path_in_schema="compliance_config.nsxt_manager.dos_protection_dns_forwarder",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate the DNS forwarder config on Tier-0 gateways",  # controller title as defined in compliance kit.
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


    def _get_dns_forwarders(self,context: NSXTManagerContext) -> list[str]:
        """
        Get dns forwarder configuration from NSX API.

        :return: return DNS forwarder configuration
        :rtype: dict
        """
       
        dns_forwarders = []
      
        #use query API to retrieve all objects of type PolicyDnsForwarder
        nsx_request = requests.get(
            f"https://localhost/policy/api/v1/search/query?query=resource_type:PolicyDnsForwarder",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")

        dns_forwarder_results = nsx_request_body['results']
        #Filter out DNS Forwarders created on Tier-1 gateways
        for forwarder in dns_forwarder_results:
            if 'tier-1' not in forwarder['path']:
                dns_forwarders.append(forwarder)

        #Filter out uneeded keys in results
        keys_to_keep = ['display_name', 'path', 'resource_type','id','enabled','default_forwarder_zone_path','listener_ip']
        dns_forwarders = [{k: d[k] for k in keys_to_keep if k in d} for d in dns_forwarders]

        return dns_forwarders
    
    
    def _del_dns_forwarders(self,context: NSXTManagerContext, dns_forwarder) -> list[str]:
        """
        Delete DNS forwarder configuration

        :return: response body
        :rtype: dict
        """
        nsx_request_body = {}
        # get input resource type. Only call DELETE if the resopurce type is a DNS forwarder
        resource_type = dns_forwarder.get('resource_type')
        if not resource_type or resource_type != "PolicyDnsForwarder":
            raise Exception(f"ERROR: Wrong resource type for DNS forwarder {dns_forwarder['display_name']} : {resource_type}")

        api_path = dns_forwarder['path']
        logger.info(f"Deleting dns forwarder with path: {api_path}")
        
        
        nsx_request = requests.delete(
            f"https://localhost/policy/api/v1{api_path}",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        if nsx_request.content:    
            nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        
        return nsx_request_body


    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get DNS forwarder config from NSX.

        | Sample get output

        .. code-block:: json

        "dns_forwarders": [ {
            "listener_ip": "192.168.20.10",
            "resource_type": "PolicyDnsForwarder",
            "display_name": "salt-dns-forwarder",
            "enabled": true,
            "default_forwarder_zone_path": "/infra/dns-forwarder-zones/salt-test-zone",
            "path": "/infra/tier-0s/salt-test/dns-forwarder",
            "marked_for_delete": false,
            "id": "dns-forwarder"
            } ]
        }]
    

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing vidm key length  and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting DNS forwarder config.")
        errors = []
       
        try:                 
            dns_forwarders = self._get_dns_forwarders(context)   
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
        logger.info(f"errors: {errors}") 
        return {"dns_forwarders": dns_forwarders }, errors
        
    
    def set(self, context: NSXTManagerContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        
        errors =[]
        try:
            dns_forwarders, errors = self.get(context) 
            dns_forwarders_list = dns_forwarders["dns_forwarders"] 
            if len(dns_forwarders_list) > 0:
                for forwarder in dns_forwarders_list:
                    self._del_dns_forwarders(context,forwarder)
            status = RemediateStatus.SUCCESS
        
        except Exception as e:
            logger.exception(f"Exception setting DNS forwarder config - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors


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

        
        #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
        errors = []
        if not nsx_utils.isLeader(context):
            errors = [nsx_utils.ERROR_MSG_NOT_VIP]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
      
        logger.debug("checking compliance")
        desired_values = {"dns_forwarders": []}
        logger.info(f"desired values: {desired_values}")
        
        return super().check_compliance(context, desired_values)
                          

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current vidm  configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for vidm config.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """

        return super().remediate(context, desired_values)
    
