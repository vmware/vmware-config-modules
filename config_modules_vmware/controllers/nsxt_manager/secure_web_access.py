import logging
from typing import Dict, Tuple, List, Any

import requests,json
import copy


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


class SecureWebAccess(BaseController):
    """Manage NSX Manager web access security protocols.
    This is a controller implementation nsxt manager.

    | Config Id - 0000
    | Config Title - web-based administrative access must support encryption for the web-based access.

    """

    metadata = ControllerMetadata(
        name="secure_web_access",  # controller name
        path_in_schema="compliance_config.nsxt_manager.secure_web_access",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Configure NSX-T Manager web access security protocols.",  # controller title as defined in compliance kit.
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


    def _get_from_api(self,context) -> dict:
        """
        Call NSX-T Manager API to get current config.

        :return: response body
        :rtype: dict
        """   
        nsx_request = requests.get(
            f"https://localhost/api/v1/cluster/api-service",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return nsx_request_body
    
    def _tls_to_number(self, tls_version):
        try:
            version = tls_version.replace("TLSv", "")
            return float(version)
        except (ValueError, AttributeError):
            return None
        
    def _get_min_tls_version(self, tls_versions):
        desired_floats = []
        for desired_tls in tls_versions["protocol_versions"]:
            desired_floats.append(self._tls_to_number(desired_tls))
          
        return min(desired_floats)
        
        
    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get web access security protocols from NSX-T Manager.

        | Sample get output

        .. code-block:: json

            {"protocol_versions": ["TLSv1.1","TLSv1.2"]}
        
        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing security protocols and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting secure web access config.")
        protocol_list = []
        errors = []
        try:
            response = self._get_from_api(context)

            #parse API response for protocol versions
            """protocol_versions": [
            {
                "enabled": true,
                "name": "TLSv1.1"
            },
            {
                "enabled": true,
                "name": "TLSv1.2"
            }
            ]
            """
        
            protocol_list = response['protocol_versions']
            logger.info(f"protocol_versions: {protocol_list}")   
            
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
        return {"protocol_versions": protocol_list}, errors

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
      
        desired_values = {"protocol_versions": desired_values.get("protocol_versions", [])}
        current_values, errors = self.get(context)
        

        if errors:
            if len(errors) == 1 and errors[0] == consts.SKIPPED:
                return {consts.STATUS: ComplianceStatus.SKIPPED}
            # If errors are seen during get, return "FAILED" status with errors.
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        #desired TLS versions as floats
        desired_floats = []      
        for desired_tls in desired_values["protocol_versions"]:
            desired_floats.append(self._tls_to_number(desired_tls))
        
        #Get minimum TLS version requested from list
        min_tls_version = self._get_min_tls_version(desired_values)
        logger.debug(f"min_tls_version: {min_tls_version}")

        desired_values_comp = copy.deepcopy(current_values)
        for item in desired_values_comp['protocol_versions']:
            tls_str = item["name"]
            version_num = self._tls_to_number(tls_str)
            if version_num in desired_floats or version_num >= min_tls_version:
                item["enabled"] = True
            else:
                item["enabled"] = False
    
        return super().check_compliance(context, desired_values_comp)

    def set(self, context: NSXTManagerContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set web access security protocols in NSX.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for web access protocols.

        .. code-block:: json

            
        {
            "protocol_versions": ["TLSv1.1","TLSv1.2"]
        }

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired value for the secure web access config Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        
        
        logger.info("Setting secure web access config.")
        errors = []

        try:
            json_body = self._get_from_api(context)
            current_config, get_errors = self.get(context)
            if get_errors:
                raise Exception(f"Exception getting current config: {get_errors[0]}")
                        
            current_config = current_config.get("protocol_versions", [])
            desired_config = desired_values.get("protocol_versions", [])

            
            #build payload
            payload = []

            min_tls_version = self._get_min_tls_version(desired_values)
            logger.debug(f"min_tls_version: {min_tls_version}")
            
            for proto in json_body["protocol_versions"]:
                tls_string =  proto["name"]
                if tls_string in desired_values:
                    proto["enabled"] = True
                else:
                    tls_version = self._tls_to_number( proto["name"])
                    if tls_version is not None and tls_version < min_tls_version:
                        proto["enabled"] = False
                

            logger.debug(f"API payload: {json_body}")
            #PUT request to update setting
            nsx_request = requests.put(
            url="https://localhost/api/v1/cluster/api-service",
            data=json.dumps(json_body),
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
            )
            nsx_request.raise_for_status()
            status = RemediateStatus.SUCCESS

        except Exception as e:
            logger.exception(f"Exception setting secure web access config - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current web access security configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for NTP control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """

        return super().remediate(context, desired_values)

