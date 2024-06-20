# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import socket
import ssl
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

ISSUER = "issuer"


class CertConfig(BaseController):
    """
    Class for cert config with get and set methods.

    | Config Id - 1603
    | Config Title - Use an SSL certificate issued by a trusted certificate authority on the SDDC Manager.

    """

    metadata = ControllerMetadata(
        name="cert_config",  # controller name
        path_in_schema="compliance_config.sddc_manager.cert_config",
        # path in the schema to this controller's definition.
        configuration_id="1603",  # configuration id as defined in compliance kit.
        title="Use an SSL certificate issued by a trusted certificate authority on the SDDC Manager.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.SDDC_MANAGER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,
        # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: SDDCManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Function to get certificate details of sddc manager for audit.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext
        :return: Details of the certificate issuer
        :rtype: tuple
        """
        logger.info("Getting Certificate details for audit.")
        errors = []
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        result = {}
        try:
            # Get SDDC manager IP
            sddc_manager_url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.SDDC_MANAGER_URL
            api_response = sddc_manager_rest_client.get_helper(sddc_manager_url)
            sddc_manager_ip = api_response["elements"][0]["ipAddress"]

            issuer = self.__get_certificate_issuer(hostname=sddc_manager_ip, port=443)
            if issuer:
                result[ISSUER] = issuer
            else:
                raise Exception("Unable to fetch issuer details from cert")
        except Exception as e:
            logger.exception(f"Unable to fetch certificate details {e}")
            errors.append(str(e))

        return result, errors

    def __get_certificate_issuer(self, hostname: str, port: int = 443) -> Optional[str]:
        """Fetch and parse the SSL certificate details from a given hostname and port and retrieve the issuer.

        :param hostname: Hostname or IP address of the server
        :param port: Port number (default is 443 for HTTPS)
        :return: Certificate Issuer
        :rtype: str or None
        """
        try:
            ssl_ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
            ssl_ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with ssl_ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert(True)
                    pem_certificate = ssl.DER_cert_to_PEM_cert(cert)
                    cert_obj = x509.load_pem_x509_certificate(pem_certificate.encode(), default_backend())
                    issuer = cert_obj.issuer.rfc4514_string()
                    logger.info(f"Published by issuer: {issuer}")
                    return issuer
        except Exception as e:
            logger.exception(f"An error occurred while fetching certificate details: {e}")
            return None

    def set(self, context: SDDCManagerContext, desired_values) -> Tuple:
        """
        Set is not implemented as this control requires manual intervention.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext.
        :param desired_values: Desired value for the certificate authority
        :type desired_values: String or list of strings
        :return: Tuple of status (RemediateStatus.SKIPPED) and errors if any
        :rtype: tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def check_compliance(self, context, desired_values) -> Dict:
        """

        Check compliance of configured certificate authority in SDDC Manager. Certificate issuer details needs
        to be provided as shown in the below sample format (can provide multiple certs too).The method will check if the
        current certificate details is available in the desired_values and return the compliance
        status accordingly.

        | Sample desired_values spec

        .. code-block:: json

            {
                "certificate_issuer":
                    ["OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB",
                    "OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"]
            }

        :param context: Product context instance
        :type context: SDDCManagerContext
        :param desired_values: Desired value for the certificate authority.
        :type desired_values: Dictionary
        :return: Dict of status and current/desired value or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance")
        cert_info, errors = self.get(context=context)
        current_value = cert_info.get(ISSUER)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        if current_value in desired_values["certificate_issuer"]:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        else:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_value,
                consts.DESIRED: desired_values,
            }
        return result
