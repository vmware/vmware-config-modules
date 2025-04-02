# Copyright 2024 Broadcom. All Rights Reserved.
import copy

from mock import MagicMock

import config_modules_vmware.controllers.esxi.cluster_config
from config_modules_vmware.controllers.esxi.cluster_config import ClusterConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.clients.vcenter.vc_consts import VC_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.configuration_drift_response import ErrorSource
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Message
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestClusterConfig:

    def setup_method(self):
        self.controller = ClusterConfig()

        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = VC_API_BASE.format(self.mock_vc_host_name)

        self.mock_vc_rest_client = MagicMock()
        self.mock_vc_rest_client.get_base_url.return_value = self.vc_base_url

        self.mock_esxi_context = self.create_context_mock()
        self.mock_esxi_context.vc_rest_client.return_value = self.mock_vc_rest_client
        self.mock_esxi_context.hostname = self.mock_vc_host_name

        self.mock_cluster_moid = "domain-c9"
        self.mock_task_id = "ca65525c-b324-49e1-9e7e-008d08dfecb4"
        self.mock_task_response = {
            "result": {
                "summary": {
                    "args": [],
                    "default_message": "All hosts in this cluster are compliant.",
                    "localized": "All hosts in this cluster are compliant.",
                    "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Summary.Compliant"
                },
                "cluster_status": "COMPLIANT",
                "non_compliant_hosts": [],
                "skipped_hosts": [],
                "commit": "config-commit-2",
                "end_time": "2024-11-08T19:39:57.371Z",
            },
            "status": "SUCCEEDED",
            "progress": {
                "total": 100,
                "completed": 100,
                "message": {
                    "args": [],
                    "default_message": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "localized": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "id": "com.vmware.vcIntegrity.lifecycle.Task.Progress"
                }
            },
        }

        self.mock_drift_spec_response = {
            "schema_version": "1.0",
            "id": "ca65525c-b324-49e1-9e7e-008d08dfecb4",
            "name": "config_modules_vmware.controllers.esxi.cluster_config",
            "timestamp": "2024-11-08T19:39:57.371Z",
            "description": "All hosts in this cluster are compliant.",
            "status": "COMPLIANT",
            "target": {
                "hostname": "mock-vc.eng.vmware.com",
                "type": "vcenter",
                "id": "domain-c9"
            }
        }

    def create_context_mock(self):
        context_mock = MagicMock()
        context_mock.product_category = "esxi"
        return context_mock

    def test_get_skipped(self):
        result, errors = self.controller.get(self.mock_esxi_context)
        assert result == {}
        assert errors == [consts.SKIPPED]

    def test_set_skipped(self):
        expected_result = RemediateStatus.SKIPPED, [consts.REMEDIATION_SKIPPED_MESSAGE]
        assert self.controller.set(self.mock_esxi_context, {}) == expected_result

    def test_remediate_skipped(self):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.REMEDIATION_SKIPPED_MESSAGE]}
        assert self.controller.remediate(self.mock_esxi_context, {}) == expected_result

    def test_check_compliance_success(self):
        self.mock_vc_rest_client.post_helper.return_value = self.mock_task_id
        self.mock_vc_rest_client.wait_for_cis_task_completion.return_value = self.mock_task_response
        result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)

        self.mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
        )
        assert result["result"]== self.mock_drift_spec_response

    def test_check_compliance_task_timedout(self):
        self.mock_vc_rest_client.post_helper.return_value = self.mock_task_id
        self.mock_vc_rest_client.wait_for_cis_task_completion.side_effect = Exception(f"Task[{self.mock_task_id}] timed out. Timeout duration [1s]")
        expected_error_msg = f"Task[{self.mock_task_id}] timed out. Timeout duration [1s]"
        result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)

        self.mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()

    def test_check_compliance_task_status_unknown(self):
        self.mock_vc_rest_client.post_helper.return_value = self.mock_task_id
        self.mock_vc_rest_client.wait_for_cis_task_completion.side_effect = Exception(
            f"Task[{self.mock_task_id}] returned an invalid status UNKNOWN")
        expected_error_msg = f"Task[{self.mock_task_id}] returned an invalid status UNKNOWN"
        result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)

        self.mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()

    def test_check_compliance_task_failed(self):
        mock_task_response = copy.deepcopy(self.mock_task_response)
        mock_task_response["status"] = "FAILED"
        mock_task_response["error"] = {
            "@class": "com.vmware.vapi.std.errors.internal_server_error",
            "error_type": "INTERNAL_SERVER_ERROR",
            "messages": [
                {
                    "args": [
                        "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                        "VALIDATE"
                    ],
                    "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation.",
                    "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation.",
                    "id": "com.vmware.vcIntegrity.lifecycle.plugin.Failed"
                }
            ]
        }

        self.mock_vc_rest_client.post_helper.return_value = self.mock_task_id
        self.mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
        result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)

        self.mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=mock_task_response["error"]["messages"][0]["default_message"]).to_dict()
        assert result["message"]["errors"][0]["source"] == ErrorSource(server=self.mock_vc_host_name, type="vcenter", endpoint=self.vc_base_url + vc_consts.CIS_TASKS_URL.format(self.mock_task_id)).to_dict()

    def test_check_compliance_task_non_compliant(self):
        mock_task_response = copy.deepcopy(self.mock_task_response)
        mock_task_response["result"]["cluster_status"] = "NOT_COMPLIANT"
        self.mock_vc_rest_client.post_helper.return_value = self.mock_task_id
        self.mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
        result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)

        expected_result = copy.deepcopy(self.mock_drift_spec_response)
        expected_result["status"] = "NON_COMPLIANT"
        self.mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
        )
        assert result["result"]== expected_result

    def test_check_compliance_task_unavailable_status(self):
        mock_task_response = copy.deepcopy(self.mock_task_response)
        mock_task_response["result"]["cluster_status"] = "UNAVAILABLE"
        expected_error_msg = "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation."
        mock_notifications = {
            "warnings": [],
            "errors": [
                {
                    "id": "com.vmware.vcIntegrity.lifecycle.plugin.Failed",
                    "time": "2024-11-06T18:41:19.430Z",
                    "message": {
                        "args": [
                            "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                            "VALIDATE"
                        ],
                        "default_message": expected_error_msg,
                        "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation.",
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Failed"
                    },
                    "type": "ERROR"
                }
            ],
            "info": [],
        }
        mock_task_response["notifications"] = mock_notifications
        self.mock_vc_rest_client.post_helper.return_value = self.mock_task_id
        self.mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
        result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)
        self.mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()

    def test_check_compliance_task_unknown_status(self):
       mock_task_response = copy.deepcopy(self.mock_task_response)
       mock_task_response["result"]["cluster_status"] = "TEST"
       self.mock_vc_rest_client.post_helper.return_value = self.mock_task_id
       self.mock_vc_rest_client.wait_for_cis_task_completion.return_value = mock_task_response
       expected_error_msg = f"Unknown status[TEST] for task {self.mock_task_id}"
       result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)

       self.mock_vc_rest_client.post_helper.assert_called_once_with(
           url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
       )
       assert result["status"] == ComplianceStatus.FAILED
       assert len(result["message"]["errors"]) == 1
       assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()

    def test_check_compliance_failed_8_0_3(self):
        self.mock_vc_rest_client.post_helper.side_effect = Exception("Failed to check compliance")
        expected_error_msg = "Failed to check compliance"
        result = self.controller.check_compliance(self.mock_esxi_context, self.mock_cluster_moid)
        self.mock_vc_rest_client.post_helper.assert_called_once_with(
            url=f"{self.vc_base_url}{config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)}",
        )
        assert result["status"] == ComplianceStatus.FAILED
        assert len(result["message"]["errors"]) == 1
        assert result["message"]["errors"][0]["error"] == Message(message=expected_error_msg).to_dict()
        assert result["message"]["errors"][0]["source"] == ErrorSource(server=self.mock_vc_host_name, type="vcenter",
                                                                       endpoint=self.vc_base_url + config_modules_vmware.controllers.esxi.cluster_config.DESIRED_STATE_SCAN_URL.format(self.mock_cluster_moid)).to_dict()
