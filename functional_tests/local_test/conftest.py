# Copyright 2024 Broadcom. All Rights Reserved.
import os

import pytest

from config_modules_vmware.framework.utils.utils import read_json_file
from functional_tests.utils.constants import AUTH_CONTEXT
from functional_tests.utils.constants import CONTROL
from functional_tests.utils.constants import HOST_NAME
from functional_tests.utils.constants import PRODUCT
from functional_tests.utils.credential_api_client import context_func_dict
from functional_tests.utils.credential_api_client import get_context
from functional_tests.utils.credential_api_client import get_contexts


def pytest_addoption(parser):
    """
    pytest commandline input options
    """

    parser.addoption(
        "--context",
        action="store",
        default="",
        help="product control context json file, used only for local test at appliance",
    )


def pytest_generate_tests(metafunc):
    """
    Dynamically generate test cases
    """
    try:
        get_contexts()
        local_prod_control_ctx_file_path = metafunc.config.getoption("context")
        print(f"Local product control context file: {local_prod_control_ctx_file_path}")
        local_prod_control_ctx = _get_local_prod_control_ctx(local_prod_control_ctx_file_path)
        if "product_control_ctx" in metafunc.fixturenames:
            # Generate test cases based on the product_control_lst
            product_control_ctx_lst = [local_prod_control_ctx]
            test_id_lst = [
                local_prod_control_ctx[PRODUCT]
                + "_"
                + local_prod_control_ctx[CONTROL]
                + "_"
                + local_prod_control_ctx[HOST_NAME]
                + "_local_test"
            ]
            metafunc.parametrize("product_control_ctx", product_control_ctx_lst, ids=test_id_lst)

    except ValueError as e:
        pass


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Configuration html test report
    """
    if not os.path.exists("functional_tests/local_test/reports"):
        os.makedirs("functional_tests/local_test/reports")
    config.option.htmlpath = "functional_tests/local_test/reports/functional_test.html"
    config.option.self_contained_html = True


def _get_local_prod_control_ctx(context_file_path):
    prod_control_ctx = read_json_file(os.path.expanduser(context_file_path))
    if PRODUCT in prod_control_ctx and prod_control_ctx[PRODUCT] in context_func_dict:
        prod_control_ctx[AUTH_CONTEXT] = get_context(prod_control_ctx[PRODUCT], prod_control_ctx[HOST_NAME])
    else:
        prod_control_ctx[AUTH_CONTEXT] = {}
    print(f"product context {prod_control_ctx}")
    return prod_control_ctx
