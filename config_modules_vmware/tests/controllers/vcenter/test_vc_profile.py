# Copyright 2024 Broadcom. All Rights Reserved.
import copy

from mock import patch

from config_modules_vmware.controllers.vcenter.utils.vc_profile_utils import REMEDIATION_COMPONENT_UNAVAILABLE
from config_modules_vmware.controllers.vcenter.vc_profile import VcProfile
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.clients.vcenter.vc_consts import VC_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ErrorSource
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Message
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestVcProfile:

    def setup_method(self):
        self.controller = VcProfile()

        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = VC_API_BASE.format(self.mock_vc_host_name)

        self.vc_profile_current = {
            "appliance": {
                "software_update_policy": {
                    "enable_SSL_cert_validation": False
                },
                "config2": {
                    "key1": False,
                    "key2": "value2"
                }
            }
        }
        self.input_desired_value = {
            "appliance": {
                "software_update_policy": {
                    "enable_SSL_cert_validation": True
                },
                "config2": {}
            }
        }

        self.expected_merged_spec = {
            "appliance": {
                "software_update_policy": {
                    "enable_SSL_cert_validation": True
                }
            }
        }
        self.mock_task_response = {
            "result": {
                "start_time": "2024-03-25T18:16:21.478Z",
                "non_compliant": ["AuthManagement"],
                "end_time": "2024-03-25T18:16:23.414Z",
                "compliance_result": [
                    {
                        "value": {
                            "diff_results": [
                                {
                                    "value": {
                                        "path": "appliance/access_settings/shell/timeout",
                                        "desired_value": 10,
                                        "description": "Entity value got updated from the source.",
                                        "category": "access_settings",
                                        "current_value": 0
                                    },
                                    "key": "/access_settings/shell/timeout"
                                }
                            ]
                        }
                    }
                ],
                "compliant": [],
                "status": "NON_COMPLIANT"
            },
            "status": "SUCCEEDED",
            "progress": {
                "total": 100,
                "completed": 100,
                "message": {
                    "args": [],
                    "default_message": "Compliance check completed successfully",
                    "id": "Profile compliance check"
                }
            }
        }
        self.mock_drift_spec_response = {"modifications": [{"category": "access_settings",
                                                            "current_value": 0,
                                                            "desired_value": 10,
                                                            "key": "appliance/access_settings/shell/timeout"}]}

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success(self, mock_vc_rest_client, mock_vc_context):
        vc_profile = {"foo": "bar"}
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = vc_profile
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        mock_vc_rest_client.get_helper.assert_called_once_with(
            f"{self.vc_base_url}{vc_consts.VC_PROFILE_CURRENT_URL}"
            f"&components=AuthManagement&components=Appliance"
        )
        assert result == vc_profile
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_success_with_template(self, mock_vc_rest_client, mock_vc_context):
        vc_profile = {"foo": "bar"}
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = vc_profile
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        template = {
            'authmgmt': {}
        }

        result, errors = self.controller.get(mock_vc_context, template)

        mock_vc_rest_client.get_helper.assert_called_once_with(
            f"{self.vc_base_url}{vc_consts.VC_PROFILE_CURRENT_URL}"
            f"&components=AuthManagement"
        )
        assert result == template
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = Exception("Exception while getting current VC profile")

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = expected_error
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context)

        mock_vc_rest_client.get_helper.assert_called_once_with(
            f"{self.vc_base_url}{vc_consts.VC_PROFILE_CURRENT_URL}"
            f"&components=AuthManagement&components=Appliance"
        )
        assert result == {}
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_get_failed(self, mock_vc_rest_client, mock_vc_context):
        expected_error = "Unsupported component 'invalid' in template"
        template = {
            'authmgmt': {},
            'invalid': {}
        }

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client

        result, errors = self.controller.get(mock_vc_context, template)

        mock_vc_rest_client.get_helper.assert_not_called()
        assert result == {}
        assert errors == [expected_error]

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    def test_set_skipped(self, mock_vc_context):
        expected_result = RemediateStatus.SKIPPED, [consts.REMEDIATION_SKIPPED_MESSAGE]
        assert self.controller.set(mock_vc_context, {}) == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    def test_remediate_skipped(self, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE]}
        assert self.controller.remediate(mock_vc_context, {}) == expected_result

    def test_populate_template(self):
        current_value = {
            "key1": ["val1.1", "val1.2"],
            "key2": "val2",
            "key3": "val3",
            "key4": [
                {
                    "key4.1": "val4.1",
                    "key4.2": "val4.2"
                },
                {
                    "key4.1": "val4.1",
                    "key4.2": "val4.2"
                }
            ],
            "key5": {},
            "key6": [],
            "key7": ["val7.1"]
        }
        template = {
            "key1": [],
            "key2": "",
            "key3": "populated_value",
            "key4": [
                {
                    "key4.1": "",
                    "key4.3": "string"
                }
            ],
            "key5": {
                "key5.1": "string"
            },
            "key6": ["string"],
            "key7": [
                {
                    "key7.1": "string"
                }
            ],
            "non_existent_primitive": "invalid",
            "non_existent_dict": {
                "non_existent_nested_key": "invalid_value"
            },
            "non_existent_list": [],
            "non_existent_primitive_list": ["string"]
        }
        expected_result = {
            "key1": ["val1.1", "val1.2"],
            "key2": "val2",
            "key3": "val3",
            "key4": [
                {
                    "key4.1": "val4.1"
                },
                {
                    "key4.1": "val4.1"
                }
            ],
            "key5": {},
            "key6": [],
            "key7": ["val7.1"]
        }
        self.controller._populate_template(current_value, template)
        assert template == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_success(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.return_value = self.mock_task_response
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        expected_result = self.mock_drift_spec_response
        result = self.controller.check_compliance(mock_vc_context, self.input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url = f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body = {"desired_state": self.expected_merged_spec}
        )
        assert result["result"]["result"] == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_task_timedout(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.side_effect = Exception("Task[test_task_id] timed out. Timeout duration [1s]")
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        expected_error_msg = "Task[test_task_id] timed out. Timeout duration [1s]"
        result = self.controller.check_compliance(mock_vc_context, self.input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": self.expected_merged_spec}
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_task_status_unknown(self, mock_vc_rest_client, mock_vc_context):
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.side_effect = Exception(
            "Task[test_task_id] returned an invalid status UNKNOWN")
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        expected_error_msg = "Task[test_task_id] returned an invalid status UNKNOWN"
        result = self.controller.check_compliance(mock_vc_context, self.input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": self.expected_merged_spec}
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_task_failed(self, mock_vc_rest_client, mock_vc_context):
        mock_task_response = copy.deepcopy(self.mock_task_response)
        mock_task_response["status"] = "FAILED"
        mock_task_response["error"] = "Test failure"

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        mock_vc_context.hostname = self.mock_vc_host_name
        mock_vc_context.product_category = "vcenter"
        expected_error_msg = "Test failure"
        result = self.controller.check_compliance(mock_vc_context, self.input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": self.expected_merged_spec}
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()
        assert result["message"]["errors"][0]["source"] == ErrorSource(server=self.mock_vc_host_name, type="vcenter", endpoint=self.vc_base_url + vc_consts.CIS_TASKS_URL.format("test_task_id")).to_dict()

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_task_compliant(self, mock_vc_rest_client, mock_vc_context):
        mock_task_response = copy.deepcopy(self.mock_task_response)
        mock_task_response["result"]["status"] = "COMPLIANT"
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT,
                           consts.RESULT: mock_task_response["result"]}
        result = self.controller.check_compliance(mock_vc_context, self.input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": self.expected_merged_spec}
        )
        assert result["result"]["status"] == "COMPLIANT"

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_task_unavailable_status(self, mock_vc_rest_client, mock_vc_context):
        mock_task_response = copy.deepcopy(self.mock_task_response)
        mock_task_response["result"]["status"] = "UNAVAILABLE"
        expected_error_msg = "Component AuthManagement is unavailable"
        mock_notifications = {
            "errors": [
                {
                    "notification": "compliance.compare.unavailable",
                    "message": {
                        "args": [],
                        "default_message": expected_error_msg,
                        "id": "compliance.compare.unavailable"
                    }
                }
            ]
        }
        mock_task_response["result"]["notifications"] = mock_notifications
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        result = self.controller.check_compliance(mock_vc_context, self.input_desired_value)
        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": self.expected_merged_spec}
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()
        assert result["message"]["errors"][0]["remediation"]["message"] == REMEDIATION_COMPONENT_UNAVAILABLE

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_task_unknown_status(self, mock_vc_rest_client, mock_vc_context):
        mock_task_response = copy.deepcopy(self.mock_task_response)
        mock_task_response["result"]["status"] = "TEST"
        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = self.vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        expected_error_msg = "Unknown status[TEST] for task test_task_id"
        result = self.controller.check_compliance(mock_vc_context, self.input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": self.expected_merged_spec}
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_with_list_success(self, mock_vc_rest_client, mock_vc_context):
        vc_profile_current = {
            "appliance": {
                "object1": {
                    "key1": False,
                    "key2": "value2"
                },
                "object2": {
                    "key1": "value1",
                    "object3": {
                        "key1": "value1"
                    }
                },
                "list1": [
                    "10.0.0.1"
                ],
                "list2": [
                    {
                        "key1": "value1",
                        "key2": "value2"
                    }
                ],
                "list3": [
                    {
                        "key1": "value1"
                    }
                ]
            }
        }
        input_desired_value = {
            "appliance": {
                "object1": {
                    "key1": True
                },
                "object2": {
                    "object3": {}
                },
                "list1": [
                    "10.0.0.2"
                ],
                "list2": [
                    {
                        "key3": "value3"
                    }
                ],
                "list3": []
            }
        }


        merged_spec = {
            "appliance": {
                "object1": {
                    "key1": True,
                    "key2": "value2"
                },
                "object2": {
                    "key1": "value1"
                },
                "list1": [
                    "10.0.0.2"
                ],
                "list2": [
                    {
                        "key3": "value3"
                    }
                ],
                "list3": []
            }
        }

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = vc_profile_current
        mock_vc_rest_client.post_helper.return_value = "test_task_id"
        mock_vc_rest_client.wait_for_cis_task_completion.return_value = self.mock_task_response
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        expected_result = self.mock_drift_spec_response
        result = self.controller.check_compliance(mock_vc_context, input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": merged_spec}
        )
        assert result["result"]["result"] == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_failed(self, mock_vc_rest_client, mock_vc_context):
        vc_profile_current = {
            "appliance": {
                "software_update_policy": {
                    "enable_SSL_cert_validation": False
                }
            }
        }
        input_desired_value = {
            "appliance": {
                "software_update_policy": {
                    "enable_SSL_cert_validation": True
                }
            }
        }

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.return_value = vc_profile_current
        mock_vc_rest_client.post_helper.side_effect = Exception("Failed to check compliance")
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        mock_vc_context.hostname = self.mock_vc_host_name
        mock_vc_context.product_category = "vcenter"
        expected_error_msg = "Failed to check compliance"
        result = self.controller.check_compliance(mock_vc_context, input_desired_value)

        mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{vc_consts.DESIRED_STATE_SCAN_URL}",
            body={"desired_state": input_desired_value}
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()
        assert result["message"]["errors"][0]["source"] == ErrorSource(server=self.mock_vc_host_name, type="vcenter",
                                                                      endpoint=self.vc_base_url + vc_consts.DESIRED_STATE_SCAN_URL).to_dict()

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    @patch('config_modules_vmware.framework.clients.vcenter.vc_rest_client.VcRestClient')
    def test_check_compliance_get_failed(self, mock_vc_rest_client, mock_vc_context):
        input_desired_value = {"appliance": {}}

        mock_vc_rest_client.get_base_url.return_value = self.vc_base_url
        mock_vc_rest_client.get_helper.side_effect = Exception("Failed to get config")
        mock_vc_context.vc_rest_client.return_value = mock_vc_rest_client
        expected_error_msg = "Failed to get config"
        result = self.controller.check_compliance(mock_vc_context, input_desired_value)
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()
        assert result["message"]["errors"][0]["source"] == ErrorSource(type="ConfigModule").to_dict()

    @patch('config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext')
    def test_check_compliance_unsupported_component(self, mock_vc_context):
        input_desired_value = {"foo": {}}

        expected_error_msg = "Unsupported component 'foo' in desired values"
        result = self.controller.check_compliance(mock_vc_context, input_desired_value)
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()
        assert result["message"]["errors"][0]["source"] == ErrorSource(type="ConfigModule").to_dict()
