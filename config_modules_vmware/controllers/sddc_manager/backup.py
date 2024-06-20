# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))
ENCRYPTION = "encryption"  # nosec
PASSPHRASE = "passphrase"  # nosec
SFTP = "SFTP"  # nosec
PORT_NUMBER = 22
SERVER = "server"
PORT = "port"
PROTOCOL = "protocol"
USERNAME = "username"  # nosec
PASSWORD = "password"  # nosec
DIRECTORY_PATH = "directory_path"
BACKUP_LOCATIONS = "backup_locations"
BACKUP_SCHEDULES = "backup_schedules"
RESOURCE_TYPE = "resource_type"
TAKE_SCHEDULED_BACKUPS = "take_scheduled_backups"
FREQUENCY = "frequency"
DAYS_OF_WEEK = "days_of_week"
HOUR_OF_DAY = "hour_of_day"
MINUTE_OF_HOUR = "minute_of_hour"
TAKE_BACKUP_ON_STATE_CHANGE = "take_backup_on_state_change"
RETENTION_POLICY = "retention_policy"
NUMBER_OF_MOST_RECENT_BACKUPS = "number_of_most_recent_backups"
NUMBER_OF_DAYS_OF_HOURLY_BACKUPS = "number_of_days_of_hourly_backups"
NUMBER_OF_DAYS_OF_DAILY_BACKUPS = "number_of_days_of_daily_backups"
SDDC_MANAGER = "SDDC_MANAGER"
ID = "id"
STATUS = "status"
CUSTOM_EXCEPTION = "Check for valid backup location and backup schedule and retry!!"


