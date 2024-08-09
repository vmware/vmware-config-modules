# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import MagicMock
from mock import patch

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.services.workflows.configuration_operations import ConfigurationOperations
from config_modules_vmware.services.workflows.operations_interface import Operations


class TestConfigurationOperations:
    def setup_method(self):
        self.context_mock = self.create_context_mock()
        self.config_template = self.create_config_template()
        self.input_values = {"foo": "bar"}

    def create_context_mock(self):
        context_mock = MagicMock()
        context_mock.product_category.value = "vcenter"
        context_mock.product_version = "8.0.3"
        return context_mock

    def create_config_template(self):
        return {
          "vcenter": "config_modules_vmware.controllers.vcenter.vc_profile.VcProfile"
        }

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_operate_get_current(self, get_class_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template

        def mock_get(context, template):
            return template, []

        get_class_mock.return_value().get = mock_get

        expected_result = {
            consts.STATUS: GetCurrentConfigurationStatus.SUCCESS,
            consts.RESULT: self.input_values
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.GET_CURRENT, self.input_values)
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_operate_get_current_single_error(self, get_class_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        errors = ["Some error in get"]

        # Mock get_class to return a class that returns errors in get
        class MockGetError:
            metadata = ControllerMetadata(name="MockGetError")

            @staticmethod
            def get(context, template):
                return {}, errors

        get_class_mock.return_value = MockGetError

        expected_result = {
            consts.STATUS: GetCurrentConfigurationStatus.FAILED,
            consts.MESSAGE: f"{errors[0]}",
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.GET_CURRENT, self.input_values)
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_operate_get_current_errors(self, get_class_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        errors = ["Some error in get", "Some error in get"]

        # Mock get_class to return a class that returns errors in get
        class MockGetError:
            metadata = ControllerMetadata(name="MockGetError")

            @staticmethod
            def get(context, template):
                return {}, errors

        get_class_mock.return_value = MockGetError

        expected_result = {
            consts.STATUS: GetCurrentConfigurationStatus.FAILED,
            consts.MESSAGE: f"{errors}",
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.GET_CURRENT, self.input_values)
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_operate_check_compliance(self, get_class_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template

        class MockControllerCheckCompliance:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def check_compliance(context, value):
                return {'status': ComplianceStatus.COMPLIANT}

        get_class_mock.return_value = MockControllerCheckCompliance

        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT,
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE, self.input_values)
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.framework.logging.logger_adapter.LoggerAdapter.error')
    def test_operate_check_compliance_input_values_none(self, logger_error_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        with pytest.raises(Exception):
            actual_result = ConfigurationOperations.operate(self.context_mock, Operations.CHECK_COMPLIANCE, None, None)
        logger_error_mock.assert_called_once_with("input_values cannot be None for CHECK_COMPLIANCE operation.")

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_operate_remediate(self, get_class_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template

        class MockControllerRemediate:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

            @staticmethod
            def remediate(context, value):
                return {'status': RemediateStatus.SUCCESS}

        get_class_mock.return_value = MockControllerRemediate

        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.REMEDIATE, self.input_values)
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.framework.logging.logger_adapter.LoggerAdapter.error')
    def test_operate_remediate_input_values_none(self, logger_error_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        with pytest.raises(Exception):
            actual_result = ConfigurationOperations.operate(self.context_mock, Operations.REMEDIATE, None, None)

        logger_error_mock.assert_called_once_with("input_values cannot be None for REMEDIATE operation.")

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_operate_metadata_filter(self, get_class_mock, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template

        class MockController:
            metadata = ControllerMetadata(name="MockController")

            @staticmethod
            def get(context, template):
                return {}, []

        get_class_mock.return_value = MockController
        expected_result = {
            consts.STATUS: GetCurrentConfigurationStatus.SKIPPED,
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.GET_CURRENT, self.input_values, lambda metadata: False)
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_no_matching_product(self, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        self.context_mock.product_category.value = "unknown"

        expected_result = {
            consts.STATUS: GetCurrentConfigurationStatus.SKIPPED,
            consts.MESSAGE: f"{self.context_mock.product_category.value} is not a supported product configuration"
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.GET_CURRENT, self.input_values)
        assert result == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_mapping_template')
    def test_operate_no_matching_product_version(self, get_mapping_template_mock):
        get_mapping_template_mock.return_value = self.config_template
        self.context_mock.product_version = "0.0.0"

        expected_result = {
            consts.STATUS: GetCurrentConfigurationStatus.SKIPPED,
            consts.MESSAGE: f"Version [0.0.0] is not supported for product [{self.context_mock.product_category}]"
        }
        result = ConfigurationOperations.operate(self.context_mock, Operations.GET_CURRENT, self.input_values)
        assert result == expected_result
