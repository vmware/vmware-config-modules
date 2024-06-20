# Copyright 2024 Broadcom. All Rights Reserved.
from functional_tests.central_test.validate_test import ValidateControl


class TestLocalControl:
    def test_local(self, product_control_ctx):
        print("start local test\n")
        test_control = ValidateControl(product_control_ctx)

        test_control.validate_control()
        print("End local test\n")