class BackupConfig(BaseController):
    """
    Class for backupSettings config with get and set methods.
    | ConfigID - 1600
    | ConfigTitle - Verify SDDC Manager backup.
    """

    metadata = ControllerMetadata(
        name="backup",  # controller name
        path_in_schema="compliance_config.sddc_manager.backup",
        # path in the schema to this controller's definition.
        configuration_id="1600",  # configuration id as defined in compliance kit.
        title="Verify SDDC Manager backup.",
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

    def __gen_ssh_fingerprint(self, backup_server):
        ssh_keyscan_command = f"ssh-keyscan -t rsa {backup_server}"
        ssh_keyscan_std_out, _, _ = utils.run_shell_cmd(ssh_keyscan_command)
        ssh_keygen_command = "ssh-keygen -lf -"
        ssh_keygen_output, _, _ = utils.run_shell_cmd(ssh_keygen_command, input_to_stdin=ssh_keyscan_std_out)
        ssh_fingerprint = ssh_keygen_output.split()[1]
        return ssh_fingerprint

    def get(self, context: SDDCManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get Backup config for audit control.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext
        :return: Tuple of dict and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting BackupSettings control config for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.BACKUP_URL
        errors = []
        try:
            current_backup_response = sddc_manager_rest_client.get_helper(url)
            backup_response = {
                BACKUP_LOCATIONS: [
                    {
                        SERVER: element.get(SERVER),
                        PORT: element.get(PORT),
                        PROTOCOL: element.get(PROTOCOL),
                        USERNAME: element.get(USERNAME),
                        DIRECTORY_PATH: element.get("directoryPath"),
                    }
                    for element in current_backup_response.get("backupLocations", {})
                ],
                BACKUP_SCHEDULES: [
                    {
                        RESOURCE_TYPE: element.get("resourceType"),
                        TAKE_SCHEDULED_BACKUPS: element.get("takeScheduledBackups"),
                        FREQUENCY: element.get(FREQUENCY),
                        DAYS_OF_WEEK: element.get("daysOfWeek"),
                        HOUR_OF_DAY: element.get("hourOfDay"),
                        MINUTE_OF_HOUR: element.get("minuteOfHour"),
                        TAKE_BACKUP_ON_STATE_CHANGE: element.get("takeBackupOnStateChange"),
                        RETENTION_POLICY: {
                            NUMBER_OF_MOST_RECENT_BACKUPS: element.get("retentionPolicy", {}).get(
                                "numberOfMostRecentBackups"
                            ),
                            NUMBER_OF_DAYS_OF_HOURLY_BACKUPS: element.get("retentionPolicy", {}).get(
                                "numberOfDaysOfHourlyBackups"
                            ),
                            NUMBER_OF_DAYS_OF_DAILY_BACKUPS: element.get("retentionPolicy", {}).get(
                                "numberOfDaysOfDailyBackups"
                            ),
                        },
                    }
                    for element in current_backup_response.get("backupSchedules", {})
                ],
            }
        except Exception as e:
            errors.append(f"Error retrieving backup settings: {str(e)}")
            backup_response = {}
        return backup_response, errors

    def set(self, context: SDDCManagerContext, desired_values: Dict) -> Tuple:
        """
        Set Backup config for the audit control.

        :param context: SDDCManagerContext.
        :type context: SDDCManagerContext.
        :param desired_values: Desired values for the DepotSettings config
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages
        :rtype: tuple
        """
        logger.info("Setting BackupSettings control config for audit.")
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.BACKUP_URL

        payload = {
            "encryption": {"passphrase": desired_values.get(ENCRYPTION).get(PASSPHRASE)},
            "backupLocations": [
                {
                    SERVER: location.get(SERVER),
                    "port": PORT_NUMBER,
                    "protocol": SFTP,
                    USERNAME: location.get(USERNAME),
                    PASSWORD: location.get(PASSWORD),
                    "directoryPath": location.get(DIRECTORY_PATH),
                    "sshFingerprint": self.__gen_ssh_fingerprint(location.get(SERVER)),
                }
                for location in desired_values.get(BACKUP_LOCATIONS)
            ],
            "backupSchedules": [
                {
                    "resourceType": SDDC_MANAGER,
                    "takeScheduledBackups": schedule.get(TAKE_SCHEDULED_BACKUPS),
                    FREQUENCY: schedule.get(FREQUENCY),
                    "daysOfWeek": schedule.get(DAYS_OF_WEEK),
                    "hourOfDay": schedule.get(HOUR_OF_DAY),
                    "minuteOfHour": schedule.get(MINUTE_OF_HOUR),
                    "takeBackupOnStateChange": schedule.get(TAKE_BACKUP_ON_STATE_CHANGE),
                    "retentionPolicy": {
                        "numberOfMostRecentBackups": schedule.get(RETENTION_POLICY).get(NUMBER_OF_MOST_RECENT_BACKUPS),
                        "numberOfDaysOfHourlyBackups": schedule.get(RETENTION_POLICY).get(
                            NUMBER_OF_DAYS_OF_HOURLY_BACKUPS
                        ),
                        "numberOfDaysOfDailyBackups": schedule.get(RETENTION_POLICY).get(
                            NUMBER_OF_DAYS_OF_DAILY_BACKUPS
                        ),
                    },
                }
                for schedule in desired_values.get(BACKUP_SCHEDULES)
            ],
        }
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            task_info = sddc_manager_rest_client.put_helper(url, body=payload)
            logger.info(f"Remediation Task ID {task_info.get(ID)}")
            task_status = sddc_manager_rest_client.monitor_task(task_info.get(ID))
            if not task_status:
                raise Exception(f"Remediation failed for task: {task_info.get(ID)} check log for details")
        except Exception as e:
            errors.append(CUSTOM_EXCEPTION + ":" + str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context: SDDCManagerContext, desired_values: Dict) -> Dict:
        """Check compliance of current backup configuration in SDDC Manager.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for backup config.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance.")
        current_value, errors = self.get(context=context)

        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # Update the desired value to match the format of current_value
        desired_value = {
            BACKUP_LOCATIONS: [
                {
                    SERVER: element.get(SERVER),
                    PORT: PORT_NUMBER,
                    PROTOCOL: SFTP,
                    USERNAME: element.get(USERNAME),
                    DIRECTORY_PATH: element.get(DIRECTORY_PATH),
                }
                for element in desired_values.get(BACKUP_LOCATIONS, {})
            ],
            BACKUP_SCHEDULES: [
                {
                    RESOURCE_TYPE: element.get(RESOURCE_TYPE),
                    TAKE_SCHEDULED_BACKUPS: element.get(TAKE_SCHEDULED_BACKUPS),
                    FREQUENCY: element.get(FREQUENCY),
                    DAYS_OF_WEEK: element.get(DAYS_OF_WEEK),
                    HOUR_OF_DAY: element.get(HOUR_OF_DAY),
                    MINUTE_OF_HOUR: element.get(MINUTE_OF_HOUR),
                    TAKE_BACKUP_ON_STATE_CHANGE: element.get(TAKE_BACKUP_ON_STATE_CHANGE),
                    RETENTION_POLICY: {
                        NUMBER_OF_MOST_RECENT_BACKUPS: element.get(RETENTION_POLICY, {}).get(
                            NUMBER_OF_MOST_RECENT_BACKUPS
                        ),
                        NUMBER_OF_DAYS_OF_HOURLY_BACKUPS: element.get(RETENTION_POLICY, {}).get(
                            NUMBER_OF_DAYS_OF_HOURLY_BACKUPS
                        ),
                        NUMBER_OF_DAYS_OF_DAILY_BACKUPS: element.get(RETENTION_POLICY, {}).get(
                            NUMBER_OF_DAYS_OF_DAILY_BACKUPS
                        ),
                    },
                }
                for element in desired_values.get(BACKUP_SCHEDULES, {})
            ],
        }

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".

        current_non_compliant_configs, desired_non_compliant_configs = Comparator.get_non_compliant_configs(
            current_value, desired_value
        )
        if current_non_compliant_configs or desired_non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_non_compliant_configs,
                consts.DESIRED: desired_non_compliant_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT.name}
        return result
