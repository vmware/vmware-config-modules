# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

VC_SSO_CONFIG_CMD_GET_LDAP_IDENTITY_SOURCE = "/opt/vmware/bin/sso-config.sh -get_identity_sources"
LDAP_SOURCE_TYPE = "IDENTITY_STORE_TYPE_LDAP_WITH_AD_MAPPING"


class LdapIdentitySourceConfig(BaseController):
    """
    Class for ldap identity source config with get and set methods.

    | Config Id - 1230
    | Config Title - The vCenter Server must use a limited privilege account when adding an
                     LDAP identity source.
    """

    metadata = ControllerMetadata(
        name="ldap_identity_source_config",  # controller name
        path_in_schema="compliance_config.vcenter.ldap_identity_source_config",  # path in the schema to this controller's definition.
        configuration_id="1230",  # configuration id as defined in compliance kit.
        title="The vCenter Server must use a limited privilege account when adding an LDAP identity source.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["vcenter"],  # location where functional tests are run.
    )

    def __parse_ldap_identity_source(self, output):
        ldap_accounts = []
        # extract ldap account name and type from command output
        identity_source = r"IDENTITY SOURCE INFORMATION\s+([\s\S]*?)?(?=IDENTITY SOURCE INFORMATION|$)"
        domain_type = r"DomainType\s+:\s+EXTERNAL_DOMAIN"
        username_pattern = r"username\s+:\s+(.*?)\s+"
        provider_type_pattern = r"providerType\s+:\s+(.*?)\s+"
        # Search for all text marked with "IDENTITY SOURCE INFORMATION"
        identity_sources = re.finditer(identity_source, output)
        # look for external domain type
        for identity_source in identity_sources:
            if re.search(domain_type, identity_source.group()):
                # Extract username after "username :"
                username_match = re.search(username_pattern, identity_source.group())
                username = username_match.group(1) if username_match else None
                provider_type_match = re.search(provider_type_pattern, identity_source.group())
                provider_type = provider_type_match.group(1) if provider_type_match else None
                if provider_type == LDAP_SOURCE_TYPE:
                    ldap_accounts.append({"username": username})

        # if no accounts found, append a empty one (user can put an empty account on
        # desired state if no ldap binding account configured.
        if not ldap_accounts:
            ldap_accounts.append({"username": ""})

        return ldap_accounts

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Get details of ldap identity source of vcenter server for audit.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Details of the ldap account name
        :rtype: tuple
        """
        logger.info("Getting ldap identity source details for audit.")
        errors = []
        result = []
        try:
            command_output, _, _ = utils.run_shell_cmd(VC_SSO_CONFIG_CMD_GET_LDAP_IDENTITY_SOURCE)
            result = self.__parse_ldap_identity_source(command_output)
        except Exception as e:
            logger.exception(f"Unable to fetch identity source details {e}")
            errors.append(str(e))

        return result, errors

    def set(self, context: VcenterContext, desired_values) -> Dict:
        """
        Set is not implemented as this control since modifying config would impact existing auth.
        Refer to Jira : VCFSC-147

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired value for the certificate authority
        :type desired_values: String or list of strings
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        :rtype: tuple
        """
        errors = ["Set is not implemented as modifying config would impact existing auth."]
        status = RemediateStatus.SKIPPED
        return status, errors
