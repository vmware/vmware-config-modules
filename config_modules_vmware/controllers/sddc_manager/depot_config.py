# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

VMWARE_ACCOUNT = "vmware_account"
VMWARE_ACCOUNT_CAMEL_CASE = "vmwareAccount"
USERNAME = "username"  # nosec
PASSWORD = "password"  # nosec
ERROR_CODE = "errorCode"
CUSTOM_EXCEPTION = "Check for valid depot credentials and retry!!"


class DepotConfig(BaseController):
    """Class for Depot config with get and set methods.
    | ConfigID - 1607
    | ConfigTitle - Dedicate an account for downloading updates and patches in SDDC Manager.
    """

    metadata = ControllerMetadata(
        name="depot_config",  # controller name
        path_in_schema="compliance_config.sddc_manager.depot_config",
        # path in the schema to this controller's definition.
        configuration_id="1607",  # configuration id as defined in compliance kit.
        title="Dedicate an account for downloading updates and patches in SDDC Manager.",
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

    def get(self, context: SDDCManagerContext) -> Tuple[Dict, List[Any]]:
        """Get Depot Configuration from SDDC Manager.
        Validation is not done to check if dedicated account is passed. Upto the customer to pass the dedicated account.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :return: Tuple of dict with key "vmware_account" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting Depot Configuration.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.DEPOT_URL
        current_value = {}

        errors = []
        try:
            depot_settings = sddc_manager_rest_client.get_helper(url)
            if VMWARE_ACCOUNT_CAMEL_CASE in depot_settings:
                current_value[VMWARE_ACCOUNT] = {
                    USERNAME: depot_settings.get(VMWARE_ACCOUNT_CAMEL_CASE, {}).get(USERNAME, None),
                    PASSWORD: depot_settings.get(VMWARE_ACCOUNT_CAMEL_CASE, {}).get(PASSWORD, None),
                }
        except Exception as e:
            errors.append(str(e))
            logger.error(f"An Exception occurred: {e}")
            current_value = {}
        return current_value, errors

    def set(self, context: SDDCManagerContext, desired_values) -> Tuple:
        """Set Depot Configuration in SDDC Manager.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired value for the Depot config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """

        logger.info("Setting Depot config for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.DEPOT_URL

        # Update the key names with Camel case for the payload
        payload = {
            VMWARE_ACCOUNT_CAMEL_CASE: {
                USERNAME: desired_values.get(VMWARE_ACCOUNT, {}).get(USERNAME, None),
                PASSWORD: desired_values.get(VMWARE_ACCOUNT, {}).get(PASSWORD, None),
            }
        }
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            sddc_manager_rest_client.put_helper(url, body=payload, raise_for_status=True)

        except Exception as e:
            errors.append(CUSTOM_EXCEPTION + ":" + str(e))
            logger.error(f"An Exception occurred: {e}")
            status = RemediateStatus.FAILED
        return status, errors
