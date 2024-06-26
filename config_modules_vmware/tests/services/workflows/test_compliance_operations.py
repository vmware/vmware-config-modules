# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import MagicMock
from mock import patch

from config_modules_vmware.framework.auth.contexts.esxi_context import EsxiContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.services.workflows.compliance_operations import ComplianceOperations
from config_modules_vmware.services.workflows.operations_interface import Operations


class TestComplianceOperations:
    def setup_method(self):
        self.context_mock = self.create_context_mock()
        self.esxi_context_mock = MagicMock(spec=EsxiContext)
        self.esxi_context_mock.esx_cli_client = MagicMock()
        self.esxi_context_mock.esxi_host_names = ['esxi-1.abc.local', 'esx-2.abc.local', 'esxi-20.abc.local']
        self.config_template = self.create_config_template()
        self.validate_patch = patch('config_modules_vmware.schemas.schema_utility.validate_input_against_schema',
                                    return_value=None)
        self.validate_mock = self.validate_patch.start()
        self.input_values = {
            'compliance_config': {
                'vcenter': {
                    'ntp': {
                        "value": {
                            "mode": "NTP",
                            "servers": ["10.0.0.250", "216.239.35.8"]
                        }
                    }
                }
            }
        }
        self.esxi_input_values = {
            'compliance_config': {
                'esxi': {
                    'password_max_lifetime': {
                        "value": 900
                    }
                }
            }
        }
    def teardown_method(self):
        self.validate_patch.stop()

    def create_context_mock(self):
        context_mock = MagicMock()
        context_mock.product_category.value = "vcenter"
        return context_mock

    def create_config_template(self):
        return {
            "compliance_config": {
                "vcenter": {
                    "ntp": "config_modules_vmware.controllers.vcenter.ntp_config.NtpConfig",
                    "dns": "config_modules_vmware.controllers.vcenter.dns_config.DnsConfig",
                    "syslog": "config_modules_vmware.controllers.vcenter.syslog_config.SyslogConfig"
                }
            }
        }

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_get_current_items(self, logger_error_mock, get_class_mock):
        result_config = {}
        successful_configs = []
        failed_configs = []
        skipped_configs = []

        def mock_get(context):
            return {"foo": "bar"}, []

        get_class_mock.return_value().get = mock_get

        ComplianceOperations._get_current_items(self.config_template, result_config, self.context_mock,
                                                successful_configs, failed_configs, skipped_configs)

        expected_result = {
            "compliance_config": {
                "vcenter": {
                    "ntp": {
                        "value": {
                            "foo": "bar"
                        }
                    },
                    "dns": {
                        "value": {
                            "foo": "bar"
                        }
                    },
                    "syslog": {
                        "value": {
                            "foo": "bar"
                        }
                    }
                }
            }
        }

        # Assert expected results
        assert result_config == expected_result
        assert not failed_configs
        assert len(successful_configs) == 3
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_get_current_items_module_not_loaded(self, get_class_mock):
        result_config = {}
        successful_configs = []
        failed_configs = []
        skipped_configs = []

        get_class_mock.side_effect = ImportError("No module named 'some_module'")

        ComplianceOperations._get_current_items(self.config_template, result_config, self.context_mock,
                                                successful_configs, failed_configs, skipped_configs)

        # Assert expected results
        assert result_config == {}
        assert len(failed_configs) == 3
        assert not successful_configs

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_get_current_items_get_exception(self, get_class_mock):
        result_config = {}
        successful_configs = []
        failed_configs = []
        skipped_configs = []

        # Mock get_class to return a class that raises an exception in get
        class MockGetException:
            metadata = ControllerMetadata(path_in_schema="MockGetException")

            @staticmethod
            def get(context):
                raise ValueError("Some error in get")

        get_class_mock.return_value = MockGetException

        ComplianceOperations._get_current_items(self.config_template, result_config, self.context_mock,
                                                successful_configs, failed_configs, skipped_configs)

        # Assert expected results
        assert result_config == {}
        assert len(failed_configs) == 3
        assert not successful_configs

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_get_current_items_get_errors(self, get_class_mock):
        result_config = {}
        successful_configs = []
        failed_configs = []
        skipped_configs = []

        # Mock get_class to return a class that returns errors in get
        class MockGetError:
            metadata = ControllerMetadata(path_in_schema="MockGetError")

            @staticmethod
            def get(context):
                return {}, ["Some error in get"]

        get_class_mock.return_value = MockGetError

        ComplianceOperations._get_current_items(self.config_template, result_config, self.context_mock,
                                                successful_configs, failed_configs, skipped_configs)

        # Assert expected results
        assert result_config == {}
        assert len(failed_configs) == 3
        assert not successful_configs

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('logging.Logger.info')
    def test_check_compliance_mapping_not_present(self, get_mapping_template_mock, logger_error_mock):
        self.context_mock.product_category.value = "vcenter"
        get_mapping_template_mock.return_value = self.config_template
        dummy_desired_values = {
            'compliance_config': {
                'vcenter': {
                    'dummy_control_not_present': 10
                }
            }
        }
        with pytest.raises(Exception):
            result = ComplianceOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE,
                                                  dummy_desired_values, None)
            logger_error_mock.assert_called_once_with("New value not present in config template for key "
                                                      "/dummy_control_not_present. Not continuing with "
                                                      "check_compliance operation")
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_get_current_items_partial_failure(self, get_class_mock):
        result_config = {}
        successful_configs = []
        failed_configs = []
        skipped_configs = []
        self.context_mock.product_category.value = "vcenter"

        # Mock get_class to return a class that returns valid value
        class MockGet:
            metadata = ControllerMetadata(path_in_schema="MockGet")

            @staticmethod
            def get(context):
                return {"foo": "bar"}, []

        # Mock get_class to return a class that raises an exception in get
        class MockGetException:
            metadata = ControllerMetadata(path_in_schema="MockGetException")

            @staticmethod
            def get(context):
                raise ValueError("Some error in get")

        get_class_mock.side_effect = [MockGet, MockGet, MockGetException]

        ComplianceOperations._get_current_items(self.config_template, result_config, self.context_mock,
                                                successful_configs, failed_configs, skipped_configs)
        expected_result = {
            'compliance_config': {
                'vcenter': {
                    'ntp': {'value': {'foo': 'bar'}},
                    'dns': {'value': {'foo': 'bar'}}
                }
            }
        }
        # Assert expected results
        assert result_config == expected_result
        assert len(failed_configs) == 1
        assert len(successful_configs) == 2

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_get_current_items(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            result_config.update(
                {'compliance_config': {'vcenter': {'ntp': {'servers': ['1.1.1.1']}}}}
            )

        get_current_items_mock.side_effect = mock_get_current_items
        get_mapping_template_mock.return_value = self.config_template

        # Call the static method to perform GET_CURRENT operation
        result = ComplianceOperations.operate(self.context_mock, Operations.GET_CURRENT)
        # Assert expected results
        self.validate_mock.assert_not_called()
        expected_result = {
            "result": {'compliance_config': {'vcenter': {'ntp': {'servers': ['1.1.1.1']}}}},
            "status": GetCurrentConfigurationStatus.SUCCESS
        }
        assert result == expected_result

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_get_current_items_failed_items(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items_failed(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            failed_configs.append("test")

        get_current_items_mock.side_effect = mock_get_current_items_failed
        get_mapping_template_mock.return_value = self.config_template

        # Call the static method to perform GET_CURRENT operation
        result = ComplianceOperations.operate(self.context_mock, Operations.GET_CURRENT)
        # Assert expected results
        self.validate_mock.assert_not_called()
        expected_result = {
            "status": GetCurrentConfigurationStatus.FAILED,
            "message": f"Failed to get configuration for - ['test']"
        }
        assert result == expected_result

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_get_current_items_partial(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items_failed(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            result_config.update(
                {'compliance_config': {'vcenter': {'ntp': {'servers': ['1.1.1.1']}}}}
            )
            successful_configs.append("test_success")
            failed_configs.append("test_failed")

        get_current_items_mock.side_effect = mock_get_current_items_failed
        get_mapping_template_mock.return_value = self.config_template

        # Call the static method to perform GET_CURRENT operation
        result = ComplianceOperations.operate(self.context_mock, Operations.GET_CURRENT)
        # Assert expected results
        self.validate_mock.assert_not_called()
        expected_result = {
            "result": {'compliance_config': {'vcenter': {'ntp': {'servers': ['1.1.1.1']}}}},
            "status": GetCurrentConfigurationStatus.PARTIAL,
            "message": f"Failed to get configuration for - ['test_failed']"
        }
        assert result == expected_result

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_get_current_items_skipped(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items_skipped(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            skipped_configs.append("test_skipped")

        get_current_items_mock.side_effect = mock_get_current_items_skipped
        get_mapping_template_mock.return_value = self.config_template

        # Call the static method to perform GET_CURRENT operation
        result = ComplianceOperations.operate(self.context_mock, Operations.GET_CURRENT)

        # Assert expected results
        self.validate_mock.assert_not_called()
        expected_result = {
            "status": GetCurrentConfigurationStatus.SUCCESS,
            "message": f"Skipped get configuration for - ['test_skipped']"
        }
        assert result == expected_result

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_get_current_items_failed_skipped(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items_failed_skipped(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            failed_configs.append("test_failed")
            skipped_configs.append("test_skipped")

        get_current_items_mock.side_effect = mock_get_current_items_failed_skipped
        get_mapping_template_mock.return_value = self.config_template

        # Call the static method to perform GET_CURRENT operation
        result = ComplianceOperations.operate(self.context_mock, Operations.GET_CURRENT)

        # Assert expected results
        self.validate_mock.assert_not_called()
        expected_result = {
            "status": GetCurrentConfigurationStatus.FAILED,
            "message": f"Failed to get configuration for - ['test_failed'], Skipped for - ['test_skipped']"
        }
        assert result == expected_result

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_get_current_items_mixed(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items_mixed(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            result_config.update(
                {'compliance_config': {'vcenter': {'ntp': {'servers': ['1.1.1.1']}}}}
            )
            successful_configs.append("test_success")
            failed_configs.append("test_failed")

        get_current_items_mock.side_effect = mock_get_current_items_mixed
        get_mapping_template_mock.return_value = self.config_template

        # Call the static method to perform GET_CURRENT operation
        result = ComplianceOperations.operate(self.context_mock, Operations.GET_CURRENT)
        # Assert expected results
        self.validate_mock.assert_not_called()
        expected_result = {
            "result": {'compliance_config': {'vcenter': {'ntp': {'servers': ['1.1.1.1']}}}},
            "status": GetCurrentConfigurationStatus.PARTIAL,
            "message": f"Failed to get configuration for - ['test_failed']"
        }
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_check_compliance_compliant(self, logger_error_mock, get_class_mock, get_mapping_template_mock):
        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {'status': ComplianceStatus.COMPLIANT}}}},
            'status': ComplianceStatus.COMPLIANT}

        class MockControllerCheckCompliance:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def check_compliance(context, value):
                return {'status': ComplianceStatus.COMPLIANT}

        get_class_mock.return_value = MockControllerCheckCompliance
        get_mapping_template_mock.return_value = self.config_template

        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.CHECK_COMPLIANCE,
            self.input_values,
            None
        )
        # Assert expected results
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_check_compliance_non_compliant(self, logger_error_mock, get_class_mock, get_mapping_template_mock):
        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {'status': ComplianceStatus.NON_COMPLIANT}}}},
            'status': ComplianceStatus.NON_COMPLIANT}

        class MockControllerCheckCompliance:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def check_compliance(context, value):
                return {'status': ComplianceStatus.NON_COMPLIANT}

        get_class_mock.return_value = MockControllerCheckCompliance
        get_mapping_template_mock.return_value = self.config_template

        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.CHECK_COMPLIANCE,
            self.input_values,
            None
        )

        # Assert expected results
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_check_compliance_metadata_disabled(self, logger_error_mock, get_class_mock, get_mapping_template_mock):
        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {'status': ComplianceStatus.SKIPPED}}}},
            'status': ComplianceStatus.COMPLIANT}

        class MockControllerCheckCompliance:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.DISABLED)

            @staticmethod
            def check_compliance(context, value):
                return None

        get_class_mock.return_value = MockControllerCheckCompliance
        get_mapping_template_mock.return_value = self.config_template

        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.CHECK_COMPLIANCE,
            self.input_values,
            None
        )

        # Assert expected results
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_check_compliance_no_metadata(self, logger_error_mock, get_class_mock, get_mapping_template_mock):
        expected_result = {
            'result': {
                'compliance_config': {
                     'vcenter': {
                         'ntp': {
                             'errors': ["type object 'MockControllerCheckCompliance' has no attribute 'metadata'"],
                             'status': ComplianceStatus.FAILED
                        }
                     }
                 }
            },
            'status': ComplianceStatus.FAILED
        }

        class MockControllerCheckCompliance:
            @staticmethod
            def check_compliance(context, value):
                return None

        get_class_mock.return_value = MockControllerCheckCompliance
        get_mapping_template_mock.return_value = self.config_template

        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.CHECK_COMPLIANCE,
            self.input_values,
            None
        )
        # Assert expected results
        assert actual_result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_check_compliance_metadata_filter(self, logger_error_mock, get_class_mock, get_mapping_template_mock):
        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {'status': ComplianceStatus.SKIPPED}}}},
            'status': ComplianceStatus.COMPLIANT}

        class MockControllerCheckCompliance:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def check_compliance(context, value):
                return None

        get_class_mock.return_value = MockControllerCheckCompliance
        get_mapping_template_mock.return_value = self.config_template

        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.CHECK_COMPLIANCE,
            self.input_values,
            lambda metadata: False
        )

        # Assert expected results
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_check_compliance_module_not_loaded(self, get_class_mock, get_mapping_template_mock):
        get_class_mock.side_effect = ImportError("No module named 'some_module'")
        get_mapping_template_mock.return_value = self.config_template

        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.CHECK_COMPLIANCE,
            self.input_values,
            None
        )
        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {'status': ComplianceStatus.FAILED,
                                                                    'errors': ["No module named 'some_module'"]}}}},
            'status': ComplianceStatus.FAILED
        }

        # Assert expected results
        assert actual_result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_check_compliance_controller_check_compliance_exception(self, get_class_mock, get_mapping_template_mock):
        # Mock get_class to return a class that raises an exception in check_compliance
        class MockCheckComplianceException:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def check_compliance(context, value):
                raise ValueError("Some error in check_compliance")

        get_class_mock.return_value = MockCheckComplianceException
        get_mapping_template_mock.return_value = self.config_template

        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.CHECK_COMPLIANCE,
            self.input_values,
            None
        )

        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {'status': ComplianceStatus.FAILED,
                                                                 'errors': ["Some error in check_compliance"]}}}},
            'status': ComplianceStatus.FAILED
        }
        # Assert expected results
        assert actual_result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_remediate_operation_success_with_changes(self, logger_error_mock, get_class_mock, get_mapping_template_mock):
        class MockControllerRemediate:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def remediate(context, value):
                return {'status': RemediateStatus.SUCCESS,
                        'old': {'servers': ['8.8.8.8']},
                        'new': {'servers': ['8.8.4.4']}}

        get_class_mock.return_value = MockControllerRemediate
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.REMEDIATE,
            self.input_values,
            None
        )
        # Assert expected results
        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {
                'old': {'servers': ['8.8.8.8']},
                'new': {'servers': ['8.8.4.4']},
                'status': RemediateStatus.SUCCESS}}}
            },
            'status': RemediateStatus.SUCCESS
        }
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_remediate_operation_success_with_no_changes(self, logger_error_mock, get_class_mock, get_mapping_template_mock):
        class MockControllerRemediate:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def remediate(context, value):
                return {'status': RemediateStatus.SUCCESS}

        get_class_mock.return_value = MockControllerRemediate
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.REMEDIATE,
            self.input_values,
            None
        )
        # Assert expected results
        expected_result = {
            'result': {},
            'status': RemediateStatus.SUCCESS
        }
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_remediate_module_not_loaded(self, get_class_mock, get_mapping_template_mock):
        get_class_mock.side_effect = ImportError("No module named 'some_module'")
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.REMEDIATE,
            self.input_values,
            None
        )

        expected_result = {
            'result': {'compliance_config': {
                'vcenter': {
                    'ntp': {'status': RemediateStatus.FAILED, 'errors': ["No module named 'some_module'"]}}}},
            'status': RemediateStatus.FAILED
        }

        # Assert expected results
        assert actual_result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_remediate_remediate_exception(self, get_class_mock, get_mapping_template_mock):
        # Mock get_class to return a class that raises an exception in remediate
        class MockRemediateException:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def remediate(context, value):
                raise ValueError("Some error in remediate")

        get_class_mock.return_value = MockRemediateException
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.REMEDIATE,
            self.input_values,
            None
        )

        expected_result = {
            'result': {'compliance_config': {'vcenter': {'ntp': {'status': RemediateStatus.FAILED,
                                                                 'errors': ["Some error in remediate"]}}}},
            'status': RemediateStatus.FAILED
        }

        # Assert expected results
        assert actual_result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.framework.logging.logger_adapter.LoggerAdapter.error')
    def test_operate_check_compliance_input_values_none(self, logger_error_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        with pytest.raises(Exception):
            actual_result = ComplianceOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE, None, None)
        logger_error_mock.assert_called_once_with("input_values cannot be None for CHECK_COMPLIANCE operation.")

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.framework.logging.logger_adapter.LoggerAdapter.error')
    def test_operate_remediate_input_values_none(self, logger_error_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        with pytest.raises(Exception):
            actual_result = ComplianceOperations.operate(self.context_mock, Operations.REMEDIATE, None, None)

        logger_error_mock.assert_called_once_with("input_values cannot be None for REMEDIATE operation.")

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.framework.logging.logger_adapter.LoggerAdapter.info')
    def test_operate_key_in_desired_state_not_in_mapping(self, logger_info_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = {}
        dummy_desired_values = {
            'compliance_config': {
                'vcenter': {
                    'dummy_control_not_present': 10
                }
            }
        }

        # Assert expected results
        with pytest.raises(Exception):
            result = ComplianceOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE, dummy_desired_values,
                                                  None)
            logger_info_mock.assert_called_once_with(
                "No controls found for product category vcenter")

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.framework.logging.logger_adapter.LoggerAdapter.error')
    def test_operate_unexpected_desired_state_type(self, logger_error_mock, get_mapping_template_mock):
        input_values = {'compliance_config': 10}
        get_mapping_template_mock.return_value = self.config_template

        with pytest.raises(Exception):
            result = ComplianceOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE,
                                                  input_values, None)
            logger_error_mock.assert_called_once_with("Should be a dictionary of products.")

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.framework.logging.logger_adapter.LoggerAdapter.error')
    def test_check_compliance_invalid_mapping_dict1(self, logger_error_mock, get_mapping_template_mock):
        expected_result = {
            'result': {
                'compliance_config': {
                    'vcenter': {
                        'ntp': {
                            'errors': ['Value key is missing.'],
                            'status': ComplianceStatus.FAILED
                        }
                    }
                }
            },
            'status': ComplianceStatus.FAILED
        }
        input_values = {'compliance_config': {'vcenter': {'ntp': {}}}}
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE, input_values, None)
        # Assert expected results
        assert actual_result == expected_result
        logger_error_mock.assert_called_once()


    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_get_current_esxi_context(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            result_config.update(
                {'compliance_config': {'esxi': {'password_max_lifetime': 90}}}
            )

        get_current_items_mock.side_effect = mock_get_current_items
        get_mapping_template_mock.return_value = {
            'compliance_config': {
                "esxi": {
                    "password_max_lifetime": "config_modules_vmware.controllers.esxi.password_max_lifetime_policy.PasswordMaxLifetimePolicy",
                }
            }
        }
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.return_value = {
            "esxi-1.abc.local": "host-100",
            "esxi-2.abc.local": "host-200",
            "esxi-20.abc.local": None,
        }
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.side_effect = \
            lambda moid: f"Ref-{moid}"
        expected_get_current_response = {
            'status': GetCurrentConfigurationStatus.SUCCESS,
            'result': {
                'esxi-1.abc.local': {
                    'status': GetCurrentConfigurationStatus.SUCCESS,
                    'host_results': {'compliance_config': {'esxi': {'password_max_lifetime': 90}}}
                },
                'esxi-2.abc.local': {
                    'status': GetCurrentConfigurationStatus.SUCCESS,
                    'host_results': {'compliance_config': {'esxi': {'password_max_lifetime': 90}}}
                }
            },
            'message': "Skipped for hosts - ['esxi-20.abc.local']"
        }

        result = ComplianceOperations.operate(self.esxi_context_mock, Operations.GET_CURRENT)
        # Assert expected results
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.assert_called_once_with(
            esxi_host_names=self.esxi_context_mock.esxi_host_names)
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-100')
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-200')

        assert result == expected_get_current_response
        assert get_current_items_mock.call_count == 2

    def test_get_current_esxi_context_skipped(self):
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.return_value = {
            "esxi-1.abc.local": None,
            "esxi-2.abc.local": None,
            "esxi-20.abc.local": None,
        }
        expected_get_current_response = {
            'status': GetCurrentConfigurationStatus.SUCCESS,
            'message': "Skipped for hosts - ['esxi-1.abc.local', 'esxi-2.abc.local', 'esxi-20.abc.local']"
        }

        result = ComplianceOperations.operate(self.esxi_context_mock, Operations.GET_CURRENT)

        # Assert expected results
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.assert_called_once_with(
            esxi_host_names=self.esxi_context_mock.esxi_host_names)

        assert result == expected_get_current_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_get_current_esxi_context_failed(self, get_mapping_template_mock, get_current_items_mock):
        def mock_get_current_items_failed(
                config_template,
                result_config,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter
        ):
            failed_configs.append("test")

        get_current_items_mock.side_effect = mock_get_current_items_failed
        get_mapping_template_mock.return_value = {
            'compliance_config': {
                "esxi": {
                    "password_max_lifetime": "config_modules_vmware.controllers.esxi.password_max_lifetime_policy.PasswordMaxLifetimePolicy",
                }
            }
        }
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.return_value = {
            "esxi-1.abc.local": "host-100",
            "esxi-2.abc.local": "host-200",
            "esxi-20.abc.local": None,
        }
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.side_effect = \
            lambda moid: f"Ref-{moid}"
        expected_get_current_response = {
            'status': GetCurrentConfigurationStatus.FAILED,
            'message': "Operation failed for hosts - ['esxi-1.abc.local', 'esxi-2.abc.local'], "
                       "Skipped for hosts - ['esxi-20.abc.local']"
        }

        result = ComplianceOperations.operate(self.esxi_context_mock, Operations.GET_CURRENT)
        # Assert expected results
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.assert_called_once_with(
            esxi_host_names=self.esxi_context_mock.esxi_host_names)
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-100')
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-200')

        assert result == expected_get_current_response
        assert get_current_items_mock.call_count == 2

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._get_current_items')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_get_current_esxi_context_partial(self, get_mapping_template_mock, get_current_items_mock):
        class MockGetCurrentItems:
            calls = 0

            def mock_get_current_items(
                    self,
                    config_template,
                    result_config,
                    context,
                    successful_configs,
                    failed_configs,
                    skipped_configs,
                    metadata_filter
            ):
                if self.calls == 0:
                    result_config.update(
                        {'compliance_config': {'esxi': {'password_max_lifetime': 90}}}
                    )
                    self.calls += 1
                else:
                    failed_configs.append("test")

        get_current_items_mock.side_effect = MockGetCurrentItems().mock_get_current_items
        get_mapping_template_mock.return_value = {
            'compliance_config': {
                "esxi": {
                    "password_max_lifetime": "config_modules_vmware.controllers.esxi.password_max_lifetime_policy.PasswordMaxLifetimePolicy",
                }
            }
        }
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.return_value = {
            "esxi-1.abc.local": "host-100",
            "esxi-2.abc.local": "host-200",
            "esxi-20.abc.local": None,
        }
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.side_effect = \
            lambda moid: f"Ref-{moid}"
        expected_get_current_response = {
            'status': GetCurrentConfigurationStatus.PARTIAL,
            'result': {
                'esxi-1.abc.local': {
                    'status': GetCurrentConfigurationStatus.SUCCESS,
                    'host_results': {'compliance_config': {'esxi': {'password_max_lifetime': 90}}}
                }
            },
            'message': "Operation failed for hosts - ['esxi-2.abc.local'], "
                       "Skipped for hosts - ['esxi-20.abc.local']"
        }

        result = ComplianceOperations.operate(self.esxi_context_mock, Operations.GET_CURRENT)
        # Assert expected results
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.assert_called_once_with(
            esxi_host_names=self.esxi_context_mock.esxi_host_names)
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-100')
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-200')

        assert result == expected_get_current_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._iterate_desired_state')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_check_compliance_esxi_context(self, get_mapping_template_mock, iterate_desired_state_mock):
        self.context_mock.product_category.value = "esxi"
        iterate_desired_state_mock.return_value = {'result': {}, 'status': ComplianceStatus.COMPLIANT}
        get_mapping_template_mock.return_value = {
            'compliance_config': {
                "esxi": {
                    "password_max_lifetime": "config_modules_vmware.controllers.esxi.password_max_lifetime_policy.PasswordMaxLifetimePolicy",
                }
            }
        }

        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.return_value = {
            "esxi-1.abc.local": "host-100",
            "esxi-2.abc.local": "host-200",
            "esxi-20.abc.local": None,
        }
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.side_effect = \
            lambda moid: f"Ref-{moid}"
        expected_check_compliance_response = {
            'status': ComplianceStatus.COMPLIANT,
            'result': {
                'esxi-1.abc.local': {
                    'status': ComplianceStatus.COMPLIANT,
                    'host_changes': {}
                },
                'esxi-2.abc.local': {
                    'status': ComplianceStatus.COMPLIANT,
                    'host_changes': {}
                },
                'esxi-20.abc.local': {
                    'status': ComplianceStatus.SKIPPED,
                    'errors': ["Host 'esxi-20.abc.local' is not managed by this vCenter."]
                }
            },
            'message': "Skipped for hosts - ['esxi-20.abc.local']"
        }

        result = ComplianceOperations.operate(self.esxi_context_mock, Operations.REMEDIATE, self.esxi_input_values)
        # Assert expected results
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.assert_called_once_with(
            esxi_host_names=self.esxi_context_mock.esxi_host_names)
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-100')
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-200')

        assert result == expected_check_compliance_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._iterate_desired_state')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_remediation_esxi_context_with_changes(self, get_mapping_template_mock, iterate_desired_state_mock):
        self.context_mock.product_category.value = "esxi"
        iterate_desired_state_mock.return_value = {
            'result': {
                'compliance_config': {
                    'esxi': {
                        'password_max_lifetime': {
                            'old': 900,
                            'new': 800,
                            'status': RemediateStatus.SUCCESS
                        }
                    }
                }
            },
            'status': RemediateStatus.SUCCESS
        }
        get_mapping_template_mock.return_value = {
            'compliance_config': {
                "esxi": {
                    "password_max_lifetime": "config_modules_vmware.controllers.esxi.password_max_lifetime_policy.PasswordMaxLifetimePolicy",
                }
            }
        }

        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.return_value = {
            "esxi-1.abc.local": "host-100",
            "esxi-2.abc.local": "host-200",
            "esxi-20.abc.local": None,
        }
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.side_effect = \
            lambda moid: f"Ref-{moid}"
        expected_check_compliance_response = {
            'status': RemediateStatus.SUCCESS,
            'result': {
                'esxi-1.abc.local': {
                    'status': RemediateStatus.SUCCESS,
                    'host_changes': {
                        'compliance_config': {
                            'esxi': {
                                'password_max_lifetime': {
                                    'old': 900,
                                    'new': 800,
                                    'status': RemediateStatus.SUCCESS
                                }
                            }
                        }
                    }
                },
                'esxi-2.abc.local': {
                    'status': RemediateStatus.SUCCESS,
                    'host_changes': {
                        'compliance_config': {
                            'esxi': {
                                'password_max_lifetime': {
                                    'old': 900,
                                    'new': 800,
                                    'status': RemediateStatus.SUCCESS
                                }
                            }
                        }
                    }
                },
                'esxi-20.abc.local': {
                    'status': RemediateStatus.SKIPPED,
                    'errors': ["Host 'esxi-20.abc.local' is not managed by this vCenter."]
                }
            },
            'message': "Skipped for hosts - ['esxi-20.abc.local']"
        }

        result = ComplianceOperations.operate(self.esxi_context_mock, Operations.REMEDIATE, self.esxi_input_values)
        # Assert expected results
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.assert_called_once_with(
            esxi_host_names=self.esxi_context_mock.esxi_host_names)
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-100')
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-200')

        assert result == expected_check_compliance_response

    @patch('config_modules_vmware.services.workflows.compliance_operations.ComplianceOperations._iterate_desired_state')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_remediation_esxi_context_no_changes(self, get_mapping_template_mock, iterate_desired_state_mock):
        self.context_mock.product_category.value = "esxi"
        iterate_desired_state_mock.return_value = {'result': {}, 'status': RemediateStatus.SUCCESS}
        get_mapping_template_mock.return_value = {
            'compliance_config': {
                "esxi": {
                    "password_max_lifetime": "config_modules_vmware.controllers.esxi.password_max_lifetime_policy.PasswordMaxLifetimePolicy",
                }
            }
        }

        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.return_value = {
            "esxi-1.abc.local": "host-100",
            "esxi-2.abc.local": "host-200",
            "esxi-20.abc.local": None,
        }
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.side_effect = \
            lambda moid: f"Ref-{moid}"
        expected_check_compliance_response = {
            'status': RemediateStatus.SUCCESS,
            'result': {
                'esxi-20.abc.local': {
                    'status': RemediateStatus.SKIPPED,
                    'errors': ["Host 'esxi-20.abc.local' is not managed by this vCenter."]
                }
            },
            'message': "Skipped for hosts - ['esxi-20.abc.local']"
        }

        result = ComplianceOperations.operate(self.esxi_context_mock, Operations.REMEDIATE, self.esxi_input_values)
        # Assert expected results
        self.esxi_context_mock.vc_rest_client.return_value.get_filtered_hosts_info.assert_called_once_with(
            esxi_host_names=self.esxi_context_mock.esxi_host_names)
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-100')
        self.esxi_context_mock.vc_vmomi_client.return_value.get_host_ref_for_moid.assert_any_call('host-200')

        assert result == expected_check_compliance_response

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('logging.Logger.error')
    def test_check_compliance_with_skipped_products(self, logger_error_mock, get_mapping_template_mock):
        expected_result = {
            'result': {
                'compliance_config': {
                    'esxi': {
                        'status': ComplianceStatus.SKIPPED,
                        'errors': ['Controls are not applicable for product vcenter']
                    }
                }
            },
            'status': ComplianceStatus.COMPLIANT
        }
        self.context_mock.product_category.value = "vcenter"
        input_values = {'compliance_config': {'esxi': {'password_max_lifetime': 10}}}
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE, input_values, None)
        # Assert expected results
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('logging.Logger.error')
    def test_remediate_with_skipped_products(self, logger_error_mock, get_mapping_template_mock):
        expected_result = {
            'result': {
                'compliance_config': {
                    'esxi': {
                        'status': RemediateStatus.SKIPPED,
                        'errors': ['Controls are not applicable for product vcenter']
                    }
                }
            },
            'status': RemediateStatus.SUCCESS
        }
        self.context_mock.product_category.value = "vcenter"
        input_values = {'compliance_config': {'esxi': {'password_max_lifetime': 10}}}
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(self.context_mock, Operations.REMEDIATE, input_values, None)
        # Assert expected results
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('logging.Logger.error')
    def test_remediate_operation_success_manual_remediation(self, logger_error_mock, get_class_mock,
                                                         get_mapping_template_mock):
        class MockControllerRemediate:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)
            @staticmethod
            def remediate(context, value):
                return {'status': RemediateStatus.SKIPPED, 'errors': ["Manual remediation required"], "current": "test_current", "desired": "test_desired"}

        get_class_mock.return_value = MockControllerRemediate
        get_mapping_template_mock.return_value = self.config_template
        actual_result = ComplianceOperations.operate(
            self.context_mock,
            Operations.REMEDIATE,
            self.input_values,
            None
        )
        # Assert expected results
        expected_result = {
            "result": {'compliance_config': {'vcenter': {'ntp': {'status': RemediateStatus.SKIPPED, 'message': ["Manual remediation required"], "current": "test_current", "desired": "test_desired"}}}},
            'status': RemediateStatus.SUCCESS
        }
        assert actual_result == expected_result
        logger_error_mock.assert_not_called()
