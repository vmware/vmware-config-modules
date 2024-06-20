from mock import patch

from config_modules_vmware.controllers.sddc_manager.auto_rotate_schedule import AutoRotateScheduleConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import SDDC_MANAGER_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestAutoRotateConfig:
    def setup_method(self):
        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.sddc_base_url = SDDC_MANAGER_API_BASE.format(self.mock_vc_host_name)

        # Initialize control
        self.controller = AutoRotateScheduleConfig()

        self.compliant_value = {'credentials': [{'credential_type': 'FTP',
                                                 'frequency': 60,
                                                 'resource_name': 'sddc-manager.vrack.vsphere.local',
                                                 'resource_type': 'BACKUP',
                                                 'username': 'backup'},
                                                {'credential_type': 'API',
                                                 'frequency': 60,
                                                 'resource_name': 'vip-nsx-mgmt.vrack.vsphere.local',
                                                 'resource_type': 'NSXT_MANAGER',
                                                 'username': 'admin'},
                                                {'credential_type': 'SSO',
                                                 'frequency': 60,
                                                 'resource_name': 'vcenter-1.vrack.vsphere.local',
                                                 'resource_type': 'PSC',
                                                 'username': 'administrator@vsphere.local'},
                                                {'credential_type': 'SSH',
                                                 'frequency': 60,
                                                 'resource_name': 'vcenter-1.vrack.vsphere.local',
                                                 'resource_type': 'VCENTER',
                                                 'username': 'root'}]}
        self.get_helper_values = {
            "elements": [
                {
                    "id": "8e083ded-6e9d-4acf-a6f6-e4faaf7bf477",
                    "credentialType": "FTP",
                    "accountType": "SYSTEM",
                    "username": "backup",
                    "password": "mR*3out#2@GF8n$1l6D0",
                    "creationTimestamp": "2024-01-22T08:41:40.034Z",
                    "modificationTimestamp": "2024-01-22T08:41:40.034Z",
                    "resource": {
                        "resourceId": "542f3787-9127-4cb1-8dfe-8e3ce72c8a3e",
                        "resourceName": "sddc-manager.vrack.vsphere.local",
                        "resourceIp": "10.0.0.4",
                        "resourceType": "BACKUP",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:01.829Z"
                    }
                },
                {
                    "id": "6305c45b-5384-402c-a3b9-873bab56d207",
                    "credentialType": "SSH",
                    "accountType": "USER",
                    "username": "root",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:39.253Z",
                    "modificationTimestamp": "2024-01-22T08:41:39.253Z",
                    "resource": {
                        "resourceId": "14f6fd9c-27ee-4136-866a-c146cc4d39c1",
                        "resourceName": "esxi-1.vrack.vsphere.local",
                        "resourceIp": "10.0.0.100",
                        "resourceType": "ESXI",
                        "domainName": "sddcId-1001"
                    }
                },
                {
                    "id": "fff35a64-9cb4-45f3-9148-77c4a07dc062",
                    "credentialType": "API",
                    "accountType": "SYSTEM",
                    "username": "admin",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:40.096Z",
                    "modificationTimestamp": "2024-01-22T08:41:40.096Z",
                    "resource": {
                        "resourceId": "20f8881b-181f-461f-87d8-94720c128ddd",
                        "resourceName": "vip-nsx-mgmt.vrack.vsphere.local",
                        "resourceIp": "10.0.0.30",
                        "resourceType": "NSXT_MANAGER",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:01.829Z"
                    }
                },
                {
                    "id": "ef11d51c-6e3e-430e-99cc-1475939f3d24",
                    "credentialType": "SSO",
                    "accountType": "SYSTEM",
                    "username": "administrator@vsphere.local",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:39.110Z",
                    "modificationTimestamp": "2024-01-22T08:41:39.110Z",
                    "resource": {
                        "resourceId": "d9fb9772-f2d3-4979-b14e-1eae23e501ad",
                        "resourceName": "vcenter-1.vrack.vsphere.local",
                        "resourceIp": "10.0.0.6",
                        "resourceType": "PSC",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:18.033Z"
                    }
                },
                {
                    "id": "eee93a54-bee6-4bfc-a500-150f32de6535",
                    "credentialType": "SSH",
                    "accountType": "USER",
                    "username": "root",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:39.179Z",
                    "modificationTimestamp": "2024-01-22T08:41:39.179Z",
                    "resource": {
                        "resourceId": "fd18127e-3b80-4575-b80f-82ac27fb6eb4",
                        "resourceName": "vcenter-1.vrack.vsphere.local",
                        "resourceIp": "10.0.0.6",
                        "resourceType": "VCENTER",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:01.829Z"
                    }
                },
            ],
            "pageMetadata": {
                "pageNumber": 0,
                "pageSize": 37,
                "totalElements": 37,
                "totalPages": 1
            }
        }
        self.get_helper_non_compliant_values = {
            "elements": [
                {
                    "id": "8e083ded-6e9d-4acf-a6f6-e4faaf7bf477",
                    "credentialType": "FTP",
                    "accountType": "SYSTEM",
                    "username": "backup",
                    "password": "mR*3out#2@GF8n$1l6D0",
                    "creationTimestamp": "2024-01-22T08:41:40.034Z",
                    "modificationTimestamp": "2024-01-22T08:41:40.034Z",
                    "resource": {
                        "resourceId": "542f3787-9127-4cb1-8dfe-8e3ce72c8a3e",
                        "resourceName": "sddc-manager.vrack.vsphere.local",
                        "resourceIp": "10.0.0.4",
                        "resourceType": "BACKUP",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:01.829Z"
                    }
                },
                {
                    "id": "6305c45b-5384-402c-a3b9-873bab56d207",
                    "credentialType": "SSH",
                    "accountType": "USER",
                    "username": "root",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:39.253Z",
                    "modificationTimestamp": "2024-01-22T08:41:39.253Z",
                    "resource": {
                        "resourceId": "14f6fd9c-27ee-4136-866a-c146cc4d39c1",
                        "resourceName": "esxi-1.vrack.vsphere.local",
                        "resourceIp": "10.0.0.100",
                        "resourceType": "ESXI",
                        "domainName": "sddcId-1001"
                    }
                },
                {
                    "id": "fff35a64-9cb4-45f3-9148-77c4a07dc062",
                    "credentialType": "API",
                    "accountType": "SYSTEM",
                    "username": "admin",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:40.096Z",
                    "modificationTimestamp": "2024-01-22T08:41:40.096Z",
                    "resource": {
                        "resourceId": "20f8881b-181f-461f-87d8-94720c128ddd",
                        "resourceName": "vip-nsx-mgmt.vrack.vsphere.local",
                        "resourceIp": "10.0.0.30",
                        "resourceType": "NSXT_MANAGER",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:01.829Z"
                    }
                },
                {
                    "id": "ef11d51c-6e3e-430e-99cc-1475939f3d24",
                    "credentialType": "SSO",
                    "accountType": "SYSTEM",
                    "username": "administrator@vsphere.local",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:39.110Z",
                    "modificationTimestamp": "2024-01-22T08:41:39.110Z",
                    "resource": {
                        "resourceId": "d9fb9772-f2d3-4979-b14e-1eae23e501ad",
                        "resourceName": "vcenter-1.vrack.vsphere.local",
                        "resourceIp": "10.0.0.6",
                        "resourceType": "PSC",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:18.033Z"
                    }
                },
                {
                    "id": "eee93a54-bee6-4bfc-a500-150f32de6535",
                    "credentialType": "SSH",
                    "accountType": "USER",
                    "username": "root",
                    "password": "password",
                    "creationTimestamp": "2024-01-22T08:41:39.179Z",
                    "modificationTimestamp": "2024-01-22T08:41:39.179Z",
                    "resource": {
                        "resourceId": "fd18127e-3b80-4575-b80f-82ac27fb6eb4",
                        "resourceName": "vcenter-1.vrack.vsphere.local",
                        "resourceIp": "10.0.0.6",
                        "resourceType": "VCENTER",
                        "domainName": "sddcId-1001"
                    },
                    "autoRotatePolicy": {
                        "frequencyInDays": 60,
                        "nextSchedule": "2024-03-24T00:00:01.829Z"
                    }
                },
            ],
            "pageMetadata": {
                "pageNumber": 0,
                "pageSize": 37,
                "totalElements": 37,
                "totalPages": 1
            }
        }
        self.put_helper_values = {'operationType': 'UPDATE_AUTO_ROTATE_POLICY', 'elements': [], 'autoRotatePolicy':
            {'frequencyInDays': 60, 'enableAutoRotatePolicy': 'true'}}
        self.non_compliant_value = {'credentials': [{'credential_type': 'FTP',
                                                 'frequency': 60,
                                                 'resource_name': 'sddc-manager.vrack.vsphere.local',
                                                 'resource_type': 'BACKUP',
                                                 'username': 'backup'},
                                                {'credential_type': 'API',
                                                 'frequency': 60,
                                                 'resource_name': 'vip-nsx-mgmt.vrack.vsphere.local',
                                                 'resource_type': 'NSXT_MANAGER',
                                                 'username': 'admin'},
                                                {'credential_type': 'SSO',
                                                 'frequency': 60,
                                                 'resource_name': 'vcenter-1.vrack.vsphere.local',
                                                 'resource_type': 'PSC',
                                                 'username': 'administrator@vsphere.local'},
                                                {'credential_type': 'SSH',
                                                 'frequency': 60,
                                                 'resource_name': 'vcenter-1.vrack.vsphere.local',
                                                 'resource_type': 'VCENTER',
                                                 'username': 'root'}]}
        self.desired_value = {
            "frequency": 60,
        }

        self.output_during_exception = {}
        self.task_info = {
                            "id": "b7047a40-e92f-42df-bddc-15f98dbf5f9b",
                            "status": "IN_PROGRESS"
                        }

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.compliant_value
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while fetching credentials")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.get(mock_sddc_manager_context)

        assert result == self.output_during_exception
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client
        result, errors = self.controller.set(mock_sddc_manager_context, self.desired_value)

        mock_sddc_manager_rest_client.patch_helper.assert_called_with(
            self.sddc_base_url + sddc_manager_consts.CREDENTIALS_URL,
            body=self.put_helper_values)

        assert result == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Setting Auto Rotate Config failed")

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.patch_helper.side_effect = [expected_error]
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result, errors = self.controller.set(mock_sddc_manager_context, self.desired_value)

        mock_sddc_manager_rest_client.patch_helper.assert_called_with(self.sddc_base_url + sddc_manager_consts.CREDENTIALS_URL,
                                                                      body=self.put_helper_values)

        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_non_compliant(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: self.non_compliant_value,
            consts.DESIRED: self.compliant_value
        }

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_check_compliance_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Compliance check failed while fetching credentials")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.check_compliance(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success_already_desired(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.desired_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS,
                           consts.OLD: self.non_compliant_value,
                           consts.NEW: self.compliant_value}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_get_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Exception while getting credentials during remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_remediate_set_failed(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        expected_error = Exception("Remediation failed while setting Auto rotate Config")
        expected_result = {consts.STATUS: RemediateStatus.FAILED,
                           consts.ERRORS: [str(expected_error)]}

        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_rest_client.get_helper.return_value = self.get_helper_non_compliant_values
        mock_sddc_manager_rest_client.patch_helper.side_effect = expected_error
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        result = self.controller.remediate(mock_sddc_manager_context, self.compliant_value)

        assert result == expected_result

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_task_status_success(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = True

        status, errors = self.controller.set(mock_sddc_manager_context, self.compliant_value)

        # Assertions
        assert status == RemediateStatus.SUCCESS
        assert not errors

    @patch('config_modules_vmware.framework.auth.contexts.sddc_manager_context.SDDCManagerContext')
    @patch('config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client.SDDCManagerRestClient')
    def test_task_status_failure(self, mock_sddc_manager_rest_client, mock_sddc_manager_context):
        mock_sddc_manager_rest_client.get_base_url.return_value = self.sddc_base_url
        mock_sddc_manager_context.sddc_manager_rest_client.return_value = mock_sddc_manager_rest_client

        # Set up expected values
        mock_sddc_manager_rest_client.put_helper.return_value = self.task_info
        mock_sddc_manager_rest_client.monitor_task.return_value = False

        status, errors = self.controller.set(mock_sddc_manager_context, self.compliant_value)

        # Assertions
        assert status == RemediateStatus.FAILED
        assert errors
