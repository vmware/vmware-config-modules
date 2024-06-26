# Copyright 2024 Broadcom. All Rights Reserved.
import pytest

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceResponse
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus


class TestComplianceResponse:

    @pytest.fixture
    def compliance_response(self):
        return ComplianceResponse()

    def test_initialization(self, compliance_response):
        assert compliance_response.changes == {}
        assert compliance_response.status == ComplianceStatus.COMPLIANT

    def test_to_dict_method(self, compliance_response):
        compliance_response.status = ComplianceStatus.NON_COMPLIANT
        compliance_response.changes = {"current": "value1", "desired": "value2"}

        expected_dict = {
            consts.STATUS: compliance_response.status,
            consts.CHANGES: compliance_response.changes
        }

        assert compliance_response.to_dict() == expected_dict

    def test_to_dict_method_without_changes(self, compliance_response):
        compliance_response.status = ComplianceStatus.COMPLIANT

        expected_dict = {
            consts.STATUS: compliance_response.status
        }

        assert compliance_response.to_dict() == expected_dict
