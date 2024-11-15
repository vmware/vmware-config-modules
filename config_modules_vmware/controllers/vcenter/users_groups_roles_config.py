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
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

NAME = "name"
TYPE = "type"
ROLE = "role"
USER = "USER"
GROUP = "GROUP"

FILTER_PATTERNS = [
    re.compile(
        r"^[a-zA-Z\d\.-]+\\(vpxd-extension|vmware-vsm|topologysvc|vsphere-webclient|vsphere-ui|vpxd|vpxd-svc-acct|"
        r"certificateauthority|perfcharts|observability-vapi|cms|vpxd-svcs-user)-["
        r"\da-fA-F]{8}\-[\da-fA-F]{4}\-[\da-fA-F]{4}\-[\da-fA-F]{4}\-[\da-fA-F]{12}"
    ),
    re.compile(r"^[a-zA-Z\d\.-]+\\svc-.*"),
]


class UsersGroupsRolesConfig(BaseController):
    """Class for UsersGroupsRolesSettings config with get and set methods.
    | ConfigId - 415
    | ConfigTitle - The vCenter Server users must have the correct roles assigned.
    """

    def __init__(self):
        # Initialize instance key with "name" and comparator option with Identifier based comparison.
        super().__init__()
        self.domain_alias_to_name_map = None

    metadata = ControllerMetadata(
        name="users_groups_roles",  # controller name
        path_in_schema="compliance_config.vcenter.users_groups_roles",
        # path in the schema to this controller's definition.
        configuration_id="415",  # configuration id as defined in compliance kit.
        title="The vCenter Server users must have the correct roles assigned.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def _create_alias_domain_name_mapping(self, context: VcenterContext):
        """
        Create domain alias to domain name mapping for existing aliases.
        :param context: Product context instance.
        :type context: VcenterContext
        """
        if self.domain_alias_to_name_map is None:
            vc_vmomi_sso_client = context.vc_vmomi_sso_client()
            all_domains = vc_vmomi_sso_client.get_all_domains()
            logger.info(f"All domains in VC {all_domains}")
            external_domains = getattr(all_domains, "externalDomains", [])
            self.domain_alias_to_name_map = {}
            for external_domain in external_domains:
                if external_domain.alias:
                    self.domain_alias_to_name_map[external_domain.alias] = external_domain.name

    def _should_filter(self, name: str) -> bool:
        """Checks if a given name matches any filter patterns."""
        for pattern in FILTER_PATTERNS:
            if pattern.match(name):
                return True
        return False

    def _normalize_domain(self, name: str) -> str:
        """Replaces alias with canonical domain if alias exists, otherwise returns name as is."""
        if "\\" in name:
            domain_or_alias, user_or_group = name.split("\\", 1)
            domain_or_alias = domain_or_alias.lower()
            # Replace alias with domain name if an alias is configured, otherwise keep the original
            domain_name = self.domain_alias_to_name_map.get(domain_or_alias, domain_or_alias)
            return f"{domain_name}\\{user_or_group.lower()}"
        else:
            raise Exception("Unexpected group or user format")

    def get(self, context: VcenterContext) -> Tuple[List[Dict[str, str]], List[Any]]:
        """Get roles for users and groups.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of dictionary (with keys-'role', 'name', 'type') objects and a list of error messages.
        :rtype: Tuple
        """
        errors = []
        result = []
        unique_entries = set()  # Set to store unique (name, role, type)
        try:
            content = context.vc_vmomi_client().content
            authorization_manager = content.authorizationManager
            role_collection = authorization_manager.roleList
            for role in role_collection:
                permissions = authorization_manager.RetrieveRolePermissions(role.roleId)
                for permission in permissions:
                    name = permission.principal
                    # Filter any user/group which matches exclude pattern
                    if self._should_filter(name):
                        continue

                    key_tuple = (name, role.name, USER if not permission.group else GROUP)
                    if key_tuple not in unique_entries:
                        unique_entries.add(key_tuple)
                        result.append({ROLE: role.name, NAME: name, TYPE: USER if not permission.group else GROUP})

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """
        Set method is not implemented as this control requires user intervention to remediate.
        This needs to be reviewed manually before remediation as it could have potential impact on vCenter access.
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def _find_drifts(self, current: List, desired: List) -> Tuple[List, List]:
        """Find the drift between current and desired users_groups_roles.

        :param current: Current list of users,groups,roles on vCenter.
        :type current: List
        :param desired: Desired list of users,groups,roles on vCenter.
        :type desired: list
        :return: Tuple of current and desired list with drifts
        :rtype: Tuple
        """

        current_dict = {(entry[NAME], entry[ROLE]): entry for entry in current}
        desired_dict = {(entry[NAME], entry[ROLE]): entry for entry in desired}

        drift_current = []
        drift_desired = []

        all_keys = set(current_dict.keys()).union(set(desired_dict.keys()))

        for key in all_keys:
            current_entry = current_dict.get(key)
            desired_entry = desired_dict.get(key)

            if current_entry and desired_entry:
                # Both exist: check for mismatches
                if current_entry != desired_entry:
                    drift_current.append(current_entry)
                    drift_desired.append(desired_entry)
            elif current_entry:
                # Extra in current
                drift_current.append(current_entry)
                drift_desired.append(None)
            elif desired_entry:
                # Extra in desired
                drift_current.append(None)
                drift_desired.append(desired_entry)

        return drift_current, drift_desired

    def check_compliance(self, context: VcenterContext, desired_values: List) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired list of users,groups,roles on vCenter.
        :type desired_values: list
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running check compliance for vCenter users_groups_roles control")
        current_value, errors = self.get(context=context)
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        self._create_alias_domain_name_mapping(context)
        logger.info(f"domain alias mapping {self.domain_alias_to_name_map}")

        try:
            normalized_current = [
                {ROLE: item[ROLE], NAME: self._normalize_domain(item[NAME]), TYPE: item[TYPE].upper()}
                for item in current_value
            ]

            normalized_desired = [
                {ROLE: item[ROLE], NAME: self._normalize_domain(item[NAME]), TYPE: item[TYPE].upper()}
                for item in desired_values
            ]
        except Exception as e:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(e)]}

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_non_compliant_configs, desired_non_compliant_configs = self._find_drifts(
            current=normalized_current, desired=normalized_desired
        )
        if current_non_compliant_configs or desired_non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_non_compliant_configs,
                consts.DESIRED: desired_non_compliant_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
