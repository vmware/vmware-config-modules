import logging
from typing import Dict, Tuple, List, Any

import requests,json
import socket

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
from config_modules_vmware.framework.clients.nsxt import nsxt_consts

logger = LoggerAdapter(logging.getLogger(__name__))



class ValidateCertificate(BaseController):
    """Manage NSX Manager web access security protocols.
    This is a controller implementation nsxt manager.

    | Config Id - 0000
    | Config Title - web-based administrative access must support encryption for the web-based access.

    """

    metadata = ControllerMetadata(
        name="validate_certificate",  # controller name
        path_in_schema="compliance_config.nsxt_manager.validate_certificate",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate NSX-T Manager certificate is valid.",  # controller title as defined in compliance kit.
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
    CERT_STATUS_OK = "OK"

    def _get_cluster_certificate(self,context) -> str:
        """
        Call NSX-T Manager API to get current config.

        :return: response body
        :rtype: dict
        """   
        nsx_request = requests.get(
            f"https://localhost/api/v1/cluster/api-certificate",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return nsx_request_body['certificate_id']
    
    def _get_certificate_status(self,context,cert_id) -> Tuple[str, str]:
        """
        Call NSX-T Manager API to get current config.

        :return: response body
        :rtype: dict
        """   
        nsx_request = requests.get(
            f"https://localhost/api/v1/trust-management/certificates/{cert_id}?action=validate",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        status = nsx_request_body['status']
        error = ""
        if status != "OK":
            error = nsx_request_body['error_message']
        return status,error 
    

    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get web access security protocols from NSX-T Manager.

        | Sample get output

        .. code-block:: json

            {"status": "OK"}
        
        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing certificate status result.
        :rtype: Tuple
        """
        logger.info("Getting cluster certificate.")
        errors = []
        cluster_cert_status = None
        cluster_cert_id = None
        try:
            cluster_cert_id = self._get_cluster_certificate(context)
            cluster_cert_status,error = self._get_certificate_status(context,cluster_cert_id)   
            if error:
                cluster_cert_status += f" -{error}"
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
                
        logger.info(f"status: {cluster_cert_status}")   
        return {"status": cluster_cert_status}, errors
      

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
        
        # NSX only needs servers for NTP control
        desired_values = {"status": desired_values.get("status", [])}
        return super().check_compliance(context, desired_values)

    def set(self, context: NSXTManagerContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set web access security protocols in NSX.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for web access protocols.

        .. code-block:: json

            
        {
            {"status": "OK"}
        }

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired value for the secure web access config Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current certificate configuration.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for certificate. status
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        #certificate replacement requires a signed certificate
        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}