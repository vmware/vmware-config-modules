# Copyright 2024 Broadcom. All Rights Reserved.
import pytest

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationResponse
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus


class TestGetCurrentResponse:

    @pytest.fixture
    def get_current_configuration_response(self):
        return GetCurrentConfigurationResponse()

    def test_initialization(self, get_current_configuration_response):
        assert get_current_configuration_response.result == {}
        assert get_current_configuration_response.status == GetCurrentConfigurationStatus.SUCCESS

    def test_to_dict_method(self, get_current_configuration_response):
        get_current_configuration_response.status = GetCurrentConfigurationStatus.SUCCESS
        get_current_configuration_response.result = {"foo": "bar"}

        expected_dict = {
            consts.STATUS: get_current_configuration_response.status,
            consts.RESULT: get_current_configuration_response.result
        }

        assert get_current_configuration_response.to_dict() == expected_dict

    def test_to_dict_method_without_result(self, get_current_configuration_response):
        get_current_configuration_response.status = GetCurrentConfigurationStatus.SUCCESS

        expected_dict = {
            consts.STATUS: get_current_configuration_response.status
        }

        assert get_current_configuration_response.to_dict() == expected_dict
