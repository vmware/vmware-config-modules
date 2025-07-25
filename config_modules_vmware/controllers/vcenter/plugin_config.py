# Copyright 2025 Broadcom. All Rights Reserved.
import logging
import os
import re
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import yaml

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))

# cmd timeout set to 30 seconds
CMD_TIMEOUT = 30
# Commands
PLUGIN_CMD_BASE = "dcli +username {} +password {} +show com vmware vcenter ui plugins "
PLUGIN_GET_CMD = "get "
PLUGIN_LIST_CMD = "list"
PLUGIN_ID = "--plugin-id "
TO_REGISTER = "+"
TO_UNREGISTER = "-"
TO_UPDATE = "*"
ID = "id"
TYPE = "type"

DESIRED_KEYS_FOR_AUDIT = [
    "id",
    "type",
    "vendor",
]


class PluginConfig(BaseController):
    """Manage vCenter Server plugin configs.

    | Config Id - 406
    | Config Title - vCenter Server plugins must be verified.
    """

    metadata = ControllerMetadata(
        name="plugin_config",  # controller name
        path_in_schema="compliance_config.vcenter.plugin_config",  # path in the schema to this controller's definition.
        configuration_id="406",  # configuration id as defined in compliance kit.
        title="vCenter Server plugins must be verified.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["vcenter"],  # location where functional tests are run.
    )

    def get(self, context: VcenterContext) -> Tuple[dict, List[Any]]:
        """Get vCenter server plugin config.

        | Sample get call output:

        .. code-block:: json

            [
              {
                "id": "com.vmware.lcm.client",
                "vendor": ""VMware, Inc.",
                "type": "REMOTE",
              },
              {
                "id": "com.vmware.vlcm.client",
                "vendor": ""VMware, Inc.",
                "type": "REMOTE",
              },
              {
                "id": "com.vmware.vum.client",
                "vendor": ""VMware, Inc.",
                "type": "LOCAL",
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict and a list of error messages if any.
        :rtype: tuple
        """
        logger.info("Getting vCenter server plugin config from vCenter")
        result = []
        errors = []
        try:
            # this control only supported on VCF 5.2 or newer version.
            if not utils.is_newer_or_same_version(context.product_version, "8.0.2"):
                return [], [consts.SKIPPED]

            result = self._get_plugin_config(context)
        except Exception as e:
            err_msg = self._sanitize_output(str(e))
            logger.error(f"An error occurred: {err_msg}")
            errors.append(err_msg)
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """Sets vCenter plugin config.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the DNS config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting plugin config")
        errors = []
        status = RemediateStatus.SUCCESS

        try:
            # this control only supported on VCF 5.2 or newer version.
            if not utils.is_newer_or_same_version(context.product_version, "8.0.2"):
                return RemediateStatus.SKIPPED, [consts.CONTROL_NOT_AUTOMATED]

            errors = self._apply_plugin_config(context, desired_values)
            if errors:
                status = RemediateStatus.FAILED
        except Exception as e:
            err_msg = self._sanitize_output(str(e))
            logger.error(f"An error occurred: {err_msg}")
            errors.append(err_msg)
            status = RemediateStatus.FAILED

        return status, errors

    def _collect_vapi_whl_files(self, whl_dir: Path) -> List[str]:
        """Helper method to collect all whl files under a path and put them into a new path."""
        whl_files = sorted(whl_dir.glob("*.whl"))
        whl_paths = [str(whl.resolve()) for whl in whl_files]
        return [str(whl_dir.resolve())] + whl_paths

    def _get_environment_variables(self) -> Dict[str, str]:
        """Helper method to return all environment variables needed."""
        environment = {
            "VMWARE_PYTHON_BIN": "/usr/bin/python",
            "VMWARE_PYTHON_PATH": "/usr/lib/vmware/site-packages",
            "VMWARE_PYTHON_MODULES_HOME": "/usr/lib/vmware/site-packages/cis",
        }

        # for path variable "VMWARE_VAPI_PYTHONPATH", need to collect whl files
        whl_files = self._collect_vapi_whl_files(Path("/usr/lib/vmware-vapi/lib/python"))
        logger.debug(f"Collected whl files {whl_files}")
        environment["VMWARE_VAPI_PYTHONPATH"] = os.pathsep.join(whl_files)

        # check if there are existing values n these env variables.
        for key, value in environment.items():
            exist_val = os.environ.get(key)
            if exist_val:
                logger.debug(f"Existing env {key} value : {exist_val}")
                new_paths = value.split(os.pathsep)
                exist_paths = exist_val.split(os.pathsep)
                all_paths = new_paths + exist_paths
                # remove redudant path
                seen = set()
                combined_paths = [p for p in all_paths if p and not (p in seen or seen.add(p))]
                environment[key] = os.pathsep.join(combined_paths)
                logger.debug(f"Merged env {key} value : {environment[key]}")
        logger.debug(f"Environment variables: {environment}")
        return environment

    @staticmethod
    def _sanitize_output(output: str) -> str:
        """Remove sensitive information from content.
           It works for the format of "'+username', 'username', '+password', 'passwd'"

        :param output: exception output content.
        :type output: str
        """

        # watch +username and +password pattern
        pattern = r"([\"']\+\w+[\"']\s*,\s*)([\"'][^\"']+[\"'])"
        # replace sensitive info
        return re.sub(pattern, "", output)

    def _get_plugin_config(self, context: VcenterContext) -> List:
        """Get vCenter server plugin config.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: A list of plugin configs
        :rtype: List
        """

        # get environment variables.
        env = self._get_environment_variables()

        plugin_cmd_base = PLUGIN_CMD_BASE.format(context._username, context._password)
        plugin_list_cmd = plugin_cmd_base + PLUGIN_LIST_CMD

        # retrieve a list of plugins identified by id
        out, _, _ = utils.run_shell_cmd(command=plugin_list_cmd, timeout=CMD_TIMEOUT, env=env)
        logger.debug(f"Retrieved plugins: {out}")

        plugin_configs = []
        plugins = yaml.safe_load(out)
        logger.debug(f"Plugins in yaml format: {plugins}")
        plugin_id_list = [plugin.get("id") for plugin in plugins.get("plugins", [])]

        # retrieve detailed plugin information
        for plugin_id in plugin_id_list:
            try:
                plugin_get_cmd = plugin_cmd_base + PLUGIN_GET_CMD + PLUGIN_ID + plugin_id
                out, _, _ = utils.run_shell_cmd(command=plugin_get_cmd, timeout=CMD_TIMEOUT, env=env)
                logger.debug(f"Retrieved plugin - {plugin_id} details: {out}")
                plugin_info = yaml.safe_load(out)
                plugin_item = {
                    "id": plugin_id,
                    "type": plugin_info.get("type", None),
                    "vendor": plugin_info.get("vendor", None),
                }
                plugin_configs.append(plugin_item)
            except Exception as e:
                err_msg = self._sanitize_output(str(e))
                logger.debug(f"Got exception when retrieve the detail of {plugin_id} with message {err_msg}")
                plugin_item = {
                    "id": plugin_id,
                    "type": None,
                    "vendor": None,
                }
                plugin_configs.append(plugin_item)

        logger.debug(f"vCenter server plugin configs: {plugin_configs}")
        return plugin_configs

    def _is_entry_diff(self, current_entry: Dict, desired_entry: Dict) -> bool:
        """Check if two entries are different.

        :param current_entry: Current entry of plugins.
        :type current_entry: Dict
        :param desired_entry: Desired entry of plugins.
        :type desired_entry: Dict
        :return: True if two entries differ.
        :rtype: bool
        """

        # only compare keys for audit.
        keys_to_compare = DESIRED_KEYS_FOR_AUDIT
        for key in keys_to_compare:
            if current_entry.get(key) != desired_entry.get(key):
                return True
        return False

    def _find_drifts(self, current: List, desired: List) -> List:
        """From current and desired, figure out which to add/delete/update..

        :param current: Current list of plugins.
        :type current: List
        :param desired: Desired list of plugins.
        :type desired: list
        :return: List of drifts dict for compliance check or remediation
        :rtype: List
        """

        # user keys in desired key list for drift comparision
        current_dict = {(entry[ID], entry[TYPE]): entry for entry in (current or [])}
        desired_dict = {(entry[ID], entry[TYPE]): entry for entry in (desired or [])}
        config_drift = []

        all_keys = set(current_dict.keys()).union(set(desired_dict.keys()))
        for key in all_keys:
            current_entry = current_dict.get(key)
            desired_entry = desired_dict.get(key)
            logger.debug(f"Current Entry: {current_entry}, Desired Entry: {desired_entry}")

            if current_entry and desired_entry:
                # Both exist: check for mismatches
                if self._is_entry_diff(current_entry, desired_entry):
                    # to modify an entry, use desired values and update method.
                    config_drift.append((TO_UPDATE, desired_entry))
            elif current_entry:
                # Extra in current
                config_drift.append((TO_UNREGISTER, current_entry))
            elif desired_entry:
                # Extra in desired
                config_drift.append((TO_REGISTER, desired_entry))

        return config_drift

    def _apply_plugin_config(self, context, remediate_configs) -> List:
        content = context.vc_vmomi_client().content
        extension_manager = content.extensionManager
        errors = []

        for op, plugin in remediate_configs:
            logger.debug(f"Op: {op} for plugin: {plugin}")
            plugin_id = plugin[ID]
            if op != TO_UNREGISTER:
                err_msg = f"Register or Update for plugin {plugin_id} is not supported at now."
                logger.debug(err_msg)
                errors.append(err_msg)
            else:  # op == TO_UNREGISTER
                logger.debug(f"Unregister plugin: {plugin_id}")
                if plugin[TYPE] == "LOCAL":
                    err_msg = f"Can't unregister local  plugin {plugin}."
                    logger.debug(err_msg)
                    errors.append(err_msg)
                else:
                    # find plugin to be unregistered
                    extension = extension_manager.FindExtension(plugin_id)
                    if not extension:
                        # can't unregister the plugin if not found
                        err_msg = f"plugin {plugin_id} not found."
                        logger.debug(err_msg)
                        errors.append(err_msg)
                    else:
                        extension_manager.UnregisterExtension(plugin_id)
        return errors

    def _exclude_plugins(self, plugins, exclude_plugins):
        filtered_plugins = []
        for plugin in plugins:
            if plugin.get("id", None) not in exclude_plugins:
                filtered_plugins.append(plugin)
        return filtered_plugins

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """Check compliance of current plugin configuration in vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the vCenter plugin config.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance for plugin config.")
        current_values, errors = self.get(context=context)

        if errors:
            if len(errors) == 1 and errors[0] == consts.SKIPPED:
                return {
                    consts.STATUS: ComplianceStatus.SKIPPED,
                    consts.ERRORS: [consts.CONTROL_NOT_APPLICABLE],
                }
            # If errors are seen during get, return "FAILED" status with errors.
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        filtered_desired_values = [
            utils.filter_dict_keys(dict_item, DESIRED_KEYS_FOR_AUDIT) for dict_item in desired_values.get("plugins", [])
        ]
        # Check if we need to exclude specific plugins.
        exclude_plugins = desired_values.get("exclude_plugins", [])
        logger.debug(f"User input plugins or plugin id pattern to be excluded from compliance check: {exclude_plugins}")
        current_values = self._exclude_plugins(current_values, exclude_plugins)

        current_configs, desired_configs = Comparator.get_non_compliant_configs(current_values, filtered_desired_values)
        if current_configs or desired_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_configs,
                consts.DESIRED: desired_configs,
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
              "id": "com.vmware.vum.client",
              "vendor": "VMware, Inc.",
              "type": "LOCAL",
              "versions": [
                "8.0.3.24091160"
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VM migrate encryption policy
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running remediation for plugin config.")
        current_values, errors = self.get(context=context)

        if errors:
            if len(errors) == 1 and errors[0] == consts.SKIPPED:
                return {
                    consts.STATUS: RemediateStatus.SKIPPED,
                    consts.ERRORS: [consts.CONTROL_NOT_APPLICABLE],
                }
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        # Check if we need to exclude specific plugins.
        exclude_plugins = desired_values.get("exclude_plugins", [])
        logger.debug(f"User input plugins or plugin id pattern to be excluded from compliance check: {exclude_plugins}")
        current_values = self._exclude_plugins(current_values, exclude_plugins)
        # find drift for remediation
        desired_plugin_values = desired_values.get("plugins", [])
        remediate_configs = self._find_drifts(current_values, desired_plugin_values)
        logger.debug(f"Current configs: {current_values}, Desired configs: {desired_plugin_values}")
        logger.debug(f"Drift for remediation: {remediate_configs}")
        if not remediate_configs:
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}
        elif errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        status, errors = self.set(context, remediate_configs)
        if not errors:
            return {consts.STATUS: status, consts.OLD: current_values, consts.NEW: desired_plugin_values}
        return {consts.STATUS: status, consts.ERRORS: errors}
