# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

ACTIVE_DIRECTORY = "ActiveDirectory"
TYPE = "type"
EXTERNAL_DOMAINS_PYVMOMI_KEY = "externalDomains"


class SSOActiveDirectoryAuthPolicy(BaseController):
    """Manage active directory authentication for VC with get and set methods.

    | Config Id - 1228
    | Config Title - The vCenter Server must implement Active Directory authentication.

    """

    metadata = ControllerMetadata(
        name="active_directory_authentication",  # controller name
        path_in_schema="compliance_config.vcenter.active_directory_authentication",
        # path in the schema to this controller's definition.
        configuration_id="1228",  # configuration id as defined in compliance kit.
        title="The vCenter Server must implement Active Directory authentication.",
        # controller title as defined in compliance kit.
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

    def get(self, context: VcenterContext) -> Tuple[bool, List[Any]]:
        """Get active directory authentication config for VC.

        | If there is at least one external domain of type = 'ActiveDirectory', then we consider the system compliant.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: A tuple indicating whether one or more external domains of Active Directory (AD) are configured,
         along with a list of associated error messages.
        :rtype: tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        try:
            all_domains = vc_vmomi_sso_client.get_all_domains()
            logger.info(f"All domains in VC {all_domains}")
            external_domains = getattr(all_domains, EXTERNAL_DOMAINS_PYVMOMI_KEY, [])
            logger.info(f"External domains in VC {external_domains}")
            result = any([getattr(domain, TYPE, None) == ACTIVE_DIRECTORY for domain in external_domains])
        except Exception as e:
            logger.exception(f"An error occurred while retrieving external domains: {e}")
            errors.append(str(e))
            result = None
        return result, errors

    def set(self, context: VcenterContext, desired_values: bool) -> Tuple[str, List[Any]]:
        """Set requires manual intervention, as seamlessly integrating AD with vCenter is not possible and
         often requires a service or appliance restart.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Bool to enforce active directory based authentication in vCenter.
        :type desired_values: bool
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors
