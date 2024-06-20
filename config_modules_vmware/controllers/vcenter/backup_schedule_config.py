# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))

DESIRED_KEYS_FOR_AUDIT = [
    "backup_schedule_name",
    "enable_backup_schedule",
    "backup_location_url",
    "backup_server_username",
    "backup_parts",
    "recurrence_info",
    "retention_info",
]


class RecurrenceType(Enum):
    """Manage recurrence types.

    :meta private:
    """

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    CUSTOM = "CUSTOM"


class BackupScheduleConfig(BaseController):
    """Manage vCenter back schedule config with get and set methods.

    | Config Id - 1220
    | Config Title - The vCenter Server configuration must be backed up on a regular basis.

    """

    metadata = ControllerMetadata(
        name="backup_schedule_config",  # controller name
        path_in_schema="compliance_config.vcenter.backup_schedule_config",  # path in the schema to this controller's definition.
        configuration_id="1220",  # configuration id as defined in compliance kit.
        title="The vCenter Server configuration must be backed up on a regular basis.",
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

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """Get backup schedule config from vCenter.

        | sample get call output

        .. code-block:: json

            {
              "backup_schedule_name": "DailyBackup",
              "enable_backup_schedule": true,
              "backup_location_url": "sftp://10.0.0.250:/root/backups",
              "backup_server_username": "root",
              "backup_parts": [
                "seat",
                "common"
              ],
              "recurrence_info": {
                "hour": 1,
                "minute": 0,
                "recurrence_type": "DAILY"
              },
              "retention_info": {
                "max_count": 5
              }
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict with key "servers" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting Backup schedule config.")
        errors = []
        try:
            backup_schedule_config = self.__get_backup_schedule(context)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            backup_schedule_config = {}
        return backup_schedule_config, errors

    def __get_backup_schedule(self, context: VcenterContext) -> Dict:
        """Get backup schedule configs from vCenter

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Dict of backup schedule config
        :rtype: Dict
        """
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.BACKUP_SCHEDULE_URL
        backup_schedule_response = vc_rest_client.get_helper(url)

        if not backup_schedule_response:
            return {}

        schedule_name, schedule_config = list(backup_schedule_response.items())[0]
        backup_schedule_config = {
            "backup_schedule_name": schedule_name,
            "enable_backup_schedule": schedule_config.get("enable"),
            "backup_location_url": schedule_config.get("location"),
            "backup_server_username": schedule_config.get("location_user"),
            "backup_parts": schedule_config.get("parts"),
            "recurrence_info": schedule_config.get("recurrence_info"),
            "retention_info": schedule_config.get("retention_info"),
        }
        # Set recurrence type based on recurrence info
        backup_schedule_config["recurrence_info"]["recurrence_type"] = self.__get_recurrence_type(
            schedule_config.get("recurrence_info")
        )
        return backup_schedule_config

    @staticmethod
    def __get_recurrence_type(recurrence_info: Dict) -> Union[str, None]:
        """
        Get recurrence type from recurrence info.

        :param recurrence_info: Dict containing recurrence info.
        :type recurrence_info: Dict
        :return: Recurrence type which can be any of ['DAILY', 'WEEKLY', 'CUSTOM']
        :rtype: str or None
        """
        days = recurrence_info.get("days", [])

        if len(days) == 1:
            return RecurrenceType.WEEKLY.value
        elif len(days) == 0:
            return RecurrenceType.DAILY.value
        else:
            return RecurrenceType.CUSTOM.value

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """Set Backup schedule config for vCenter.

        | Sample desired state for Backup schedule config

        .. code-block:: json

            {
              "backup_schedule_name": "DailyBackup",
              "enable_backup_schedule": true,
              "backup_location_url": "sftp://10.0.0.250:/root/backups",
              "backup_server_username": "root",
              "backup_server_password": "HFKMo18wrwBh.k.H",
              "backup_encryption_password": "HFKMo18wrwBh.k.H",
              "backup_parts": [
                "seat",
                "common"
              ],
              "recurrence_info": {
                "recurrence_type": "DAILY",
                "hour": 1,
                "minute": 0
              },
              "retention_info": {
                "max_count": 5
              }
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the vCenter backup schedule config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        logger.info("Setting Backup schedule config for remediation.")

        errors = []
        status = RemediateStatus.SUCCESS
        try:
            self.__set_backup_schedule(context, desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def __delete_backup_schedule(self, context: VcenterContext):
        """Delete a backup schedule if exists.

        :param context:
        :return:
        """
        vc_rest_client = context.vc_rest_client()
        get_url = vc_rest_client.get_base_url() + vc_consts.BACKUP_SCHEDULE_URL
        backup_schedule_config = vc_rest_client.get_helper(get_url)

        if not backup_schedule_config:
            return

        if backup_schedule_config and isinstance(backup_schedule_config, dict) and len(backup_schedule_config) == 1:
            schedule_name, _ = list(backup_schedule_config.items())[0]
            delete_url = vc_rest_client.get_base_url() + vc_consts.BACKUP_SCHEDULE_BY_NAME_URL.format(schedule_name)
            vc_rest_client.delete_helper(delete_url)

    def __set_backup_schedule(self, context: VcenterContext, desired_values: Dict):
        """Set backup schedule configs in vCenter

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values as dict.
        :type desired_values: Dict
        :return: None
        """
        vc_rest_client = context.vc_rest_client()
        # cleanup existing schedules
        self.__delete_backup_schedule(context)

        payload = {"schedule": desired_values.get("backup_schedule_name"), "spec": {}}
        backup_password = desired_values.get("backup_encryption_password")
        if backup_password:
            payload["spec"]["backup_password"] = backup_password

        payload["spec"]["enable"] = desired_values.get("enable_backup_schedule")
        payload["spec"]["location"] = desired_values.get("backup_location_url")
        payload["spec"]["location_user"] = desired_values.get("backup_server_username")

        location_password = desired_values.get("backup_server_password")
        if location_password:
            payload["spec"]["location_password"] = location_password

        payload["spec"]["parts"] = desired_values.get("backup_parts")
        payload["spec"]["recurrence_info"] = desired_values.get("recurrence_info")
        del payload["spec"]["recurrence_info"]["recurrence_type"]
        payload["spec"]["retention_info"] = desired_values.get("retention_info")

        # create a new schedule
        create_schedule_url = vc_rest_client.get_base_url() + vc_consts.BACKUP_SCHEDULE_URL
        vc_rest_client.post_helper(create_schedule_url, body=payload)

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Check compliance of vCenter backup schedules.

        | Password is not considered during compliance check.
        | Due to security restrictions we cannot get the current password. But it is still used for remediation.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for vCenter backup schedule config.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        backup_schedule_config, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        filtered_desired_values = utils.filter_dict_keys(desired_values, DESIRED_KEYS_FOR_AUDIT)

        current_non_compliant_configs, desired_configs = Comparator.get_non_compliant_configs(
            current_config=backup_schedule_config, desired_config=filtered_desired_values
        )

        if current_non_compliant_configs or desired_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_non_compliant_configs,
                consts.DESIRED: desired_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
