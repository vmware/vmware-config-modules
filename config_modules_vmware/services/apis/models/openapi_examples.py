# Copyright 2024 Broadcom. All Rights Reserved.

get_config_vc_request_payload_without_template_example = {
    "summary": "Without template",
    "description": "This is to retrieve all vcenter configuration without any filtering.",
    "value": {
        "target": {
            "hostname": "vcenter-1.vsphere.local",
            "auth": [
                {
                    "username": "sso_username",
                    "password": "sso_password",
                    "type": "SSO",
                    "ssl_thumbprint": "AA:BB:CC:DD...",
                }
            ],
        }
    },
}
get_config_vc_request_payload_with_template_example = {
    "summary": "With template",
    "description": "This is to retrieve only vcenter configuration based on the template.",
    "value": {
        "target": {
            "hostname": "vcenter-1.vsphere.local",
            "auth": [
                {
                    "username": "sso_username",
                    "password": "sso_password",
                    "type": "SSO",
                    "ssl_thumbprint": "AA:BB:CC:DD...",
                }
            ],
        },
        "template": {
            "authmgmt": {"global_permissions": []},
            "appliance": {"access_settings": {"shell": {"enabled": ""}}},
        },
    },
}
get_config_vc_request_payload_invalid_example = {
    "summary": "Missing required parameters",
    "description": "Same request body with missing hostname.",
    "value": {
        "target": {
            "auth": [
                {
                    "username": "sso_username",
                    "password": "sso_password",
                    "type": "SSO",
                    "ssl_thumbprint": "AA:BB:CC:DD...",
                }
            ]
        }
    },
}
scan_drift_vc_request_payload_example = {
    "summary": "default",
    "description": "Sample request body",
    "value": {
        "target": {
            "hostname": "vcenter-1.vsphere.local",
            "auth": [
                {
                    "username": "sso_username",
                    "password": "sso_password",
                    "type": "SSO",
                    "ssl_thumbprint": "AA:BB:CC:DD...",
                }
            ],
        },
        "input_spec": {
            "appliance": {
                "user_account_settings": {"local_accounts_policy": {"warn_days": 7, "max_days": 120, "min_days": 1}},
                "syslog": [{"hostname": "8.8.4.0", "protocol": "TLS", "port": 90}],
                "network": {
                    "dns_server_configuration": {
                        "mode": "IS_STATIC",
                        "servers": ["10.0.0.250", "8.8.8.8"],
                        "domains": ["."],
                    }
                },
            }
        },
    },
}
scan_drift_vc_200_response_example = {
    "description": "Successful drift workflow response.",
    "content": {
        "application/json": {
            "example": {
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
    },
}
scan_drift_vc_500_response_example = {
    "description": "Internal error response.",
    "content": {
        "application/json": {
            "example": {
                "schema_version": "1.0-DRAFT",
                "id": "2bcaa939-e6c2-4347-808f-ad90debc20ae",
                "name": "config_modules_vmware.controllers.vcenter.vc_profile",
                "timestamp": "2024-03-28T23:03:19.472Z",
                "description": "Compliance check failed",
                "status": "FAILED",
                "errors": [
                    {
                        "timestamp": "2024-03-07T12:50:39.092Z",
                        "source": {
                            "server": "vcenter1.mydomain.com",
                            "type": "vcenter",
                            "endpoint": "https://vcenter1.mydomain.com/apis/vsphere-automation/latest/appliance/api/appliance/vcenter/settings/v1/configactionscan-desired-statevmw-tasktrue/post/",
                        },
                        "error": {"id": "", "localizable_message": "", "message": "Server Internal Error"},
                        "remediation": {
                            "id": "",
                            "localizable_message": "",
                            "message": "Please fix the input spec appliance system entry [0] and retry",
                        },
                    }
                ],
                "target": {"type": "vcenter", "hostname": "10.0.0.6"},
            }
        }
    },
}
