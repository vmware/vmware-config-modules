# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

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
PROPAGATE = "propagate"
ROLE_ID = "role_id"
GLOBAL_CONFIG = "global"
VCENTER_CONFIG = "vcenter"
EXCLUDE_USER_PATTERNS = "exclude_user_patterns"
OPER_ADD = "+"
OPER_DELETE = "-"
OPER_MODIFY = "*"


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

    def _load_user_exclude_patterns(self, exclude_user_patterns):
        patterns = []
        for pattern in exclude_user_patterns:
            pattern = "^" + pattern
            pattern = pattern.replace("\\", "\\\\")
            regex_pattern = re.compile(pattern, re.IGNORECASE)
            logger.debug(f"Regex pattern: {regex_pattern}")
            patterns.append(regex_pattern)
        logger.debug(f"Regex patterns: {patterns}")
        return patterns

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

    def _should_filter(self, name: str, patterns) -> bool:
        """Checks if a given name belongs to local domain."""
        for pattern in patterns:
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
            return name.lower()

    def get(self, context: VcenterContext) -> Tuple[List[Dict[str, str]], List[Any]]:
        """Get roles for users and groups.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of dictionary (with keys-'role', 'name', 'type') objects and a list of error messages.
        :rtype: Tuple
        """

        errors = []
        result = {}
        unique_entries = set()  # Set to store unique (name, role, type)
        try:
            content = context.vc_vmomi_client().content
            authorization_manager = content.authorizationManager
            role_collection = authorization_manager.roleList
            role_id2name = {role.roleId: role.name for role in role_collection}

            # get global permissions
            vc_invsvc_mob3_client = context.vc_invsvc_mob3_client()
            global_permissions = vc_invsvc_mob3_client.get_global_permissions()
            for global_permission in global_permissions:
                global_permission[ROLE] = role_id2name[global_permission.get(ROLE_ID)]
                del global_permission[ROLE_ID]
                result.setdefault(GLOBAL_CONFIG, []).append(global_permission)
            global_users_roles = result.get(GLOBAL_CONFIG, [])
            logger.debug(f"Get global permissions: {global_users_roles}")

            # get vcenter level permissions
            for role in role_collection:
                permissions = authorization_manager.RetrieveRolePermissions(role.roleId)
                for permission in permissions:
                    # skip permissions not in vcenter level
                    name = permission.principal
                    if permission.entity != content.rootFolder:
                        logger.debug(f"Skip this permission, name: {name}, entity: {permission.entity}")
                        continue
                    key_tuple = (name, role.name, USER if not permission.group else GROUP)
                    if key_tuple not in unique_entries:
                        unique_entries.add(key_tuple)
                        vc_permission = {
                            ROLE: role.name,
                            NAME: name,
                            TYPE: USER if not permission.group else GROUP,
                            PROPAGATE: permission.propagate,
                        }
                        # check if this permission is global permission, if yes, exclude
                        # from compliance checking for vcenter portion
                        if vc_permission in global_users_roles and permission.propagate:
                            continue
                        result.setdefault(VCENTER_CONFIG, []).append(vc_permission)
            logger.debug(f"Vcenter permissions: {result.get(VCENTER_CONFIG)}")

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """
        Set method to remediate drifts found in users, roles and permissions.
        """
        status = RemediateStatus.SUCCESS
        errors = []
        try:
            content = context.vc_vmomi_client().content
            authorization_manager = content.authorizationManager
            role_collection = authorization_manager.roleList
            role_name2id = {role.name: role.roleId for role in role_collection}

            # remediate global permissions.
            global_remediate_configs = desired_values.get(GLOBAL_CONFIG)
            if global_remediate_configs:
                logger.debug(f"Remediate drifts for global permissions: {global_remediate_configs}")
                # remediate global permissions
                vc_invsvc_mob3_client = context.vc_invsvc_mob3_client()
                for op, entry in global_remediate_configs:
                    user = entry[NAME]
                    role_id = role_name2id[entry[ROLE]]
                    group = "true" if entry[TYPE] == GROUP else "false"
                    propagate = entry[PROPAGATE]
                    if op == OPER_ADD:
                        logger.debug(
                            f"Adding Permission for Entry: user - {user}, role id: {role_id}, group - {group}, propagate - {propagate}"
                        )
                        vc_invsvc_mob3_client.add_global_permission(user, role_id, group, propagate)
                    elif op == OPER_DELETE:
                        logger.debug(f"Removing Permission for Entry: {user}, group: {group}")
                        vc_invsvc_mob3_client.remove_global_permission(user, group)
                    else:
                        # for modifying an entry, first remove then add.
                        logger.debug(f"Removing Permission for Entry: {user}, group: {group}")
                        vc_invsvc_mob3_client.remove_global_permission(user, group)
                        logger.debug(
                            f"Adding Permission for Entry: user - {user}, role id: {role_id}, group - {group}, propagate - {propagate}"
                        )
                        vc_invsvc_mob3_client.add_global_permission(user, role_id, group, propagate)
                    logger.debug(f"Op: {op} for Global Permission Entry: {entry}")
                logger.info("Global permissions updated successfully")

            # remediate vcenter permissions.
            vc_remediate_configs = desired_values.get(VCENTER_CONFIG)
            if vc_remediate_configs:
                logger.debug(f"Remediate drifts for vCenter permission: {vc_remediate_configs}")
                # get vcenter MOID.
                vc_moid = content.rootFolder
                for op, entry in vc_remediate_configs:
                    user = entry[NAME]
                    role_id = role_name2id[entry[ROLE]]
                    group = entry[TYPE] == GROUP
                    propagate = entry[PROPAGATE]
                    perm = vim.AuthorizationManager.Permission()
                    perm.principal = user
                    perm.roleId = role_id
                    perm.group = group
                    perm.propagate = propagate
                    logger.debug(f"Permission: {perm}")
                    if op == OPER_ADD:
                        authorization_manager.SetEntityPermissions(vc_moid, [perm])
                    elif op == OPER_DELETE:
                        authorization_manager.RemoveEntityPermission(vc_moid, user, group)
                    else:
                        # for modifying an entry, first remove then add.
                        logger.debug(f"Removing: {user}, group: {group}")
                        authorization_manager.RemoveEntityPermission(vc_moid, user, group)
                        logger.debug(f"Adding: {perm}")
                        authorization_manager.SetEntityPermissions(vc_moid, [perm])
                    logger.debug(f"Op: {op} for vCenter permission Entry: {entry}")
                logger.info("vCenter permissions updated successfully")

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED

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

        current_dict = {(entry[NAME], entry[TYPE]): entry for entry in (current or [])}
        desired_dict = {(entry[NAME], entry[TYPE]): entry for entry in (desired or [])}

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

    def _construct_remediate_operation(self, current: List, desired: List) -> List:
        """Find the drift between current and desired users_groups_roles.

        :param current: Current list of users,groups,roles on vCenter.
        :type current: List
        :param desired: Desired list of users,groups,roles on vCenter.
        :type desired: list
        :return: List of drifts dict for remediation
        :rtype: List
        """

        current_dict = {(entry[NAME], entry[TYPE]): entry for entry in (current or [])}
        desired_dict = {(entry[NAME], entry[TYPE]): entry for entry in (desired or [])}
        remediate_drift = []
        all_keys = set(current_dict.keys()).union(set(desired_dict.keys()))

        for key in all_keys:
            current_entry = current_dict.get(key)
            desired_entry = desired_dict.get(key)
            logger.debug(f"Current Entry: {current_entry}, Desired Entry: {desired_entry}")

            if current_entry and desired_entry:
                # Both exist: check for mismatches
                if current_entry != desired_entry:
                    remediate_drift.append((OPER_MODIFY, desired_entry))
            elif current_entry:
                # Extra in current
                remediate_drift.append((OPER_DELETE, current_entry))
            elif desired_entry:
                # Extra in desired
                remediate_drift.append((OPER_ADD, desired_entry))

        return remediate_drift

    def _find_drifts_for_remediate(self, current: Dict, desired: Dict) -> Dict:
        """Find the drift between current and desired users_groups_roles.

        :param current: Current list of users,groups,roles on vCenter.
        :type current: List
        :param desired: Desired list of users,groups,roles on vCenter.
        :type desired: list
        :return: Dict of desired remediate drifts
        :rtype: Dict
        """

        errors = []
        remediate_drifts = {}
        try:
            current = self._normalize_all_domains(current)
            desired = self._normalize_all_domains(desired)
            current_global = current.get(GLOBAL_CONFIG)
            desired_global = desired.get(GLOBAL_CONFIG)
            drift_global = self._construct_remediate_operation(current_global, desired_global)
            if drift_global:
                remediate_drifts[GLOBAL_CONFIG] = drift_global
            current_vcenter = current.get(VCENTER_CONFIG)
            desired_vcenter = desired.get(VCENTER_CONFIG)
            drift_vcenter = self._construct_remediate_operation(current_vcenter, desired_vcenter)
            if drift_vcenter:
                remediate_drifts[VCENTER_CONFIG] = drift_vcenter
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))

        return remediate_drifts, errors

    def _find_all_drifts(self, current_values, desired_values):
        current_non_compliant_configs = {}
        desired_non_compliant_configs = {}
        current_global_values = current_values.get(GLOBAL_CONFIG)
        current_vcenter_values = current_values.get(VCENTER_CONFIG)
        desired_global_values = desired_values.get(GLOBAL_CONFIG)
        desired_vcenter_values = desired_values.get(VCENTER_CONFIG)

        current_global_drifts, desired_global_drifts = self._find_drifts(current_global_values, desired_global_values)
        if current_global_drifts:
            current_non_compliant_configs[GLOBAL_CONFIG] = current_global_drifts
        if desired_global_drifts:
            desired_non_compliant_configs[GLOBAL_CONFIG] = desired_global_drifts
        current_vcenter_drifts, desired_vcenter_drifts = self._find_drifts(
            current_vcenter_values, desired_vcenter_values
        )
        if current_vcenter_drifts:
            current_non_compliant_configs[VCENTER_CONFIG] = current_vcenter_drifts
        if desired_vcenter_drifts:
            desired_non_compliant_configs[VCENTER_CONFIG] = desired_vcenter_drifts

        return current_non_compliant_configs, desired_non_compliant_configs

    def _normalize_all_domains(self, config_values):
        normalized_values = {}

        global_values = config_values.get(GLOBAL_CONFIG)
        vcenter_values = config_values.get(VCENTER_CONFIG)

        if global_values:
            normalized_global_values = [
                {
                    ROLE: item[ROLE],
                    NAME: self._normalize_domain(item[NAME]),
                    TYPE: item[TYPE].upper(),
                    PROPAGATE: item[PROPAGATE],
                }
                for item in global_values
            ]
            normalized_values[GLOBAL_CONFIG] = normalized_global_values
        if vcenter_values:
            normalized_vcenter_values = [
                {
                    ROLE: item[ROLE],
                    NAME: self._normalize_domain(item[NAME]),
                    TYPE: item[TYPE].upper(),
                    PROPAGATE: item[PROPAGATE],
                }
                for item in vcenter_values
            ]
            normalized_values[VCENTER_CONFIG] = normalized_vcenter_values

        return normalized_values

    def _exclude_users(self, config_values, patterns):
        global_configs = []
        vcenter_configs = []
        exclude_local_configs = {}
        global_values = config_values.get(GLOBAL_CONFIG, [])
        for item in global_values:
            if not self._should_filter(item.get(NAME), patterns):
                global_configs.append(item)
                exclude_local_configs.setdefault(GLOBAL_CONFIG, []).append(item)
        vcenter_values = config_values.get(VCENTER_CONFIG, [])
        for item in vcenter_values:
            if not self._should_filter(item.get(NAME), patterns):
                vcenter_configs.append(item)
                exclude_local_configs.setdefault(VCENTER_CONFIG, []).append(item)
        return exclude_local_configs

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired list of users,groups,roles on vCenter.
        :type desired_values: list
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """

        exclude_user_patterns = desired_values.get(EXCLUDE_USER_PATTERNS, [])
        logger.info("Running check compliance for vCenter users_groups_roles control")
        current_values, errors = self.get(context=context)
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # check if need to exclude local users.
        if exclude_user_patterns:
            patterns = self._load_user_exclude_patterns(exclude_user_patterns)
            current_values = self._exclude_users(current_values, patterns)

        self._create_alias_domain_name_mapping(context)
        logger.info(f"domain alias mapping {self.domain_alias_to_name_map}")

        # normalize current and desired config.
        try:
            normalized_current = self._normalize_all_domains(current_values)
            normalized_desired = self._normalize_all_domains(desired_values)
        except Exception as e:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(e)]}

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_non_compliant_configs, desired_non_compliant_configs = self._find_all_drifts(
            normalized_current, normalized_desired
        )
        if current_non_compliant_configs or desired_non_compliant_configs:
            if EXCLUDE_USER_PATTERNS in desired_values:
                del desired_values[EXCLUDE_USER_PATTERNS]
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_values,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Remediate configuration drifts by applying desired values.

        | Sample desired state

        .. code-block:: json

            {
              "global": [
                {
                  "name": "VSPHERE.LOCAL\\SyncUsers",
                  "type": "GROUP",
                  "role": "SyncUsers",
                  "propagate": True
                },
                {
                  "name": "VSPHERE.LOCAL\\Administrator",
                  "type": "USER",
                  "role": "Admin",
                  "propagate": True
                }
              ],
              "vcenter": [
                {
                  "name": "VSPHERE.LOCAL\\Administrator",
                  "type": "USER",
                  "role": "Admin",
                  "propagate": True
                },
                {
                  "name": "VSPHERE.LOCAL\\Administrators",
                  "type": "USER",
                  "role": "Admin",
                  "propagate": False
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VM migrate encryption policy
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running remediation")
        current_values, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        # check if need to exclude local users.
        exclude_user_patterns = desired_values.get(EXCLUDE_USER_PATTERNS, [])
        if exclude_user_patterns:
            patterns = self._load_user_exclude_patterns(exclude_user_patterns)
            current_values = self._exclude_users(current_values, patterns)
        self._create_alias_domain_name_mapping(context)
        remediate_configs, errors = self._find_drifts_for_remediate(current_values, desired_values)
        logger.debug(f"Current configs: {current_values}, Desired configs: {desired_values}")
        logger.debug(f"Drift for remediation: {remediate_configs}")
        if not errors and not remediate_configs:
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}
        elif errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        status, errors = self.set(context, remediate_configs)
        if not errors:
            if EXCLUDE_USER_PATTERNS in desired_values:
                del desired_values[EXCLUDE_USER_PATTERNS]
            result = {consts.STATUS: status, consts.OLD: current_values, consts.NEW: desired_values}
        else:
            result = {consts.STATUS: status, consts.ERRORS: errors}
        return result
