import logging
from typing import Dict, Tuple, List, Any

import requests
import ssl
import socket
import hashlib

from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class LegitimateSourceAddress(BaseController):
    """Manage NSX urpf mode configuration.
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - urpf mode set to strict 

    """

    metadata = ControllerMetadata(
        name="legitimate_source_address",  # controller name
        path_in_schema="compliance_config.nsxt_manager.legitimate_source_address",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate the uRPF mode on Tier-0 gaeways",  # controller title as defined in compliance kit.
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

    
    def _get_gateways(self,context: NSXTManagerContext, gw_type) -> dict:
        """Fetch all gateways of a specific type (Tier-0 or Tier-1)
    
        Fetch all gateways of a specific type (Tier-0 or Tier-1)

        :return: list of gateways
        :rtype: dict
        """
        nsx_request = requests.get(
            f"https://localhost/policy/api/v1/infra/{gw_type}s",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return  nsx_request_body['results']
  
    def _get_tier0s(self,context: NSXTManagerContext) -> dict:
        """
        Get urpf mode provider configuration.

        :return: urpf mode provider configuration
        :rtype: dict
        """
        nsx_request = requests.get(
            f"https://localhost/policy/api/v1/infra/tier-0s",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()

        tier0_list = []
        for tier0_gw in nsx_request_body["results"]:
            tier0_list.append(tier0_gw["id"])
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return tier0_list
    
    def _get_urpf_mode(self,context: NSXTManagerContext, t0_id) -> dict:
        """
        Get urpf mode  configuration.

        :return: urpf mode provider configuration
        :rtype: dict
        """
    
        #get locale_services
        nsx_request = requests.get(
            f"https://localhost/policy/api/v1/infra/tier-0s/{t0_id}/locale-services/",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")

        if(nsx_request_body['result_count'] > 1):
            raise Exception(f"Found multiple locale-services for gateway {t0_id}. Max 1")
        else:
            locale_service_id = nsx_request_body['results'][0]['id']

        nsx_request = requests.get(
            f"https://localhost/policy/api/v1/infra/tier-0s/{t0_id}/locale-services/{locale_service_id}/interfaces",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")

        iface_list = []
        for interface in nsx_request_body['results']:
            urpf_mode = interface["urpf_mode"]
            if urpf_mode != "STRICT":
                iface_list.append({"gateway": t0_id, "interface": interface["display_name"],"urpf_mode": urpf_mode })
        
        logger.debug(f"Interface list: {iface_list}")
        return iface_list
    
    


    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get urpf mode provider config from NSX.

        | Sample get output

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing urpf mode key length  and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting urpf mode protocol config.")
        errors = []
        t0_urpf_configs = []
       
        try:
            t0_list = self._get_tier0s(context)
            for t0_id in t0_list:
                config = self._get_urpf_mode(context, t0_id)
                if config:
                    t0_urpf_configs.append(config)

        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
        logger.debug(f"urpf_configs: {t0_urpf_configs}") 
        logger.info(f"errors: {errors}") 
        if not t0_urpf_configs:
             return {"urpf_mode": 'STRICT'}, errors
        return {"urpf_mode": t0_urpf_configs}, errors
    
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
        logger.debug("checking compliance")

        #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
        errors = []
        if not nsx_utils.isLeader(context):
            errors = [nsx_utils.ERROR_MSG_NOT_VIP]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
        
        return super().check_compliance(context, desired_values)
                          

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
    
