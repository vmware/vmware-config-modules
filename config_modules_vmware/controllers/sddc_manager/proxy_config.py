# Copyright 2024 Broadcom. All Rights Reserved.
import fcntl
import logging
from typing import Any
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

PROXY_ENABLED = "isEnabled"
LCM_APP_PROPERTY_FILE = "/opt/vmware/vcf/lcm/lcm-app/conf/application-prod.properties"
LCM_DEPOT_PROXY_ENABLED = "lcm.depot.adapter.proxyEnabled="
LCM_SERVICE_RESTART = "systemctl restart lcm"


class ProxyConfig(BaseController):
    """Class for Proxy config with get and set methods.
    | ConfigID - 1604
    | ConfigTitle - Enable/Disable lcm proxy configuration.
    """

    metadata = ControllerMetadata(
        name="proxy_config",  # controller name
        path_in_schema="compliance_config.sddc_manager.proxy_config",
        # path in the schema to this controller's definition.
        configuration_id="1604",  # configuration id as defined in compliance kit.
        title="Enable/Disable lcm proxy configuration",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.SDDC_MANAGER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def _get_proxy_setting_by_api(self, sddc_manager_rest_client) -> Tuple[bool, List[Any]]:
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.PROXY_URL
        current_value = None
        errors = []
        try:
            proxy_settings = sddc_manager_rest_client.get_helper(url)
            logger.info(f"Proxy Configuration: {proxy_settings}")
            current_value = proxy_settings.get(PROXY_ENABLED, False)
        except Exception as e:
            errors.append(str(e))
            logger.error(f"An Exception occurred: {str(e)}")
        return current_value, errors

    def _set_proxy_setting_by_api(self, sddc_manager_rest_client, desired_values) -> Tuple:
        """Set Proxy Configuration from SDDC Manager by api.
        :param sddc_manager_rest_client: SDDC Manager API client.
        :type sddc_manager_rest_client: API client
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Set proxy config by API.")
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.PROXY_URL

        # Update the key names with Camel case for the payload
        # There are 1 parameters used in proxy config api:
        # isEnabled - to enable proxy
        payload = {
            PROXY_ENABLED: desired_values,
        }
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            sddc_manager_rest_client.patch_helper(url, body=payload, raise_for_status=True)

        except Exception as e:
            errors.append(str(e))
            logger.error(f"An Exception occurred: {str(e)}")
            status = RemediateStatus.FAILED
        return status, errors

    def _get_proxy_setting_by_file(self, lcm_app_property_file) -> Tuple[bool, List[Any]]:
        """Get Proxy Configuration from SDDC Manager lcm app property file.
        :param lcm_app_property_file: LCM app property file.
        :type lcm_app_property_file: str
        :return: Tuple of proxy enabled boolean and a list of errors if any.
        :rtype: Tuple
        """
        errors = []
        proxy_enabled = None
        try:
            # Read the lcm app property file file
            with open(lcm_app_property_file, "r", encoding="UTF-8") as f:
                lines = f.readlines()
            logger.debug(f"Readlines from file: {lines}")

            for line in lines:
                if line.startswith(LCM_DEPOT_PROXY_ENABLED):
                    value = line.strip().split("=", 1)[1].strip().lower() in (
                        "true",
                        "1",
                        "yes",
                    )
                    proxy_enabled = value
                    return proxy_enabled, errors

        except Exception as e:
            errors.append(str(e))

        return proxy_enabled, errors

    def _set_proxy_setting_by_file(self, lcm_app_property_file, desired_values) -> Tuple:
        """Set Proxy Configuration from SDDC Manager by modifying lcm app property file.
        :param lcm_app_property_file: LCM app property file.
        :type lcm_app_property_file: str
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting Proxy config from LCM file.")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            proxy_enabled_value = "true" if desired_values else "false"
            key_to_new_lines = {LCM_DEPOT_PROXY_ENABLED: f"{LCM_DEPOT_PROXY_ENABLED}{proxy_enabled_value}\n"}

            with open(lcm_app_property_file, "r+", encoding="UTF-8") as f:
                # Acquire an exclusive lock on the file
                fcntl.flock(f, fcntl.LOCK_EX)

                # Read the lines
                lines = f.readlines()

                updated_lines = []
                for line in lines:
                    if line.startswith(LCM_DEPOT_PROXY_ENABLED):
                        updated_lines.append(key_to_new_lines.pop(LCM_DEPOT_PROXY_ENABLED))
                    else:
                        updated_lines.append(line)

                # Add any remaining new lines
                for _, new_line in key_to_new_lines.items():
                    updated_lines.append(new_line)

                # Move the file pointer to the beginning of the file
                f.seek(0)
                # Write the updated lines
                f.writelines(updated_lines)
                # Truncate the file to the new length
                f.truncate()

                # Release the lock
                fcntl.flock(f, fcntl.LOCK_UN)

            # Restart LCM service
            _, _, _ = utils.run_shell_cmd(LCM_SERVICE_RESTART)

        except Exception as e:
            errors.append(str(e))
            status = RemediateStatus.FAILED

        return status, errors

    def get(self, context: SDDCManagerContext) -> Tuple[bool, List[Any]]:
        """Get Proxy Configuration from SDDC Manager.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :return: Tuple of proxy enabled boolean value and a list of errors if any.
        :rtype: Tuple
        """
        logger.info("Getting Proxy Configuration.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        # if VCF version 4.5.0.0 and above, use api to get proxy setting
        if utils.is_newer_or_same_version(context.product_version, sddc_manager_consts.SDDC_MANAGER_VERSION_4_5_0_0):
            return self._get_proxy_setting_by_api(sddc_manager_rest_client)

        # if VCF version lower than 4.5.0.0, get proxy setting from lcp app property file.
        return self._get_proxy_setting_by_file(LCM_APP_PROPERTY_FILE)

    def set(self, context: SDDCManagerContext, desired_values) -> Tuple:
        """Set Proxy Configuration in SDDC Manager.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired value for the Proxy config.
        :type desired_values: boolean
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """

        logger.info("Setting Proxy config for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        # if VCF version 4.5.0.0 and above, use api to get proxy setting
        if utils.is_newer_or_same_version(context.product_version, sddc_manager_consts.SDDC_MANAGER_VERSION_4_5_0_0):
            return self._set_proxy_setting_by_api(sddc_manager_rest_client, desired_values)

        # if VCF version lower than 4.5.0.0, get proxy setting from lcp app property file.
        return self._set_proxy_setting_by_file(LCM_APP_PROPERTY_FILE, desired_values)
