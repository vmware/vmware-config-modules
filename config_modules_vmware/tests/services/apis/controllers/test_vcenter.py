# Copyright 2024 Broadcom. All Rights Reserved.
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from mock import patch
from starlette import status
from starlette.testclient import TestClient

from config_modules_vmware.app import app
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Status
from config_modules_vmware.services.apis.controllers.consts import VC_GET_CONFIGURATION_V1
from config_modules_vmware.services.apis.controllers.consts import VC_SCAN_DRIFTS_V1
from config_modules_vmware.services.apis.models.get_config_payload import GetConfigResponsePayload
from config_modules_vmware.services.apis.models.get_config_payload import GetConfigStatus
from config_modules_vmware.services.apis.models.target_model import Target


class TestVcenterController:

    def setup_method(self):
        self.client = TestClient(app)

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.get_current_configuration')
    @patch('config_modules_vmware.framework.utils.utils.get_current_time')
    def test_get_configuration_api(self, get_current_time, controller_interface):
        desired_state = {"status": "SUCCESS", "result": {"desired_state": "sample"}}
        target_hostname = "some_host"
        current_timestamp = datetime.utcnow().strftime(consts.DEFAULT_TIMESTAMP_FORMAT)
        get_current_time.return_value = current_timestamp
        controller_interface.return_value = desired_state
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": target_hostname,
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.content is not None
        response_json = response.json()
        assert response_json[consts.STATUS] == desired_state["status"]
        assert response_json[consts.RESULT] == desired_state["result"]
        assert response_json == jsonable_encoder(
            GetConfigResponsePayload(status=desired_state.get("status"),
                                     result=desired_state.get("result"),
                                     target=Target(hostname=target_hostname, type=BaseContext.ProductEnum.VCENTER),
                                     timestamp=current_timestamp), exclude_none=True)

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.get_current_configuration')
    def test_get_configuration_partial_response(self, controller_interface):
        desired_state = {"status": "PARTIAL", "message": "Exception running controls",
                         "result": {"desired_state": "sample"}}
        controller_interface.return_value = desired_state
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.content is not None
        assert response.json()[consts.STATUS] == GetConfigStatus.PARTIAL.value
        assert response.json()[consts.RESULT] == desired_state["result"]
        assert desired_state.get("message") in response.json()[consts.ERRORS][0]["error"]["message"]

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.get_current_configuration')
    def test_get_configuration_failed_response(self, controller_interface):
        desired_state = {"status": "FAILED", "message": "All controls failed",
                         "result": {"desired_state": "sample"}}
        controller_interface.return_value = desired_state
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()[consts.STATUS] == GetConfigStatus.FAILED.value
        assert response.json()[consts.RESULT] == desired_state["result"]
        assert desired_state.get("message") in response.json()[consts.ERRORS][0]["error"]["message"]

    def test_get_configuration_api_using_get(self):
        response = self.client.get(VC_GET_CONFIGURATION_V1)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_get_configuration_api_missing_body(self):
        response = self.client.post(VC_GET_CONFIGURATION_V1)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_configuration_api_missing_required_property(self):
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_configuration_api_missing_auth(self):
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.get_current_configuration')
    def test_get_configuration_none_response(self, controller_interface):
        # test empty return from product interface
        controller_interface.return_value = None
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()[consts.STATUS] == GetConfigStatus.FAILED.value

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.get_current_configuration')
    def test_get_configuration_missing_status(self, controller_interface):
        # test empty return from product interface
        controller_interface.return_value = {"result": {"desired_state": "sample"}}
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()[consts.STATUS] == GetConfigStatus.FAILED.value
        assert "Missing status in configuration response." in response.json()[consts.ERRORS][0]["error"]["message"]

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.get_current_configuration')
    def test_get_configuration_error_response(self, controller_interface):
        # test errors while invoking product interface
        desired_state = {"status": "ERROR", "message": {"desired_state": "sample"}}
        controller_interface.return_value = desired_state
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()[consts.STATUS] == GetConfigStatus.FAILED.value

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.get_current_configuration')
    def test_get_configuration_exception(self, controller_interface):
        # test exception while invoking product interface
        controller_interface.side_effect = Exception("exception")
        response = self.client.post(VC_GET_CONFIGURATION_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password",
                        "type": "SSO",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()['status'] == GetConfigStatus.FAILED.value

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance')
    def test_scan_drifts_api(self, controller_interface):
        drift_response_mock = {
            "status": "NON_COMPLIANT",
            "changes": {
                "schema_version": "1.0-DRAFT",
                "id": "2bcaa939-e6c2-4347-808f-ad90debc20ae",
                "name": "config_modules_vmware.controllers.vcenter.vc_profile",
                "timestamp": "2024-03-28T23:03:19.472Z",
                "description": "Compliance check completed successfully",
                "status": "NON_COMPLIANT",
                "result": {
                    "additions": [
                        {
                            "key": "appliance/network/dns_server_configuration/servers/1",
                            "category": "network",
                            "value": "8.8.8.8",
                        }
                    ],
                    "modifications": [
                        {
                            "key": "appliance/user_account_settings/local_accounts_policy/max_days",
                            "category": "user_account_settings",
                            "current_value": 90,
                            "desired_value": 120,
                        }
                    ],
                    "deletions": [
                        {
                            "key": "appliance/syslog/1",
                            "category": "syslog",
                            "value": {"hostname": "8.8.1.1", "protocol": "TLS", "port": 90},
                        }
                    ],
                },
                "target": {"type": "vcenter", "hostname": "10.0.0.6"},
            }
        }
        controller_interface.return_value = drift_response_mock
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.content is not None
        assert response.json() == drift_response_mock.get(consts.CHANGES)

    def test_scan_drifts_api_using_get(self):
        response = self.client.get(VC_SCAN_DRIFTS_V1)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_scan_drifts_api_missing_required_property(self):
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            }
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_scan_drifts_api_missing_body(self):
        response = self.client.post(VC_SCAN_DRIFTS_V1)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_scan_drifts_api_missing_auth(self):
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {}
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            }
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance')
    def test_scan_drifts_none_response(self, controller_interface):
        # test empty return from product interface
        controller_interface.return_value = None
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()['status'] == Status.FAILED

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance')
    def test_scan_drifts_missing_status_response(self, controller_interface):
        # test missing status in response from product interface
        controller_interface.return_value = {
            "changes": {
                "schema_version": "1.0-DRAFT",
                "id": "2bcaa939-e6c2-4347-808f-ad90debc20ae",
                "name": "config_modules_vmware.controllers.vcenter.vc_profile",
                "timestamp": "2024-03-28T23:03:19.472Z",
                "description": "Compliance check completed successfully"
            }
        }
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()[consts.STATUS] == Status.FAILED

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance')
    def test_scan_drifts_invalid_fields(self, controller_interface):
        # test invalid fields in product interface drift response
        controller_interface.return_value = {
            "status": "FAILED",
            "changes": {
                "schema_version": "1.0-DRAFT",
                "id": "2bcaa939-e6c2-4347-808f-ad90debc20ae",
                "name": "config_modules_vmware.controllers.vcenter.vc_profile",
                "timestamp": "2024-03-28T23:03:19.472Z",
                "description": "Compliance check completed successfully",
                "status": "FAILED",
                "result": {
                    "additions": [
                        {
                            "key": "appliance/network/dns_server_configuration/servers/1",
                            "category": "network",
                            "value": "8.8.8.8",
                        }
                    ],
                    "modifications": [
                        {
                            "key": "appliance/user_account_settings/local_accounts_policy/max_days",
                            "category": "user_account_settings",
                            "current_value": 90,
                            "desired_value": 120,
                        }
                    ],
                    "deletions": [
                        {
                            "key": "appliance/syslog/1",
                            "category": "syslog",
                            "value": {"hostname": "8.8.1.1", "protocol": "TLS", "port": 90},
                        }
                    ],
                },
                "invalid-target": {"type": "vcenter", "hostname": "10.0.0.6"},
            }
        }
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()['status'] == Status.FAILED

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance')
    def test_scan_drifts_failed_response(self, controller_interface):
        # test invalid fields in product interface drift response
        controller_interface.return_value = {
            "status": "FAILED",
            "message": {
                "schema_version": "1.0-DRAFT",
                "id": "2bcaa939-e6c2-4347-808f-ad90debc20ae",
                "name": "config_modules_vmware.controllers.vcenter.vc_profile",
                "timestamp": "2024-03-28T23:03:19.472Z",
                "description": "Compliance check completed successfully",
                "status": "FAILED",
                "target": {"type": "vcenter", "hostname": "10.0.0.6"},
            }
        }
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()[consts.STATUS] == Status.FAILED

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance')
    def test_scan_drifts_error_response(self, controller_interface):
        # test errors while invoking product interface
        drift_response_mock = {
            "status": "ERROR",
            "message": "Exception in workflow"
        }
        controller_interface.return_value = drift_response_mock
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert drift_response_mock.get("message") in response.json()[consts.ERRORS][0]["error"]["message"]

    @patch('config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance')
    def test_scan_drifts_exception(self, controller_interface):
        # test exception while invoking product interface
        controller_interface.side_effect = Exception("exception")
        response = self.client.post(VC_SCAN_DRIFTS_V1, json={
            "target": {
                "hostname": "some_host",
                "auth": [
                    {
                        "username": "sso_username",
                        "password": "sso_password!",
                        "type": "SSO",
                        "ssl_thumbprint": "AA:BB:CC:DD...",
                    }
                ],
            },
            "input_spec": {
                "authmgmt": {
                    "global_permissions": [
                        {
                            "principal": {"name": "VSPHERE.LOCAL\\TrustedAdmins", "group": True},
                            "role_names": ["TrustedAdmin"],
                            "propagate": True,
                            "role_ids": [-7],
                        }
                    ]
                }
            },
        })
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.content is not None
        assert response.json()['status'] == Status.FAILED
