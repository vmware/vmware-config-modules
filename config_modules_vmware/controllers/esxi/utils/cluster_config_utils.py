# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
from typing import List

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import EsxiContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ConfigurationDriftResponse
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Error
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Status
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Target
from config_modules_vmware.framework.models.utils import drift_utils
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))


def transform_to_drift_schema(
    context: EsxiContext, cluster_moid: str, task_id: str, task_response: Dict, errors: List[Error]
) -> Dict:
    """
    Transform task output to drift spec format.

    Drift Spec:
        {
          "schema_version": "1.0",
          "id": "c87f790a-9873-451d-adaa-55158f6a6093",
          "name": "config_modules_vmware.controllers.esxi.cluster_config",
          "timestamp": "2024-03-07T12:50:39.092Z",
          "description": "ESXi cluster compliance check",
          "status": "NON_COMPLIANT",
          "target": {
            "id": "domain-c9",
            "hostname": "vcenter1.mydomain.com",
            "type": "vcenter"
          }
        }
    :param context: EsxiContext
    :param cluster_moid: Cluster moid
    :param task_id: valid cis task id
    :param task_response: task response obj for given task id
    :param errors: list of errors to be transformed
    :return: Task response or errors transformed into drift spec schema format.
    :rtype: Dict
    """
    config_drift_response = ConfigurationDriftResponse(
        id=drift_utils.uuid_from_task_id(task_id),
        name="config_modules_vmware.controllers.esxi.cluster_config",
        target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=context.hostname, id=cluster_moid),
        description="ESXi cluster compliance check",
        timestamp=utils.get_current_time(),
    )
    output = {consts.RESULT: config_drift_response.to_dict()}
    if not errors:
        if "status" in task_response and "result" in task_response:
            if task_response["status"] == vc_consts.CIS_TASK_SUCCEEDED:
                result_status = task_response["result"]["cluster_status"]
                config_drift_response.description = task_response["result"]["summary"]["default_message"]
                config_drift_response.timestamp = task_response["result"]["end_time"]
                if result_status.upper() == "COMPLIANT":
                    config_drift_response.status = Status.COMPLIANT
                    output = {
                        consts.STATUS: ComplianceStatus.COMPLIANT,
                        consts.RESULT: config_drift_response.to_dict(),
                    }
                elif result_status.upper() == "NOT_COMPLIANT":
                    config_drift_response.status = Status.NON_COMPLIANT
                    output = {
                        consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                        consts.RESULT: config_drift_response.to_dict(),
                    }
                elif result_status.upper() == "UNAVAILABLE" or result_status.upper() == "FAILED":
                    # This happens if the service on VC is down
                    drift_utils.parse_unavailable_failed_status(
                        context, task_id, task_response, errors, "cluster_config"
                    )
                else:
                    logger.error(
                        f"unknown result status[{result_status}] for task[{task_id}] in 'check_compliance' cluster_config"
                    )
                    errors.append(
                        drift_utils.create_error(
                            drift_utils.source_type_config_module, f"Unknown status[{result_status}] for task {task_id}"
                        )
                    )
            else:
                # Task status = FAILED
                if "error" in task_response:
                    if "messages" in task_response["error"]:
                        for message in task_response["error"]["messages"]:
                            errors.append(
                                drift_utils.create_error(
                                    BaseContext.ProductEnum.VCENTER,
                                    message["default_message"],
                                    context.hostname,
                                    context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                                )
                            )
                    else:
                        errors.append(
                            drift_utils.create_error(
                                BaseContext.ProductEnum.VCENTER,
                                task_response["error"],
                                context.hostname,
                                context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                            )
                        )
                elif "notifications" in task_response["result"]:
                    drift_utils.parse_unavailable_failed_status(
                        context, task_id, task_response, errors, "cluster_config"
                    )
                else:
                    # task response not in expected format or missing required fields.
                    errors.append(
                        drift_utils.create_error(
                            BaseContext.ProductEnum.VCENTER,
                            f"malformed task response {task_response}",
                            context.hostname,
                            context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                        )
                    )
        else:
            # task response not in expected format or missing required fields.
            errors.append(
                drift_utils.create_error(
                    BaseContext.ProductEnum.VCENTER,
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
