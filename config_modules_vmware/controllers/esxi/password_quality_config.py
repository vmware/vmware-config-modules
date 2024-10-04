# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils import esxi_advanced_settings_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))

SETTINGS_NAME = "Security.PasswordQualityControl"
SYSTEM_DEFAULTS = {"retry": 3, "min": "disabled,disabled,disabled,7,7", "max": 40, "passphrase": 3, "similar": "deny"}


class PasswordQualityConfig(BaseController):
    """ESXi password quality control configuration.

    | Config Id - 22
    | Config Title - The ESXi host must enforce password complexity.
    """

    metadata = ControllerMetadata(
        name="password_quality_config",  # controller name
        path_in_schema="compliance_config.esxi.password_quality_config",
        # path in the schema to this controller's definition.
        configuration_id="22",  # configuration id as defined in compliance kit.
        title="The ESXi host must enforce password complexity.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def _parse_config_string(self, config_str) -> Dict:
        """parse config string retrieved from advanced setting.
        :param config_str: configuration string.
        :type config_str: string
        :return: dict of quality control configs
        :rtype: dict
        """
        password_quality_config = {}
        for key_value in config_str.split():
            key, value = key_value.split("=")
            password_quality_config[key] = int(value) if key not in ["min", "similar"] else value
        return password_quality_config

    def _create_config_string(self, desired_values) -> str:
        """create config string desired values.
        :param desired_values: desired configurations.
        :type desired_value: dict
        :return: configs string
        :rtype: string
        """
        config_str = ""
        for key, value in desired_values.items():
            config_str += f"{key}={value} "
        return config_str.rstrip()

    def _pre_compare_process(self, configs, desired_values) -> Tuple[dict, dict]:
        """Process config string and desired values before compliance check.
        :param configs: configurations retrieved from host.
        :type configs: dict
        :param desired_values: desired configurations.
        :type desired_value: dict
        :return: tuple of processed configs and desired values
        :rtype: tuple
        """
        # add missing keys from one dict to another with default values
        all_keys = set(configs.keys()).union(desired_values.keys())
        for key in all_keys:
            if key not in desired_values:
                desired_values[key] = SYSTEM_DEFAULTS[key]
            if key not in configs:
                configs[key] = SYSTEM_DEFAULTS[key]
        return configs, desired_values

    def get(self, context: HostContext) -> Tuple[dict, List[str]]:
        """Get password quality control configuration for esxi host.

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of dict for password quality control configs and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting password quality control configuration for esxi.")
        errors = []
        password_quality_config = {}
        try:
            # Fetch configuration from advanced option setting.
            result = esxi_advanced_settings_utils.invoke_advanced_option_query(context.host_ref, prefix=SETTINGS_NAME)
            password_quality_config = self._parse_config_string(result[0].value)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return password_quality_config, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set password quality control configurations for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: dict of desired configs to update ESXi password quality control configurations.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting password quality control configs in advanced option for esxi.")
        password_quality_config = self._create_config_string(desired_values)
        logger.debug(f"Password quality control configs: {password_quality_config}")
        host_option = vim.option.OptionValue(key=SETTINGS_NAME, value=password_quality_config)
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_advanced_settings_utils.update_advanced_option(context.host_ref, host_option=host_option)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context: HostContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: ESX context instance.
        :type context: HostContext
        :param desired_values: Desired values for rulesets.
        :type desired_values: Any
        :return: Dict of status and list of current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance for ESXi password quality control configurations")
        password_quality_config, errors = self.get(context=context)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        password_quality_config, desired_values = self._pre_compare_process(password_quality_config, desired_values)
        current, desired = Comparator.get_non_compliant_configs(password_quality_config, desired_values)
        if current or desired:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current,
                consts.DESIRED: desired,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
