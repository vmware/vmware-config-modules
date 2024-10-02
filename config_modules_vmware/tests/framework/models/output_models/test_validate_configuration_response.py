# Copyright 2024 Broadcom. All Rights Reserved.
import pytest

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.validate_configuration_response import ValidateConfigurationResponse
from config_modules_vmware.framework.models.output_models.validate_configuration_response import ValidateConfigurationStatus


class TestValidateConfigurationResponse:

    @pytest.fixture
    def validate_configuration_response(self):
        return ValidateConfigurationResponse()

    def test_initialization(self, validate_configuration_response):
        assert validate_configuration_response.result == {}
        assert validate_configuration_response.status == ValidateConfigurationStatus.VALID

    def test_to_dict_method(self, validate_configuration_response):
        validate_configuration_response.status = ValidateConfigurationStatus.INVALID
        validate_configuration_response.result = {"current": "value1", "desired": "value2"}

        expected_dict = {
            consts.STATUS: validate_configuration_response.status,
            consts.RESULT: validate_configuration_response.result
        }

        assert validate_configuration_response.to_dict() == expected_dict

    def test_to_dict_method_without_result(self, validate_configuration_response):
        validate_configuration_response.status = ValidateConfigurationStatus.VALID

        expected_dict = {
            consts.STATUS: validate_configuration_response.status
        }

        assert validate_configuration_response.to_dict() == expected_dict
