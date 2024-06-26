# Copyright 2024 Broadcom. All Rights Reserved.
import pytest

from functional_tests.central_test.conftest import race_track
from functional_tests.central_test.validate_test import ValidateControl
from functional_tests.local_test.ssh_tester import SshTest
from functional_tests.utils.constants import CONTROL
from functional_tests.utils.constants import PRODUCT
from functional_tests.utils.constants import REMEDIATION
from functional_tests.utils.constants import SSH_CREDENTIAL
from functional_tests.utils.constants import TEST_TARGET


class TestCentralControl:
    def test_control_validations(self, product_control_ctx):
        """
        1. Preserve the control values
        2. Introduce drift
        3. Perform the check-compliance negative test
        4. Remediate with the desire spec
        5. Perform the check-compliance positive test
        6. Revert back the control to the prior values
        7. Control Config framework will route the check compliance and remediate api calls to the right control based
           on the spec.
        :param product_control_ctx: dictionary of values needed for the test case.
        :type: Dict
        """
        if not product_control_ctx[REMEDIATION]:
            testcase_description = "get configuration, compliance check"
        else:
            testcase_description = "get configuration, drift detection, remediation, after remediation compliance check"

        race_track.test_case_begin(
            f"{product_control_ctx[PRODUCT]}:{product_control_ctx[CONTROL]}",
            "vcf.pipeline.config_module",
            testcase_description,
        )
        print(f"test_case_creation : {testcase_description}")

        print(f"\ntest_control_validations_{product_control_ctx[PRODUCT]}_{product_control_ctx[CONTROL]}")
        if len(product_control_ctx[TEST_TARGET]) > 0:
            self._ssh_test_at_appliance(product_control_ctx)
        else:
            test_control = ValidateControl(product_control_ctx)
            test_control.validate_control()

    @staticmethod
    def _ssh_test_at_appliance(product_control_ctx):
        ssh_test = SshTest.get_instance(product_control_ctx[SSH_CREDENTIAL])
        output, error = ssh_test.run_ssh_test(product_control_ctx)

        if "FAILED functional_tests/local_test/local_test.py" in output:
            race_track.test_case_end("FAIL")
            pytest.fail(
                f"Error with Control test - {product_control_ctx[PRODUCT]}:"
                f" {product_control_ctx[CONTROL]}, {output} {error}"
            )
        else:
            race_track.test_case_end("PASS")
