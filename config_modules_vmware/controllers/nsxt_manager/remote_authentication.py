import logging
from typing import Dict, Tuple, List, Any

import requests
from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class RemoteAuthentication(BaseController):
    """Manage NSX vidm configuration.
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - NSX Manager must integrate with vIDM

    """

    metadata = ControllerMetadata(
        name="remote_authentication",  # controller name
        path_in_schema="compliance_config.nsxt_manager.remote_authentication",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate NSX is integrated with vIDM",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[
            NSXTManagerContext.ProductEnum.NSXT_MANAGER
        ],  # product from enum in NSXTManagerContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsx_manager"],  # location where functional tests are run.
    )


    http_headers = {'Content-Type': 'application/json'}

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
                "enabled": true
            }

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing vidm key length  and a list of error messages.
        :rtype: Tuple
        """
        errors = []
        vidm_enabled = False
        try:
            vidm_config = self._get_vidm_config(context)
            vidm_enabled = vidm_config.get("vidm_enable",False)                      
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))

        return {"enabled": vidm_enabled}, errors
    
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

        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
    
