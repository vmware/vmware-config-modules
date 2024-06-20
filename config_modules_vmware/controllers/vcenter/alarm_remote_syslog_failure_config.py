# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.vcenter.utils import vc_alarms_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import Comparator
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList

logger = LoggerAdapter(logging.getLogger(__name__))

ESX_REMOTE_SYSLOG_FAILURE_EVENT = "esx.problem.vmsyslogd.remote.failure"


class AlarmRemoteSyslogFailureConfig(BaseController):
    """Manage esxi remote syslog failure alarm config with get and set methods.

    | Config Id - 0000
    | Config Title - Configure an alarm to alert on ESXi remote syslog connection.

    Remediation is supported only for creation of alarm. Any update/delete in an alarm is not supported.
    """

    def __init__(self):
        super().__init__()
        self.comparator_option = ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON
        self.instance_key = vc_alarms_utils.ALARM_NAME

    metadata = ControllerMetadata(
        name="alarm_esx_remote_syslog_failure",  # controller name
        path_in_schema="compliance_config.vcenter.alarm_esx_remote_syslog_failure",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Configure an alert if an error occurs with the ESXi remote syslog connection.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """
        Get alarms for alarm_esx_remote_syslog_failure event type on vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of alarm info and a list of error messages if any.
        :rtype: tuple
        """
        errors = []
        result = []
        try:
            logger.info(f"Get all the alarms with eventId {ESX_REMOTE_SYSLOG_FAILURE_EVENT}.")
            content = context.vc_vmomi_client().content
            alarm_manager = content.alarmManager

            # Get all alarm definitions (currently there is no support to query an alarm for specific event)
            alarm_definitions = alarm_manager.GetAlarm(content.rootFolder)
            alarms = []

            # Fetch details of all the alarms for which any expression within an alarm has eventId :
            # ESX_REMOTE_SYSLOG_FAILURE_EVENT
            for alarm_def in alarm_definitions:
                for expression in alarm_def.info.expression.expression:
                    if isinstance(expression, vim.alarm.EventAlarmExpression):
                        if expression.eventTypeId == ESX_REMOTE_SYSLOG_FAILURE_EVENT:
                            target_type = vc_alarms_utils.get_target_type(expression.objectType)
                            alarms.append(vc_alarms_utils.get_alarm_details(alarm_def, target_type))
            result = alarms

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: List[Dict]) -> Tuple[str, List[Any]]:
        """
        Set alarms for alarm_esx_remote_syslog_failure event type on vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: List of dict objects with alarm info for the esx syslog failure alarm configuration.
        :type desired_values: list[dict]
        :return: Tuple of remediation status and a list of error messages if any.
        :rtype: tuple
        """
        errors = []
        status = RemediateStatus.SUCCESS
        logger.info(f"Set the desired alarms for eventId {ESX_REMOTE_SYSLOG_FAILURE_EVENT}.")
        # Iterate over all the alarm in desired list of alarms and create an alarm for each of them.
        for desired_alarm_value in desired_values:
            alarm_name = desired_alarm_value.get(vc_alarms_utils.ALARM_NAME)
            logger.info(f"Create the alarm with name: {alarm_name}.")
            try:
                content = context.vc_vmomi_client().content
                spec = vc_alarms_utils.create_alarm_spec(desired_alarm_value, ESX_REMOTE_SYSLOG_FAILURE_EVENT)
                content.alarmManager.CreateAlarm(content.rootFolder, spec)
            except vim.fault.DuplicateName:
                logger.exception(f"Error creating duplicate alarm {alarm_name}")
                status = RemediateStatus.FAILED
                errors = [
                    f"An alarm with same name '{alarm_name}' already exists.",
                    "Manual remediation required for an update or deletion.",
                    "Please either update/delete that alarm manually or choose different alarm name.",
                ]
            except Exception as e:
                logger.exception(f"An error occurred: {e}")
                status = RemediateStatus.FAILED
                errors = [f"Error during {alarm_name} creation with error {str(e)}."]
        return status, errors

    def check_compliance(self, context: VcenterContext, desired_values: List[Dict]) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Vcenter context instance.
        :type context: VcenterContext
        :param desired_values: List of dict objects with info for the esx remote syslog failure alarm configuration.
        :type desired_values: list[dict]
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance.")
        current_value, errors = self.get(context=context)
        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # Use case is to have at least one alarm with that eventTypeId.
        # Numerous alarms can be configured with same eventId. Check compliance should be run against only on the
        # list of alarms which are part of desired spec to avoid showing non_compliant due to non-interested alarms.
        # Can remove this filtering if there is a use case where user wants to run check compliance for all the alarms.
        desired_alarm_names = {item[vc_alarms_utils.ALARM_NAME] for item in desired_values}
        filtered_current_values = [
            item for item in current_value if item[vc_alarms_utils.ALARM_NAME] in desired_alarm_names
        ]

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_non_compliant_configs, desired_non_compliant_configs = Comparator.get_non_compliant_configs(
            filtered_current_values, desired_values, self.comparator_option, self.instance_key
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
