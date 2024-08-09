# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from copy import deepcopy
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.vcenter.utils import vc_profile_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.services.config import Config

logger = LoggerAdapter(logging.getLogger(__name__))
components_mapping = {"authmgmt": "AuthManagement", "appliance": "Appliance"}


class VcProfile(BaseController):
    """
    Class for managing VC profiles.
    """

    metadata = ControllerMetadata(
        name="vc_profile",  # controller name
        path_in_schema="",  # path in the schema to this controller's definition.
        configuration_id="-1",  # configuration id as defined in compliance kit.
        title="vCenter Profile Configuration",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        type=ControllerMetadata.ControllerType.CONFIGURATION,
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def __init__(self):
        super().__init__()
        self.vc_profile_config = Config.get_section("vcenter.profile")

    def get(self, context: VcenterContext, template: dict = None) -> Tuple[dict, List[str]]:
        """Get the current VC profile configuration.

        :param context: Product context instance.
        :type context: VcenterContext
        :param template: Template of requested properties to populate
        :type template: dict
        :return: Tuple of the VC profile config and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting current VC profile configuration.")

        if utils.is_newer_or_same_version(context.product_version, "9.0"):
            return {}, [consts.SKIPPED]
        elif utils.is_newer_or_same_version(context.product_version, "8.0.3"):
            return self._get_8_0_3(context, template)
        else:
            return {}, [consts.SKIPPED]

    def _get_8_0_3(self, context: VcenterContext, template: dict = None) -> Tuple[dict, List[str]]:
        logger.info(f"Getting VC profile configuration for version {context.product_version}")
        current_vc_profile = {}
        errors = []
        try:
            vc_rest_client = context.vc_rest_client()
            url = vc_rest_client.get_base_url() + vc_consts.VC_PROFILE_SETTINGS_URL
            if template:
                # Get requested components
                for component_key in template.keys():
                    if component_key in components_mapping:
                        url += "&components=" + components_mapping[component_key]
                    else:
                        err_msg = f"Unsupported component '{component_key}' in template"
                        logger.error(err_msg)
                        errors.append(err_msg)
                        return current_vc_profile, errors
            else:
                # Get all supported components
                for component in components_mapping.values():
                    url += "&components=" + component
            current_vc_profile = vc_rest_client.get_helper(url)
        except Exception as e:
            logger.error(f"An error occurred for 'get' vc_profile: {e}")
            errors.append(str(e))

        if errors or not template:
            return current_vc_profile, errors

        template = self._populate_template(current_vc_profile, template)
        return template, errors

    def set(self, context: VcenterContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """
        Set - NOT IMPLEMENTED.
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def check_compliance(self, context: VcenterContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and result (for non_compliant) or errors (for failure).
        :rtype: dict
        """
        errors = []
        task_id = None
        task_response = None

        if utils.is_newer_or_same_version(context.product_version, "9.0"):
            errors.append(
                vc_profile_utils.create_error(
                    vc_profile_utils.source_type_config_module,
                    f"Version [{context.product_version}] is not supported for product [{context.product_category}]",
                )
            )
        elif utils.is_newer_or_same_version(context.product_version, "8.0.3"):
            try:
                self._validate_input(desired_values)
                # VC scan drift API doesn't support subset of configuration.
                # So pull current config and merge with input subset to get full config with desired values.

                # Get components from desired values
                get_template = {key: {} for key in desired_values.keys()}
                current_config, get_errors = self.get(context, get_template)
                if get_errors:
                    logger.error(f"Get current config failed with errors. {get_errors}")
                    for get_error in get_errors:
                        errors.append(
                            vc_profile_utils.create_error(
                                vc_profile_utils.source_type_config_module,
                                get_error,
                                remediation_msg=vc_profile_utils.REMEDIATION_RETRY_MESSAGE,
                            )
                        )
                else:
                    # Merge subset with current config
                    desired_values = self._merge_config(current_config, desired_values)
                    # Invoke scan drift VCProfile API
                    try:
                        task_id = context.vc_rest_client().post_helper(
                            url=context.vc_rest_client().get_base_url() + vc_consts.DESIRED_STATE_SCAN_URL,
                            body={"desired_state": desired_values},
                        )
                    except Exception as e:
                        logger.error(f"An error occurred in 'check_compliance' vc_profile: {e}")
                        errors.append(
                            vc_profile_utils.create_error(
                                context.product_category,
                                str(e),
                                context.hostname,
                                context.vc_rest_client().get_base_url() + vc_consts.DESIRED_STATE_SCAN_URL,
                                vc_profile_utils.REMEDIATION_RETRY_MESSAGE,
                            )
                        )
                    # Monitor task until completion.
                    if task_id:
                        logger.info(f"check_compliance initiated on vc: {context.hostname}, task id: {task_id}")
                        task_response = context.vc_rest_client().wait_for_cis_task_completion(
                            task_id=task_id,
                            retry_wait_time=self.vc_profile_config.getint("TaskPollIntervalSeconds"),
                            timeout=self.vc_profile_config.getint("TaskTimeoutSeconds"),
                        )
            except Exception as e:
                logger.error(f"An error occurred for 'check_compliance' vc_profile: {e}")
                errors.append(
                    vc_profile_utils.create_error(
                        vc_profile_utils.source_type_config_module,
                        str(e),
                        remediation_msg=vc_profile_utils.REMEDIATION_RETRY_MESSAGE,
                    )
                )
        else:
            errors.append(
                vc_profile_utils.create_error(
                    vc_profile_utils.source_type_config_module,
                    f"Version [{context.product_version}] is not supported for product [{context.product_category}]",
                )
            )

        # Transform API result into drift spec schema format.
        return vc_profile_utils.transform_to_drift_schema(context, task_id, task_response, errors)

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Remediate - NOT IMPLEMENTED.
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        logger.info(f"{consts.REMEDIATION_SKIPPED_MESSAGE}")
        result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
        return result

    def _populate_template(self, current_value: dict, template: dict) -> dict:
        """Populate the template with the corresponding entries in current_value.

        Example:
        current_value =
        {
            "key1": ["val1.1", "val1.2"],
            "key2": "val2",
            "key3": "val3",
            "key4": [
                {
                    "key4.1": "val4.1",
                    "key4.2": "val4.2"
                },
                {
                    "key4.1": "val4.1",
                    "key4.2": "val4.2"
                }
            ],
            "key5": {},
            "key6": [],
            "key7": ["val7.1"]
        }
        template =
        {
            "key1": [],
            "key2": "",
            "key3": "populated_value",
            "key4": [
                {
                    "key4.1": "",
                    "key4.3": "string"
                }
            ],
            "key5": {
                "key5.1": "string"
            },
            "key6": ["string"],
            "key7": [
                {
                    "key7.1": "string"
                }
            ],
            "non_existent_primitive": "invalid",
            "non_existent_dict": {
                "non_existent_nested_key": "invalid_value"
            },
            "non_existent_list": [],
            "non_existent_primitive_list": ["string"]
        }
        template result =
        {
            "key1": ["val1.1", "val1.2"],
            "key2": "val2",
            "key3": "val3",
            "key4": [
                {
                    "key4.1": "val4.1"
                },
                {
                    "key4.1": "val4.1"
                }
            ],
            "key5": {},
            "key6": [],
            "key7": ["val7.1"]
        }

        :param current_value: The current value of the configuration
        :type current_value: dict
        :param template: The template to populate
        :type template: dict
        """
        for key, value in list(template.items()):
            if key not in current_value:
                logger.debug(f"Deleting {key} from template since it is not in current vc profile")
                del template[key]
            else:
                if value and isinstance(value, dict) and isinstance(current_value[key], dict):
                    self._populate_template(current_value[key], value)
                elif value and isinstance(value, list) and isinstance(current_value[key], list):
                    if isinstance(value[0], dict):
                        template[key] = [
                            self._populate_template(item, deepcopy(value[0])) if isinstance(item, dict) else item
                            for item in current_value[key]
                        ]
                    else:
                        template[key] = current_value[key]
                else:
                    template[key] = current_value[key]

        return template

    def _validate_input(self, desired_values: dict):
        """
        Validate if components in desired values are supported.
        """
        if not desired_values:
            raise ValueError("Desired values cannot be empty")

        for key in desired_values.keys():
            if key not in components_mapping:
                raise ValueError(f"Unsupported component '{key}' in desired values")

    def _merge_config(self, current, desired):
        """
        Merge current with desired values to create a complete spec before sending to VC.
        1. Merge leaf values on non list dict object
        2. List on desired merged as is.

        Example :
        current =
        {
          "appliance": {
            "config1": {
              "key1": "value1",
              "key2": "value2"
            },
            "config2": {
                "key1": "value1"
            },
            "config3": [
                {
                    "key1": "value1"
                },
                {
                    "key2": "value2"
                }
            ]
          }
        }
        desired =
        {
          "appliance": {
            "config1": {
              "key1": "changed",
              "key3": "key3",
              "key4": "value4"
            },
            "config2": {},
            "config3": [
                {
                    "key3": "value3"
                }
            ]
          }
        }
        result =
        {
          "appliance": {
            "config1": {
              "key1": "changed",
              "key2": "value2",
              "key3": "key3",
              "key4": "value4"
            },
            "config3": [
                {
                    "key3": "value3"
                }
            ]
          }
        }
        """
        if isinstance(desired, dict):
            for key, value in desired.items():
                if key in current:
                    # Merge each items
                    if isinstance(value, dict) and not value and current.get(key) != value:
                        # If dict is empty in desired, remove it.
                        # This would ensure entire object to be reported as drift
                        current.pop(key)
                    else:
                        current[key] = self._merge_config(current[key], value)
                else:
                    # Key in desired spec but not in product
                    current[key] = value
            return current
        else:
            # Merge list and leaf values from desired.
            return desired
