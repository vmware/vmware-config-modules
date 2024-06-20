# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from mock import patch

from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.interfaces.controller_interface import ControllerInterface
from config_modules_vmware.services.workflows.operations_interface import Operations


class TestControllerInterface:
    def setup_method(self):
        self.context_mock = MagicMock(spec=VcenterContext)
        self.control_config = ControllerInterface(self.context_mock)
        self.desired_state_spec = {
            "compliance_config": {
                "vcenter": {
                    "ntp": {
                        "metadata": {
                            "configuration_id": "1246",
                            "configuration_title": "Configure the ntp servers"
                        },
                        "value": {
                            "mode": "NTP",
                            "servers": ["10.0.0.250", "216.239.35.8"]
                        }
                    },
                    "dns": {
                        "metadata": {
                            "configuration_id": "0000",
                            "configuration_title": "Configure the dns servers"
                        },
                        "value": {
                            "mode": "is_static",
                            "servers": ["10.0.0.250"]
                        }
                    },
                    "syslog": {
                        "metadata": {
                            "configuration_id": "1218",
                            "configuration_title": "Configure the dns servers"
                        },
                        "value": {
                            "servers": [{"hostname": "8.8.4.4",
                                         "port": 90,
                                         "protocol": "TLS"},
                                        {"hostname": "8.8.1.8",
                                         "port": 90,
                                         "protocol": "TLS"}]
                        }
                    }
                }
            }
        }

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations.operate')
    def test_get_current_configuration(self, compliance_operation_operate_mock):
        expected_get_current_response = {
            'status': GetCurrentConfigurationStatus.SUCCESS,
            'result': {
               "compliance_config": {
                   "vcenter": {
                       "ntp": {
                           "value": {
                               "mode": "NTP",
                               "servers": ["10.0.0.250"]
                           }
                       },
                       "syslog": {
                           "value": {
                               "servers": [
                                   {
                                       "hostname": "8.8.4.4",
                                       "port": 90,
                                       "protocol": "TLS"
                                   }
                               ]
                           }
                       }
                   }
               }
            }
        }
        compliance_operation_operate_mock.return_value = {
            'status': GetCurrentConfigurationStatus.SUCCESS,
            'result': expected_get_current_response.get(consts.RESULT)
        }

        result = self.control_config.get_current_configuration()

        # Assert expected results
        compliance_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.GET_CURRENT, input_values=None, metadata_filter=None)
        assert result == expected_get_current_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations.operate')
    def test_get_current_configuration_with_message(self, compliance_operation_operate_mock):
        expected_get_current_response = {
            'status': GetCurrentConfigurationStatus.PARTIAL,
            'result': {
                "compliance_config": {
                    "vcenter": {
                        "ntp": {
                            "status": "SUCCESS",
                            "value": {
                                "mode": "NTP",
                                "servers": ["10.0.0.250"]
                            }
                        }
                    }
                }
            },
            'message': "Failed to get configuration for - ['monitoring.syslog']"
        }
        compliance_operation_operate_mock.return_value = {
            'status': GetCurrentConfigurationStatus.PARTIAL,
            'result': expected_get_current_response.get(consts.RESULT),
            'message': expected_get_current_response.get(consts.MESSAGE)
        }

        result = self.control_config.get_current_configuration()

        # Assert expected results
        compliance_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.GET_CURRENT, input_values=None, metadata_filter=None)
        assert result == expected_get_current_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations.operate')
    def test_get_current_configuration_exception(self, compliance_operation_operate_mock):
        compliance_operation_operate_mock.side_effect = Exception('Test Exception')
        result = self.control_config.get_current_configuration()

        # Assert expected results
        compliance_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.GET_CURRENT, input_values=None, metadata_filter=None)
        assert result == {'status': ComplianceStatus.ERROR, 'message': 'Test Exception'}

    @patch('config_modules_vmware.services.workflows.configuration_operations.ConfigurationOperations.operate')
    def test_get_current_configuration_configuration_operation(self, configuration_operation_operate_mock):
        expected_get_current_response = {
            'status': GetCurrentConfigurationStatus.SUCCESS,
            'result': {"foo": "bar"}
        }
        configuration_operation_operate_mock.return_value = {
            'status': GetCurrentConfigurationStatus.SUCCESS,
            'result': expected_get_current_response.get(consts.RESULT)
        }

        template = {"foo": None}
        result = self.control_config.get_current_configuration(
            metadata_filter=None,
            controller_type=ControllerMetadata.ControllerType.CONFIGURATION,
            template=template
        )

        # Assert expected results
        configuration_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.GET_CURRENT, input_values=template, metadata_filter=None)
        assert result == expected_get_current_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations.operate')
    def test_check_compliance(self, compliance_operation_operate_mock):
        expected_compliance_response = {
            'status': ComplianceStatus.COMPLIANT,
            'changes': {
                "compliance_config": {
                    "vcenter": {
                        "ntp": {
                            "status": "COMPLIANT"
                        },
                        "dns": {
                            "status": "COMPLIANT"
                        },
                        "syslog": {
                            "status": "COMPLIANT"
                        }
                    }
                }
            }
        }
        compliance_operation_operate_mock.return_value = {
            'status': ComplianceStatus.COMPLIANT,
            'result': expected_compliance_response.get("changes")
        }

        result = self.control_config.check_compliance(self.desired_state_spec)

        # Assert expected results
        compliance_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.CHECK_COMPLIANCE, input_values=self.desired_state_spec, metadata_filter=None)
        assert result == expected_compliance_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations.operate')
    def test_check_compliance_exception(self, compliance_operation_operate_mock):
        compliance_operation_operate_mock.side_effect = Exception('Test Exception')
        result = self.control_config.check_compliance(self.desired_state_spec)

        # Assert expected results
        compliance_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.CHECK_COMPLIANCE, input_values=self.desired_state_spec, metadata_filter=None)
        assert result == {'status': ComplianceStatus.ERROR, 'message': 'Test Exception'}

    @patch('config_modules_vmware.services.workflows.configuration_operations.ConfigurationOperations.operate')
    def test_check_compliance_configuration_operation(self, configuration_operation_operate_mock):
        expected_compliance_response = {
            'status': ComplianceStatus.COMPLIANT,
            'changes': {"foo": "bar"}
        }
        configuration_operation_operate_mock.return_value = {
            'status': ComplianceStatus.COMPLIANT,
            'result': expected_compliance_response.get("changes")
        }

        result = self.control_config.check_compliance(
            self.desired_state_spec,
            controller_type=ControllerMetadata.ControllerType.CONFIGURATION
        )

        # Assert expected results
        configuration_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.CHECK_COMPLIANCE, input_values=self.desired_state_spec, metadata_filter=None)
        assert result == expected_compliance_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations.operate')
    def test_remediate_with_desired_state(self, compliance_operation_operate_mock):
        expected_remediation_response = {
            'status': RemediateStatus.SUCCESS,
            'changes': {
                "compliance_config": {
                    "vcenter": {
                        "ntp": {
                            "status": "SUCCESS"
                        },
                        "dns": {
                            "status": "SUCCESS"
                        },
                        "syslog": {
                            "status": "SUCCESS"
                        }
                    }
                }
            }
        }
        compliance_operation_operate_mock.return_value = {
            'status': RemediateStatus.SUCCESS,
            'result': expected_remediation_response.get("changes")
        }
        result = self.control_config.remediate_with_desired_state(self.desired_state_spec)

        # Assert expected results
        compliance_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.REMEDIATE, input_values=self.desired_state_spec, metadata_filter=None)
        assert result == expected_remediation_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations.operate')
    def test_remediate_with_desired_state_exception(self, compliance_operation_operate_mock):
        compliance_operation_operate_mock.side_effect = Exception('Test Exception')
        result = self.control_config.remediate_with_desired_state(self.desired_state_spec)

        # Assert expected results
        compliance_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.REMEDIATE, input_values=self.desired_state_spec, metadata_filter=None)
        assert result == {'status': RemediateStatus.ERROR, 'message': 'Test Exception'}

    @patch('config_modules_vmware.services.workflows.configuration_operations.ConfigurationOperations.operate')
    def test_remediate_configuration_operation(self, configuration_operation_operate_mock):
        expected_remediation_response = {
            'status': RemediateStatus.SUCCESS,
            'changes': {"foo": "bar"}
        }
        configuration_operation_operate_mock.return_value = {
            'status': RemediateStatus.SUCCESS,
            'result': expected_remediation_response.get("changes")
        }
        result = self.control_config.remediate_with_desired_state(
            self.desired_state_spec,
            controller_type=ControllerMetadata.ControllerType.CONFIGURATION
        )

        # Assert expected results
        configuration_operation_operate_mock.assert_called_once_with(
            self.context_mock, Operations.REMEDIATE, input_values=self.desired_state_spec, metadata_filter=None)
        assert result == expected_remediation_response
