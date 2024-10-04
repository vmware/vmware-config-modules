# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

ISSUER = "issuer"
ISSUER_DN = "issuer_dn"
CERTIFICATE_ISSUER = "certificate_issuer"


class CertConfig(BaseController):
    """
    Class for cert config with get and set methods.

    | Config Id - 1205
    | Config Title - The vCenter Server Machine SSL certificate must be issued by an appropriate
    |                certificate authority.

    """

    metadata = ControllerMetadata(
        name="cert_config",  # controller name
        path_in_schema="compliance_config.vcenter.cert_config",  # path in the schema to this controller's definition.
        configuration_id="1205",  # configuration id as defined in compliance kit.
        title="The vCenter Server Machine SSL certificate must be issued by "
        "an appropriate certificate authority",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,
        # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Get certificate details of vcenter server for audit.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Details of the certificate issuer
        :rtype: tuple
        """
        logger.info("Getting Certificate details for audit.")
        errors = []
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.CERT_CA_URL
        result = {}
        try:
            # api "api/vcenter/certificate-management/vcenter/tls" to get cert
            cert_ca = vc_rest_client.get_helper(url)
            # extract issuer info from cert.
            issuer = cert_ca.get(ISSUER_DN)
            if issuer:
                result[ISSUER] = issuer
            else:
                raise Exception("Unable to fetch issuer details from cert")
        except Exception as e:
            logger.exception(f"Unable to fetch certificate details {e}")
            errors.append(str(e))

        return result, errors

    def set(self, context: VcenterContext, desired_values) -> Tuple:
        """
        Set is not implemented as this control requires manual intervention.

        :param context: Product context instance.
        :type context: VcenterContext
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

        Check compliance of configured certificate authority in vCenter server. Certificate issuer details needs
        to be provided as shown in the below sample format (can provide multiple certs too).The method will check
        if the current certificate details is available in the desired_values and return the compliance
        status accordingly.

        | Sample desired_values spec

        .. code-block:: json

            {
                "certificate_issuer":
                    ["OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB",
                    "OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"]
            }

        :param context: Product context instance.
        :param desired_values: Desired value for the certificate authority.
        :return: Dict of status and current/desired value or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance")
        cert_info, errors = self.get(context=context)
        current_value = cert_info.get(ISSUER)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        if current_value.replace(", ", ",") in desired_values[CERTIFICATE_ISSUER]:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
            return result

        result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: current_value,
            consts.DESIRED: desired_values,
        }
        return result
