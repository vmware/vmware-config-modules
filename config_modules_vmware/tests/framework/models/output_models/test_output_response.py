# Copyright 2024 Broadcom. All Rights Reserved.
import pytest

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse


class TestOutputResponse:

    @pytest.fixture
    def output_response(self):
        return OutputResponse()

    def test_initialization(self, output_response):
        assert output_response.message is None

    def test_message_property(self, output_response):
        message_data = "output message"
        output_response.message = message_data
        assert output_response.message == message_data

    def test_to_dict_method(self, output_response):
        output_response.message = "output message"

        expected_dict = {
            consts.MESSAGE: output_response.message,
        }

        assert output_response.to_dict() == expected_dict
