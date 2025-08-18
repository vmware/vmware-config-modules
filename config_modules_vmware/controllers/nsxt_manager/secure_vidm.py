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


class SecureVidm(BaseController):
    """Manage NSX vidm configuration.
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - NSX Manager must connect to vIDM using TLS 

    """

    metadata = ControllerMetadata(
        name="secure_vidm",  # controller name
        path_in_schema="compliance_config.nsxt_manager.secure_vidm",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate the vidm protocol on NSX-T node.",  # controller title as defined in compliance kit.
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

    def _get_ssl_thumbprint(self, host, port=443,allow_self_signed=False):
        """
        Get SSL thumbprint from remote server.

        :param host: hostname or ip of remote server
        :type string
        :param port: port to conenct to
        :type integer    
        :param: allow_self_signed: allow connection to server with self signed cert in chain
        :type: boolean
        :return: SSl thumbprint
        :rtype: str
        """
        thumbprint = None
        context = ssl.create_default_context()

        if allow_self_signed:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        logger.debug(f"retreiving thumbprint from {host}")
        try:
            # Create a socket and connect to server
            with socket.create_connection((host, port)) as sock:
                # Wrap the socket using SSL
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    # Get the binary DER form of the certificate
                    der_cert = ssock.getpeercert(binary_form=True)
                    # Calculate SHA-256 hash
                    thumbprint = hashlib.sha256(der_cert).hexdigest()
        except Exception as e:
            logger.exception(f"Error retrieveing vIDM thumbprint: {e}")                            
    
        if thumbprint:
            thumbprint = thumbprint.upper()
        return thumbprint
    
    def _get_supported_tls_versions(self, host, port=443, allow_self_signed=False):
        """
        Get supported TLS versions from remote server.

        :param host: hostname or ip of remote server
        :type string
        :param port: port to conenct to
        :type integer    
        :param: allow_self_signed: allow connection to server with self signed cert in chain
        :type: boolean
        :return: supported ssl versions
        :rtype: list
        """

        tls_versions = {
            ssl.TLSVersion.TLSv1: 'TLSv1',
            ssl.TLSVersion.TLSv1_1: 'TLSv1_1',
            ssl.TLSVersion.TLSv1_2: 'TLSv1_2',
            ssl.TLSVersion.TLSv1_3: 'TLSv1_3',
        }

        supported_versions = []
        # Create a new SSL context
        ssl_context = ssl.create_default_context()
        if allow_self_signed:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        for version, name in tls_versions.items():
            try:
                # Set the specific TLS version to use
                ssl_context.minimum_version = version
                ssl_context.maximum_version = version

                # Create a socket and attempt to connect and wrap it with SSL
                with socket.create_connection((host, port)) as sock:
                    with ssl_context.wrap_socket(sock, server_hostname=host) as ssock:
                        logger.debug(f"Successfully connected to {host}:{port} with {name}")
                        supported_versions.append(name.replace('_','.'))

            except ssl.SSLError as e:
                logger.exception(f"Failed to connect with {name}: {e}")
            except Exception as e:
                logger.exception(f"An error occurred with {name}: {e}")

        return supported_versions


    def _get_vidm_config(self,context: NSXTManagerContext) -> dict:
        """
        Get vidm provider configuration.

        :return: vidm provider configuration
        :rtype: dict
        """
        nsx_request = requests.get(
            f"https://localhost/api/v1/node/aaa/providers/vidm",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return nsx_request_body
    


    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get vidm provider config from NSX.

        | Sample get output

        .. code-block:: json

            {
                "vidm_hostname": vidm-host.corp, 
                "enabled": true, 
                "protocol_versions": [TLSv1.2, TLSv1.3], 
                "thumbprint": <SSL thumbprint>
            }

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing vidm key length  and a list of error messages.
        :rtype: Tuple
        """
        errors = []
       
        
        try:
            vidm_config = self._get_vidm_config(context)
            vidm_hostname = vidm_config.get("host_name","")
            vidm_thumbprint = vidm_config.get("thumbprint","")
            vidm_enabled = vidm_config.get("vidm_enable",False)
            tls_versions = self._get_supported_tls_versions(vidm_hostname,allow_self_signed=True)
          
                      
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
    
        return {"enabled": vidm_enabled, "protocol_versions": tls_versions}, errors
    
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

        #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
        errors = []
        if not nsx_utils.isLeader(context):
            errors = [nsx_utils.ERROR_MSG_NOT_VIP]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
      
        logger.info("checking compliance")
        
        #Check current protocol versions available from vIDM. If current protocols are a subset
        #of desired protocols then compliance passes
        current_values,errors = self.get(context=context)  
        current_protos = set(current_values.get("protocol_versions"))
        desired_protos = set(desired_values.get("protocol_versions"))
        if (current_protos == desired_protos or current_protos.issubset(desired_protos)) \
            and (current_values.get("enabled") == desired_values.get("enabled")):
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        else:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_values,
                consts.DESIRED: desired_values,
            }
            
        return result     
       
                          

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current vidm  configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for vidm config.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """

        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
    
