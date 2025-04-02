# Copyright 2024 Broadcom. All Rights Reserved.
import json

from mock import MagicMock

from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.models.utils import drift_utils


def test_create_error():
    type = "type"
    error_msg = "error_msg"
    server = "server"
    endpoint = "endpoint"
    remediation_msg = "remediation_msg"
    error = drift_utils.create_error(type, error_msg, server, endpoint, remediation_msg)
    error_dict = error.to_dict()
    assert error_dict["source"]["type"] == type
    assert error_dict["source"]["server"] == server
    assert error_dict["source"]["endpoint"] == endpoint
    assert error_dict["error"]["message"] == error_msg
    assert error_dict["remediation"]["message"] == remediation_msg

def test_parse_unavailable_failed_status():
    task_response = json.loads('''
    {
        "cancelable": false,
        "end_time": "2024-08-14T17:52:51.364Z",
        "description": {
            "args": [],
            "default_message": "Desired state compliance check",
            "id": "Desired state compliance check"
        },
        "result": {
            "notifications": {
                "warnings": [],
                "errors": [
                    {
                        "id": "service.complianceFailure",
                        "message": {
                            "args": [],
                            "default_message": "Internal error during service precheck execution",
                            "id": "service.complianceFailure"
                        }
                    }
                ],
                "info": []
            },
            "status": "FAILED"
        },
        "start_time": "2024-08-14T17:52:46.376Z",
        "service": "com.vmware.domain.v1.configuration",
        "progress": {
            "total": 100,
            "completed": 100,
            "message": {
                "args": [],
                "default_message": "Compliance check completed successfully",
                "id": "Profile compliance check"
            }
        },
        "operation": "check_compliance",
        "status": "SUCCEEDED"
    }
    ''')
    context = VcenterContext(hostname="hostname")
    context.vc_rest_client = MagicMock()
    context.vc_rest_client.get_base_url.return_value = "mock-vc.eng.vmware.com"
    task_id = "task_id"
    errors = []
    drift_utils.parse_unavailable_failed_status(context, task_id, task_response, errors, "controller_name", "remediation_msg")
    assert len(errors) == 1
    assert errors[0].to_dict()["error"]["message"] == "Internal error during service precheck execution"

def test_parse_unavailable_failed_status_missing_errors():
    task_response = json.loads('''
    {
        "cancelable": false,
        "end_time": "2024-08-14T17:52:51.364Z",
        "description": {
            "args": [],
            "default_message": "Desired state compliance check",
            "id": "Desired state compliance check"
        },
        "result": {
            "notifications": {
                "warnings": [],
                "info": []
            },
            "status": "FAILED"
        },
        "start_time": "2024-08-14T17:52:46.376Z",
        "service": "com.vmware.domain.v1.configuration",
        "progress": {
            "total": 100,
            "completed": 100,
            "message": {
                "args": [],
                "default_message": "Compliance check completed successfully",
                "id": "Profile compliance check"
            }
        },
        "operation": "check_compliance",
        "status": "SUCCEEDED"
    }
    ''')
    context = VcenterContext(hostname="hostname")
    context.vc_rest_client = MagicMock()
    context.vc_rest_client.get_base_url.return_value = "mock-vc.eng.vmware.com"
    task_id = "task_id"
    errors = []
    drift_utils.parse_unavailable_failed_status(context, task_id, task_response, errors, "controller_name", "remediation_msg")
    assert len(errors) == 1
    assert errors[0].to_dict()["error"]["message"] == f"missing errors for result status[FAILED] for task {task_id}"

def test_parse_unavailable_failed_status_missing_notifications():
    task_response = json.loads('''
    {
        "cancelable": false,
        "end_time": "2024-08-14T17:52:51.364Z",
        "description": {
            "args": [],
            "default_message": "Desired state compliance check",
            "id": "Desired state compliance check"
        },
        "result": {
            "status": "FAILED"
        },
        "start_time": "2024-08-14T17:52:46.376Z",
        "service": "com.vmware.domain.v1.configuration",
        "progress": {
            "total": 100,
            "completed": 100,
            "message": {
                "args": [],
                "default_message": "Compliance check completed successfully",
                "id": "Profile compliance check"
            }
        },
        "operation": "check_compliance",
        "status": "SUCCEEDED"
    }
    ''')
    context = VcenterContext(hostname="hostname")
    context.vc_rest_client = MagicMock()
    context.vc_rest_client.get_base_url.return_value = "mock-vc.eng.vmware.com"
    task_id = "task_id"
    errors = []
    drift_utils.parse_unavailable_failed_status(context, task_id, task_response, errors, "controller_name", "remediation_msg")
    assert len(errors) == 1
    assert errors[0].to_dict()["error"]["message"] == f"Unknown status[FAILED] for task {task_id}"

def test_uuid_from_task_id():
    uuid_string = "52d0be83-9e2e-7a4e-9e04-d1469959c159"
    task_uuid = drift_utils.uuid_from_task_id(f"{uuid_string}:com.vmware.esx.settings.clusters.configuration")
    assert str(task_uuid) == uuid_string

def test_uuid_from_task_id_invalid():
    task_uuid = drift_utils.uuid_from_task_id("invalid")
    assert task_uuid is None
