# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import uuid
from typing import Dict
from typing import List
from typing import Union

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Error
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ErrorSource
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Message
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

source_type_config_module = "ConfigModule"


def create_error(
    type: str,  # pylint: disable=W0622
    error_msg: str,
    server: str = None,
    endpoint: str = None,
    remediation_msg: str = None,
) -> Error:  # pylint: disable=W0622
    """
    Create Error spec
    :param type: source type. ConfigModule, vcenter, etc
    :param error_msg: Error Message
    :param remediation_msg: Remediation message
    :param server: hostname of source.
    :param endpoint: error endpoint if error is due to API call failure
    :return: Error object
    :rtype: Error
    """
    source = ErrorSource(type)
    if server:
        source.server = server
    if endpoint:
        source.endpoint = endpoint
    error = Error(timestamp=utils.get_current_time(), source=source, error=Message(message=error_msg))
    if remediation_msg:
        error.remediation = Message(message=remediation_msg)
    return error


def parse_unavailable_failed_status(
    context: VcenterContext,
    task_id: str,
    task_response: Dict,
    errors: List[Error],
    controller_name: str,
    remediation_msg: str = None,
):
    """
    Parse the compliance change errors when task status is unavailable or failed.

    :param context: Product context
    :type context: vCenterContext
    :param task_id: valid cis task id
    :type task_id: str
    :param task_response: task response obj for given task id
    :type task_response: Dict
    :param errors: list of errors to be transformed
    :type: List[Error]
    :param controller_name: Name of controller responsible for compliance check
    :type controller_name: str
    :param remediation_msg: Remediation message
    :type remediation_msg: str
    """
    result_status = (
        task_response["result"]["status"]
        if "status" in task_response["result"]
        else task_response["result"]["cluster_status"]
    )
    if "notifications" in task_response["result"] or "notifications" in task_response:
        if "notifications" in task_response["result"]:
            notifications = task_response["result"]["notifications"]
        else:
            notifications = task_response["notifications"]
        if "errors" in notifications:
            for error in notifications["errors"]:
                error_message = f"unknown result status[{result_status}] for task[{task_id}] in 'check_compliance' {controller_name}"
                if "message" in error and "default_message" in error["message"]:
                    error_message = error["message"]["default_message"]
                errors.append(
                    create_error(
                        BaseContext.ProductEnum.VCENTER,
                        error_message,
                        context.hostname,
                        context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                        remediation_msg,
                    )
                )
        else:
            logger.error(
                f"missing errors for result status[{result_status}] for task[{task_id}] in 'check_compliance"
                f"' {controller_name}"
            )
            errors.append(
                create_error(
                    source_type_config_module, f"missing errors for result status[{result_status}] for task {task_id}"
                )
            )
    else:
        logger.error(
            f"missing notifications for result status[{result_status}] for task[{task_id}] in 'check_compliance' {controller_name}"
        )
        errors.append(create_error(source_type_config_module, f"Unknown status[{result_status}] for task {task_id}"))


def uuid_from_task_id(task_id: str) -> Union[uuid.UUID, None]:
    """
    Get UUID from cis task id if valid, else return None
    i.e. 52aa6087-33ae-3953-7826-826cd5fa56bf:com.vmware.esx.settings.clusters.configuration
    -> UUID(52aa6087-33ae-3953-7826-826cd5fa56bf)

    :param task_id: cis task id
    :type task_id: str
    :return: Task id as uuid
    :rtype: uuid.UUID | None
    """
    try:
        task_uuid = task_id.split(":")[0]
        return uuid.UUID(task_uuid)
    except Exception as e:
        logger.error(f"Could not retrieve task uuid from task {task_id}: {str(e)}")
        return None
