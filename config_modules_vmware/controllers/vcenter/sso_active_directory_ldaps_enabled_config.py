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
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

ACTIVE_DIRECTORY = "ActiveDirectory"
TYPE = "type"
PATTERN = "ldaps://"
EXTERNAL_DOMAINS_PYVMOMI_KEY = "externalDomains"


class SSOActiveDirectoryLdapsEnabledPolicy(BaseController):
    """Manage active directory LDAPS enabled config for VC with get and set methods.

    | Config Id - 1229
    | Config Title - The vCenter Server must use LDAPS when adding an SSO identity source.

    """

    metadata = ControllerMetadata(
        name="active_directory_ldaps_enabled",  # controller name
        path_in_schema="compliance_config.vcenter.active_directory_ldaps_enabled",
        # path in the schema to this controller's definition.
        configuration_id="1229",  # configuration id as defined in compliance kit.
        title="The vCenter Server must use LDAPS when adding an SSO identity source.",
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

    def get(self, context: VcenterContext) -> Tuple[List, List[Any]]:
        """Get active directory authentication config for VC.

        | If any external domain is of type 'ActiveDirectory' and doesn't use LDAPS, then the system is deemed
            non-compliant.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: A tuple indicating that at least one Active Directory (AD) external domain is configured without LDAPS,
         along with a list of associated error messages.
        :rtype: tuple
        """
        vc_vmomi_sso_client = context.vc_vmomi_sso_client()
        errors = []
        try:
            all_domains = vc_vmomi_sso_client.get_all_domains()
            logger.info(f"All domains in VC {all_domains}")
            external_domains = getattr(all_domains, "externalDomains", [])
            logger.info(f"External domains in VC {external_domains}")
            result = self.__get_non_compliant_domains(external_domains)
        except Exception as e:
            logger.exception(f"An error occurred while retrieving external domains: {e}")
            errors.append(str(e))
            result = None
        return result, errors

    def __get_non_compliant_domains(self, external_domains) -> List:
        """Get list of all non-compliant AD domains not using LDAPS.

        :param external_domains: List of SSO ExternalDomain objects with AD details.
        :return:
        """
        non_compliant_external_domains = []
        for external_domain in external_domains:
            ad_details = {
                "domain_name": external_domain.name,
                "domain_alias": external_domain.alias,
                "user_base_dn": None,
                "group_base_dn": None,
                "primary_server_url": None,
                "failover_server_url": None,
                "use_ldaps": False,
            }

            details = getattr(external_domain, "details")
            if details:
                ad_details["user_base_dn"] = getattr(details, "userBaseDn")
                ad_details["group_base_dn"] = getattr(details, "groupBaseDn")
                ad_details["primary_server_url"] = getattr(details, "primaryUrl")
                ad_details["failover_server_url"] = getattr(details, "failoverUrl")

                is_primary_compliant = ad_details["primary_server_url"] and ad_details["primary_server_url"].startswith(
                    PATTERN
                )
                # If failover is not set, we treat it as compliant.
                is_failover_compliant = ad_details["failover_server_url"] is None or ad_details[
                    "failover_server_url"
                ].startswith(PATTERN)

                ad_details["use_ldaps"] = is_primary_compliant and is_failover_compliant

            if not ad_details["use_ldaps"]:
                non_compliant_external_domains.append(ad_details)

        return non_compliant_external_domains

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """Set requires manual intervention, as seamlessly integrating AD with vCenter is not possible and
         often requires a service or appliance restart.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Dict containing use_ldaps bool to enforce active directory based authentication in
         vCenter.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """Check compliance of Active directories configurations in VC, if AD is configured but it does not use LDAPS
         protocol then flag it as non-compliant.

        | The audit process flags an Active Directory source as non-compliant if it does not use LDAPS protocol.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Dict containing use_ldaps bool to enforce active directory based authentication in
         vCenter. When set to true (the only allowed value), the audit process flags an Active directory as
         non-compliant if it does not use LDAPS protocol.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        non_compliant_active_directory_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        if non_compliant_active_directory_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_active_directory_configs,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
