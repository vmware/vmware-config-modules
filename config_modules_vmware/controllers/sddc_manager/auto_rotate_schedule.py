# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))
TASK_ID = "id"
ESXI = "ESXI"
PSC = "PSC"
AUTO_ROTATE_CREDENTIALS = "credentials"
AUTO_ROTATE_FREQUENCY = "frequency"
RESOURCE_TYPE = "resource_type"
RESOURCE_NAME = "resource_name"
CREDENTIAL_TYPE = "credential_type"
USERNAME = "username"
FREQUENCY = "frequency"
RESOURCE = "resource"
AUTO_ROTATE_POLICY = "autoRotatePolicy"


class AutoRotateScheduleConfig(BaseController):
    """
    Class for AutoRotateSchedule config with get and set methods.
    | ConfigID - 1609
    | ConfigTitle - SDDC Manager must schedule automatic password rotation.
    """

    metadata = ControllerMetadata(
        name="credential_auto_rotate_policy",  # controller name
        path_in_schema="compliance_config.sddc_manager.credential_auto_rotate_policy",
        # path in the schema to this controller's definition.
        configuration_id="1609",  # configuration id as defined in compliance kit.
        title="SDDC Manager must schedule automatic password rotation.",
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

    def __get_non_compliant_credentials(self, current_value, desired_value):
        non_compliant_credentials = {
            AUTO_ROTATE_CREDENTIALS: [
                {
                    RESOURCE_TYPE: element.get(RESOURCE_TYPE),
                    RESOURCE_NAME: element.get(RESOURCE_NAME),
                    CREDENTIAL_TYPE: element.get(CREDENTIAL_TYPE),
                    USERNAME: element.get(USERNAME),
                    FREQUENCY: element.get(FREQUENCY),
                }
                for element in current_value.get(AUTO_ROTATE_CREDENTIALS, [])
                if element.get(FREQUENCY) != desired_value.get(FREQUENCY)
            ]
        }
        return non_compliant_credentials

    def get(self, context: SDDCManagerContext):
        """
        Get AutoRotateSchedule config of credentials.

        :param context: SddcManagerContext.
        :type context: SddcManagerContext
        :return: Tuple of dict with key "credentials" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting AutoRotateSchedule control config for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.CREDENTIALS_URL
        errors = []
        try:
            get_response = sddc_manager_rest_client.get_helper(url)
            auto_rotate_schedule_credentials = {
                AUTO_ROTATE_CREDENTIALS: [
                    {
                        RESOURCE_TYPE: element.get(RESOURCE).get("resourceType"),
                        RESOURCE_NAME: element.get(RESOURCE).get("resourceName"),
                        CREDENTIAL_TYPE: element.get("credentialType"),
                        USERNAME: element.get(USERNAME),
                        FREQUENCY: (
                            element.get(AUTO_ROTATE_POLICY).get("frequencyInDays")
                            if (AUTO_ROTATE_POLICY in element)
                            else ""
                        ),
                    }
                    for element in get_response.get("elements", {})
                    if ESXI not in element.get(RESOURCE, {}).get("resourceType")
                ]
            }
        except Exception as e:
            errors.append(str(e))
            auto_rotate_schedule_credentials = {}
        return auto_rotate_schedule_credentials, errors

    def set(self, context, desired_values):
        """
        Set AutoRotateSchedule config for the audit control.

        :param context: SddcManagerContext.
        :type context: SddcManagerContext.
        :param desired_values: Desired values for the AutoRotateSchedule config
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages
        :rtype: tuple
        """
        logger.info("Setting AutoRotateSchedule control config for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.CREDENTIALS_URL
        response, errors = self.get(context=context)
        payload = {
            "operationType": "UPDATE_AUTO_ROTATE_POLICY",
            "elements": [
                {
                    "resourceName": element.get("resource_name"),
                    "resourceType": element.get("resource_type"),
                    "credentials": [
                        {"credentialType": element.get("credential_type"), "username": element.get("username")}
                    ],
                }
                for element in response.get("credentials", {})
                if PSC not in element.get("resource_type")
            ],
            "autoRotatePolicy": {
                "frequencyInDays": desired_values.get(AUTO_ROTATE_FREQUENCY),
                "enableAutoRotatePolicy": "true",
            },
        }
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            task_info = sddc_manager_rest_client.patch_helper(url, body=payload)
            logger.info(f"Remediation Task ID {task_info.get(TASK_ID)}")
            task_status = sddc_manager_rest_client.monitor_task(task_info.get(TASK_ID))
            if not task_status:
                raise Exception(f"Remediation failed for task: {task_info.get(TASK_ID)} check log for details")
        except Exception as e:
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context, desired_values: Dict) -> Dict:
        """
        Check compliance of auto rotate configuration.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Dict
        :return: Dict of status and current/desired value( for non_compliant) or errors ( for failure).
        :rtype: tuple
        """
        logger.info("Checking compliance.")
        current_value, errors = self.get(context=context)
        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_credentials = self.__get_non_compliant_credentials(current_value, desired_values)
        if non_compliant_credentials.get(AUTO_ROTATE_CREDENTIALS):
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_credentials,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context, desired_values: Dict) -> Dict:
        """
        Remediate configuration drifts.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Dict
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        logger.info("Running remediation")
        current_value, errors = self.get(context=context)
        # Errors seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        desired_value = desired_values
        non_compliant_credentials = self.__get_non_compliant_credentials(current_value, desired_value)
        if non_compliant_credentials.get(AUTO_ROTATE_CREDENTIALS):
            status, errors = self.set(context=context, desired_values=desired_value)
        else:
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ["Control already compliant"]}

        if not errors:
            result = {consts.STATUS: status, consts.OLD: non_compliant_credentials, consts.NEW: desired_value}
        else:
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        return result
