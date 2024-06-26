# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
from typing import List

from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ConfigAddition
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ConfigDeletion
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ConfigModification
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ConfigurationDriftResponse
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Error
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ErrorSource
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Message
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Result
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Status
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Target
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))
source_type_config_module = "ConfigModule"
REMEDIATION_RETRY_MESSAGE = "Check input spec and retry the operation"
REMEDIATION_COMPONENT_UNAVAILABLE = "Check component on vcenter"


def _parse_unavailable_status(context, task_id, task_response, errors):
    result_status = task_response["result"]["status"]
    if "notifications" in task_response["result"]:
        notifications = task_response["result"]["notifications"]
        if "errors" in notifications:
            for error in notifications["errors"]:
                error_message = (
                    f"unknown result status[{result_status}] for task[{task_id}] in 'check_compliance' vc_profile"
                )
                if "message" in error and "default_message" in error["message"]:
                    error_message = error["message"]["default_message"]
                errors.append(
                    create_error(
                        context.product_category,
                        error_message,
                        context.hostname,
                        context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                        REMEDIATION_COMPONENT_UNAVAILABLE,
                    )
                )
        else:
            logger.error(
                f"missing errors for result status[{result_status}] for task[{task_id}] in 'check_compliance"
                f"' vc_profile"
            )
            errors.append(
                create_error(
                    source_type_config_module, f"missing errors for result status[{result_status}] for task {task_id}"
                )
            )
    else:
        logger.error(
            f"missing notifications for result status[{result_status}] for task[{task_id}] in 'check_compliance' vc_profile"
        )
        errors.append(create_error(source_type_config_module, f"Unknown status[{result_status}] for task {task_id}"))


def transform_to_drift_schema(context: VcenterContext, task_id: str, task_response: Dict, errors: List[Error]) -> Dict:
    """
    Transform task output to drift spec format.

    Drift Spec:
        {
          "schema_version": "1.0-DRAFT",
          "id": "c87f790a-9873-451d-adaa-55158f6a6093",
          "name": "config.modules.vc.profile.drift",
          "target": {
            "hostname": "vcenter1.mydomain.com",
            "type": "vcenter"
          },
          "timestamp": "2024-03-07T12:50:39.092Z",
          "description": "Sample VC Profile Drift Results",
          "status": "NON_COMPLIANT",
          "results": {
            "additions": [
              {
                "key": "appliance/syslog/0",
                "category": "syslog",
                "value": {
                  "hostname": "vndcdfxdvliwnd01.ual.com",
                  "protocol": "UDP",
                  "port": 514
                }
              }
            ],
            "deletions": [
              {
                "key": "appliance/network/dns_server_configuration/servers/0",
                "value": {
                  "address": "10.166.1.1",
                  "mode": "DHCP"
                }
              }
            ],
            "modifications": [
              {
                "key": "appliance/network/interfaces/0/ipv4/address",
                "current_value": "10.78.183.209",
                "desired_value": "10.168.189.35"
              }
            ]
          }
        }
    :param context: vCenterContext
    :param task_id: valid cis task id
    :param task_response: task response obj for given task id
    :param errors: list of errors to be transformed
    :return: Task response or errors transformed into drift spec schema format.
    :rtype: Dict
    """
    config_drift_response = ConfigurationDriftResponse(
        name="config_modules_vmware.controllers.vcenter.vc_profile",
        target=Target(context.product_category, context.hostname),
        description=f"{context.product_category} compliance check",
        timestamp=utils.get_current_time(),
    )
    output = {consts.RESULT: config_drift_response.to_dict()}
    if not errors:
        if "status" in task_response and "progress" in task_response and "result" in task_response:
            if task_response["status"] == vc_consts.CIS_TASK_SUCCEEDED:
                result_status = task_response["result"]["status"]
                config_drift_response.description = task_response["progress"]["message"]["default_message"]
                if result_status.upper() == "COMPLIANT":
                    config_drift_response.status = Status.COMPLIANT
                    output = {
                        consts.STATUS: ComplianceStatus.COMPLIANT,
                        consts.RESULT: config_drift_response.to_dict(),
                    }
                elif result_status.upper() == "NON_COMPLIANT":
                    task_result = task_response["result"]
                    compliance_results = task_result["compliance_result"]
                    added_configs = []
                    deleted_configs = []
                    modified_configs = []
                    for compliance_result in compliance_results:
                        diffs = compliance_result["value"]["diff_results"]
                        for diff in diffs:
                            diff_value = diff["value"]
                            if "Added" in diff_value["description"]:
                                # Add Config
                                added_configs.append(
                                    ConfigAddition(
                                        diff_value["path"], diff_value["category"], diff_value["desired_value"]
                                    )
                                )
                            elif "Removed" in diff_value["description"]:
                                # Removed Config
                                deleted_configs.append(
                                    ConfigDeletion(
                                        diff_value["path"], diff_value["category"], diff_value["current_value"]
                                    )
                                )
                            else:
                                # Modified config
                                modified_config = ConfigModification(diff_value["path"], diff_value["category"])
                                modified_config.current_value = (
                                    diff_value["current_value"] if "current_value" in diff_value else ""
                                )
                                modified_config.desired_value = (
                                    diff_value["desired_value"] if "desired_value" in diff_value else ""
                                )
                                modified_configs.append(modified_config)

                    config_drift_response.status = Status.NON_COMPLIANT
                    config_drift_response.result = Result(added_configs, deleted_configs, modified_configs)
                    output = {
                        consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                        consts.RESULT: config_drift_response.to_dict(),
                    }
                elif result_status.upper() == "UNAVAILABLE":
                    # This happens if the service on VC is down
                    _parse_unavailable_status(context, task_id, task_response, errors)
                else:
                    logger.error(
                        f"unknown result status[{result_status}] for task[{task_id}] in 'check_compliance' vc_profile"
                    )
                    errors.append(
                        create_error(source_type_config_module, f"Unknown status[{result_status}] for task {task_id}")
                    )
            else:
                # Task status = FAILED
                errors.append(
                    create_error(
                        context.product_category,
                        task_response["error"],
                        context.hostname,
                        context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                        REMEDIATION_RETRY_MESSAGE,
                    )
                )
        else:
            # task response not in expected format or missing required fields.
            errors.append(
                create_error(
                    context.product_category,
                    f"malformed task response {task_response}",
                    context.hostname,
                    context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                )
            )

    if errors:
        config_drift_response.status = Status.FAILED
        config_drift_response.errors = errors
        output = {consts.STATUS: ComplianceStatus.FAILED, consts.MESSAGE: config_drift_response.to_dict()}
    return output


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
