# Copyright 2024 Broadcom. All Rights Reserved.
import copy

import pytest

from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import Comparator
from config_modules_vmware.interfaces.controller_interface import ControllerInterface
from functional_tests.central_test.conftest import race_track
from functional_tests.utils.constants import AUTH_CONTEXT
from functional_tests.utils.constants import CHECK_COMPLIANCE
from functional_tests.utils.constants import COMPLIANCE_VALUES
from functional_tests.utils.constants import CONTROL
from functional_tests.utils.constants import DRIFT_VALUES
from functional_tests.utils.constants import FAIL
from functional_tests.utils.constants import OVERRIDES
from functional_tests.utils.constants import PASS
from functional_tests.utils.constants import PRODUCT
from functional_tests.utils.constants import REMEDIATION
from functional_tests.utils.constants import RESULT
from functional_tests.utils.constants import ROLLBACK
from functional_tests.utils.constants import STATUS
from functional_tests.utils.constants import VALUE
from functional_tests.utils.control_util import find_and_replace_value
from functional_tests.utils.control_util import find_key
from functional_tests.utils.control_util import find_value


class ValidateControl:
    def __init__(self, product_control_ctx):
        self.product_control_ctx = product_control_ctx
        self.drift_values = product_control_ctx[DRIFT_VALUES]
        self.compliant_values = product_control_ctx[COMPLIANCE_VALUES]
        self.control_api = ControllerInterface(self.product_control_ctx[AUTH_CONTEXT])
        self.control_current_val = self._get_current_value(self.compliant_values)

    def validate_control(self):
        print(f"auth ctx {self.product_control_ctx[AUTH_CONTEXT]}\n")
        try:
            self._validate_control_helper()
            if self.product_control_ctx[ROLLBACK] and self.product_control_ctx[REMEDIATION]:
                self._revert_to_prior_values()
            race_track.test_case_end(PASS)
        except Exception as e:
            race_track.test_case_end(FAIL)
            pytest.fail(
                f"Error with Control test - {self.product_control_ctx[PRODUCT]}: {self.product_control_ctx[CONTROL]}, {e}"
            )

    def _validate_control_helper(self):
        if self.product_control_ctx[REMEDIATION]:
            # Set the control with the drift values
            remediate_status = self.control_api.remediate_with_desired_state(self.drift_values)
            if remediate_status[STATUS].value in [
                RemediateStatus.ERROR,
                RemediateStatus.FAILED,
                RemediateStatus.SKIPPED,
            ]:
                print(f"Error in control_config.remediate_with_desired_state with drift values: {remediate_status}")
            # check the status of introducing drift
            assert remediate_status[STATUS] == RemediateStatus.SUCCESS

            # Run compliance check, it should be non-compliant
            result = self.control_api.check_compliance(self.compliant_values)
            race_track.verify("drift detection", result[STATUS], ComplianceStatus.NON_COMPLIANT)
            if result[STATUS].value in [ComplianceStatus.ERROR, ComplianceStatus.FAILED, ComplianceStatus.SKIPPED]:
                print(f"Error in control_config.check_compliance: {result}")
            assert result[STATUS] == ComplianceStatus.NON_COMPLIANT

            # Check if "current" and "desired" are different
            drift, desired_config = Comparator.get_non_compliant_configs(
                find_value("current", result), find_value("desired", result)
            )
            assert drift is not None or desired_config is not None

            # Remediate the control using COMPLIANT_SPEC
            remediate_status = self.control_api.remediate_with_desired_state(self.compliant_values)
            race_track.verify(REMEDIATION, remediate_status[STATUS], RemediateStatus.SUCCESS)
            if remediate_status[STATUS].value in [
                RemediateStatus.ERROR,
                RemediateStatus.FAILED,
                RemediateStatus.SKIPPED,
            ]:
                print(f"Error in control_config.remediate_with_desired_state: {remediate_status}")

            # Check the successful remediation status
            assert remediate_status[STATUS] == RemediateStatus.SUCCESS

        # Run compliance check, it should be compliant
        result = self.control_api.check_compliance(self.compliant_values)
        if result[STATUS].value in [ComplianceStatus.ERROR, ComplianceStatus.FAILED, ComplianceStatus.SKIPPED]:
            print(f"Error in control_config.check_compliance: {result}")
        race_track.verify(CHECK_COMPLIANCE, result[STATUS], ComplianceStatus.COMPLIANT)
        assert result[STATUS] == ComplianceStatus.COMPLIANT

    def _revert_to_prior_values(self):
        # replace value object in desire spec using the saved prior value of the control
        replace_key = VALUE
        if find_key(OVERRIDES, self.compliant_values):
            replace_key = OVERRIDES
        replace_value = find_value("value", self.control_current_val)
        control_spec = find_and_replace_value(copy.deepcopy(self.compliant_values), replace_key, replace_value)
        print(f"Revert to prior value using control template {control_spec}")
        remediate_status = self.control_api.remediate_with_desired_state(control_spec)
        assert remediate_status[STATUS] == RemediateStatus.SUCCESS

    def _get_current_value(self, desired_state_spec):
        result = self.control_api.get_current_configuration(
            metadata_filter=lambda metadata: metadata.name == self.product_control_ctx[CONTROL]
        )
        print(f"current value: {result}")
        if result[STATUS].value in [ComplianceStatus.ERROR, ComplianceStatus.FAILED, ComplianceStatus.SKIPPED]:
            print(f"Error in _get_current_value: {result}")
        race_track.comment(f"get current value status:  {result[STATUS].value}")
        return result[RESULT]
