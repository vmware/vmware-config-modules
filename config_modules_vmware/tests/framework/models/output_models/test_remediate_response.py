# Copyright 2024 Broadcom. All Rights Reserved.
import pytest

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateResponse
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestRemediateResponse:

    @pytest.fixture
    def remediate_response(self):
        return RemediateResponse()

    def test_initialization(self, remediate_response):
        assert remediate_response.changes == {}
        assert remediate_response.status == RemediateStatus.SUCCESS

    def test_to_dict_method(self, remediate_response):
        remediate_response.status = RemediateStatus.SUCCESS
        remediate_response.changes = {"old": "value1", "new": "value2"}

        expected_dict = {
            consts.STATUS: remediate_response.status,
            consts.CHANGES: remediate_response.changes
        }

        assert remediate_response.to_dict() == expected_dict

    def test_to_dict_method_without_changes(self, remediate_response):
        remediate_response.status = RemediateStatus.SUCCESS

        expected_dict = {
            consts.STATUS: remediate_response.status
        }

        assert remediate_response.to_dict() == expected_dict
