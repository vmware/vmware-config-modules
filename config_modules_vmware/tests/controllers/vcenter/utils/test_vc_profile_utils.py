# Copyright 2024 Broadcom. All Rights Reserved.
import json

from config_modules_vmware.controllers.vcenter.utils import vc_profile_utils
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext


class TestVcProfileUtils:

    def test_transform_to_drift_schema_non_compliant_array_modified(self):
        task_response = json.loads('''
        {
            "cancelable": false,
            "end_time": "2024-05-14T22:55:26.126Z",
            "description": {
                "args": [],
                "default_message": "Profile compliance check",
                "id": "Profile compliance check"
            },
            "result": {
                "start_time": "2024-05-14T22:55:23.666Z",
                "non_compliant": [
                    "Appliance"
                ],
                "unavailable": [],
                "profile": "NOT_APPLICABLE",
                "end_time": "2024-05-14T22:55:26.126Z",
                "compliance_result": [
                    {
                        "value": {
                            "diff_results": [
                                {
                                    "value": {
                                        "path": "appliance/network/interfaces/0/ipv4/configurable",
                                        "desired_value": false,
                                        "description": "Entity value got updated from the source.",
                                        "category": "network",
                                        "current_value": true
                                    },
                                    "key": "/network/interfaces/0/ipv4/configurable"
                                }
                            ]
                        },
                        "key": "Appliance"
                    }
                ],
                "compliant": [
                    "AuthManagement"
                ],
                "version": "NOT_APPLICABLE",
                "notifications": {},
                "status": "NON_COMPLIANT"
            },
            "start_time": "2024-05-14T22:55:23.631Z",
            "service": "com.vmware.appliance.vcenter.settings.v1.config",
            "progress": {
                "total": 100,
                "completed": 100,
                "message": {
                    "args": [],
                    "default_message": "Compliance check completed successfully",
                    "id": "Profile compliance check"
                }
            },
            "operation": "scan_desired_state",
            "status": "SUCCEEDED"
        }
        ''')
        context = VcenterContext(hostname="hostname")
        task_id = "task_id"
        errors = []
        expected_result = {
            "modifications": [
                {
                    "key": "appliance/network/interfaces/0/ipv4/configurable",
                    "category": "network",
                    "current_value": True,
                    "desired_value": False
                }
            ]
        }
        expected_status = "NON_COMPLIANT"
        drift_response = vc_profile_utils.transform_to_drift_schema(context, task_id, task_response, errors)
        assert drift_response["result"]["result"] == expected_result
        assert drift_response["result"]["status"] == expected_status

    def test_transform_to_drift_schema_non_compliant_array_modified_missing_desired(self):
        task_response = json.loads('''
        {
            "cancelable": false,
            "end_time": "2024-05-14T23:01:26.646Z",
            "description": {
                "args": [],
                "default_message": "Profile compliance check",
                "id": "Profile compliance check"
            },
            "result": {
                "start_time": "2024-05-14T23:01:23.747Z",
                "non_compliant": [
                    "Appliance"
                ],
                "unavailable": [],
                "profile": "NOT_APPLICABLE",
                "end_time": "2024-05-14T23:01:26.646Z",
                "compliance_result": [
                    {
                        "value": {
                            "diff_results": [
                                {
                                    "value": {
                                        "path": "appliance/network/interfaces/0/ipv4",
                                        "description": "Entity value got updated from the source.",
                                        "category": "network",
                                        "current_value": {
                                            "mode": "STATIC",
                                            "default_gateway": "10.0.0.250",
                                            "address": "10.0.0.6",
                                            "prefix": 22,
                                            "configurable": true
                                        }
                                    },
                                    "key": "/network/interfaces/0/ipv4"
                                }
                            ]
                        },
                        "key": "Appliance"
                    }
                ],
                "compliant": [
                    "AuthManagement"
                ],
                "version": "NOT_APPLICABLE",
                "notifications": {},
                "status": "NON_COMPLIANT"
            },
            "start_time": "2024-05-14T23:01:23.713Z",
            "service": "com.vmware.appliance.vcenter.settings.v1.config",
            "progress": {
                "total": 100,
                "completed": 100,
                "message": {
                    "args": [],
                    "default_message": "Compliance check completed successfully",
                    "id": "Profile compliance check"
                }
            },
            "operation": "scan_desired_state",
            "status": "SUCCEEDED"
        }
        ''')
        context = VcenterContext(hostname="hostname")
        task_id = "task_id"
        errors = []
        expected_result = {
            "modifications": [
                {
                    "key": "appliance/network/interfaces/0/ipv4",
                    "category": "network",
                    "current_value": {
                        "mode": "STATIC",
                        "default_gateway": "10.0.0.250",
                        "address": "10.0.0.6",
                        "prefix": 22,
                        "configurable": True
                    },
                    "desired_value": ""
                }
            ]
        }
        expected_status = "NON_COMPLIANT"
        drift_response = vc_profile_utils.transform_to_drift_schema(context, task_id, task_response, errors)
        assert drift_response["result"]["result"] == expected_result
        assert drift_response["result"]["status"] == expected_status

    def test_transform_to_drift_schema_non_compliant_array_modified_missing_current(self):
        task_response = json.loads('''
        {
            "cancelable": false,
            "end_time": "2024-05-14T23:05:34.121Z",
            "description": {
                "args": [],
                "default_message": "Profile compliance check",
                "id": "Profile compliance check"
            },
            "result": {
                "start_time": "2024-05-14T23:05:31.079Z",
                "non_compliant": [
                    "Appliance"
                ],
                "unavailable": [],
                "profile": "NOT_APPLICABLE",
                "end_time": "2024-05-14T23:05:34.121Z",
                "compliance_result": [
                    {
                        "value": {
                            "diff_results": [
                                {
                                    "value": {
                                        "path": "appliance/network/interfaces/0/ipv6",
                                        "desired_value": {
                                            "default_gateway": "",
                                            "addresses": [],
                                            "autoconf": true,
                                            "dhcp": true,
                                            "configurable": true
                                        },
                                        "description": "Entity value got updated from the source.",
                                        "category": "network"
                                    },
                                    "key": "/network/interfaces/0/ipv6"
                                }
                            ]
                        },
                        "key": "Appliance"
                    }
                ],
                "compliant": [
                    "AuthManagement"
                ],
                "version": "NOT_APPLICABLE",
                "notifications": {},
                "status": "NON_COMPLIANT"
            },
            "start_time": "2024-05-14T23:05:31.044Z",
            "service": "com.vmware.appliance.vcenter.settings.v1.config",
            "progress": {
                "total": 100,
                "completed": 100,
                "message": {
                    "args": [],
                    "default_message": "Compliance check completed successfully",
                    "id": "Profile compliance check"
                }
            },
            "operation": "scan_desired_state",
            "status": "SUCCEEDED"
        }
        ''')
        context = VcenterContext(hostname="hostname")
        task_id = "task_id"
        errors = []
        expected_result = {
            "modifications": [
                {
                    "key": "appliance/network/interfaces/0/ipv6",
                    "category": "network",
                    "current_value": "",
                    "desired_value": {
                        "default_gateway": "",
                        "addresses": [],
                        "autoconf": True,
                        "dhcp": True,
                        "configurable": True
                    }
                }
            ]
        }
        expected_status = "NON_COMPLIANT"
        drift_response = vc_profile_utils.transform_to_drift_schema(context, task_id, task_response, errors)
        assert drift_response["result"]["result"] == expected_result
        assert drift_response["result"]["status"] == expected_status
