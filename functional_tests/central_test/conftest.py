# Copyright 2024 Broadcom. All Rights Reserved.
import os
from pathlib import Path

import pytest

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from functional_tests.central_test.control_compliance_template import ComplianceTemplate
from functional_tests.central_test.control_compliance_template import InputOptions
from functional_tests.utils.credential_api_client import get_contexts
from functional_tests.utils.credential_api_client import get_ssh_credentials
from functional_tests.utils.racetrack import Racetrack

race_track = Racetrack()


def pytest_addoption(parser):
    """
    pytest commandline input options
    """
    # optional include list, it defaults to include all controls for all control and all products
    parser.addoption(
        "--include_list",
        action="store",
        default="",
        help="include list for controls. The query syntax: "
        "--include_list product1:[comma separated control list] or product2:[comma separated control list] or ..."
        " For example: --include_list 'vcenter:ntp,dns,syslog or sddc_manager:ntp,dns"
        " when '--include_list' is not specified it takes all controls for all product except the controls in "
        "exclude_list. when [comma separated control list] is empty it includes all controls from that product.",
    )

    # optional input, it defaults to all controls
    parser.addoption(
        "--exclude_list",
        action="store",
        default="",
        help="exclude list for controls. The query syntax: "
        "--exclude_list product:[comma separated control list] or product:[comma separated control list] or ..."
        " For example: --exclude_list 'vcenter:ntp,dns or sddc_manager:ntp.",
    )

    # required input
    parser.addoption("--compliance_values", action="store", default="", help="compliance values yaml file path")

    # required input
    parser.addoption("--drift_values", action="store", default="", help="drift values yaml file path")

    # required input
    parser.addoption(
        "--rollback",
        action="store",
        default="true",
        help="boolean - true or false for rolling back the changes",
    )


def pytest_generate_tests(metafunc):
    """
    Dynamically generate test cases
    """
    try:
        control_include_dict = _process_control_query(metafunc.config.getoption("include_list"))
        control_exclude_dict = _process_control_query(metafunc.config.getoption("exclude_list"))
        compliance_yaml_file = metafunc.config.getoption("compliance_values")
        compliance_yaml_file_path = _validate_file(compliance_yaml_file)

        drift_yaml_file = metafunc.config.getoption("drift_values")
        drift_yaml_file_path = _validate_file(drift_yaml_file)
        rollback = True if metafunc.config.getoption("rollback").lower() == "true" else False
        context_dict = get_contexts()
        ssh_credential_dict = None
        for hostname in context_dict[BaseContext.ProductEnum.SDDC_MANAGER]:
            if not ssh_credential_dict:
                ssh_credential_dict = get_ssh_credentials(context_dict[BaseContext.ProductEnum.SDDC_MANAGER][hostname])

        input_options = InputOptions(
            control_include_dict=control_include_dict,
            control_exclude_dict=control_exclude_dict,
            compliance_values_file=compliance_yaml_file_path,
            drift_values_file=drift_yaml_file_path,
            context_dict=context_dict,
            ssh_credential_dict=ssh_credential_dict,
            rollback=rollback,
        )
        print(f"include_list, {control_include_dict}\n")
        print(f"exclude_list, {control_exclude_dict}\n")
        print(f"compliance_yaml_file_path, {compliance_yaml_file_path}\n")
        print(f"drift_yaml_file_path, {drift_yaml_file_path}\n")
        print(f"compliance_yaml_file_path, {compliance_yaml_file_path}\n")
        print(f"rollback, {rollback}\n")

        product_control_ctx, test_id_lst = ComplianceTemplate.generate_compliance_templates_test_data(input_options)
        if "product_control_ctx" in metafunc.fixturenames:
            # Generate test cases based on the product_control_ctx
            metafunc.parametrize("product_control_ctx", product_control_ctx, ids=test_id_lst)

    except ValueError as e:
        pass


def _process_control_query(input_query):
    """
    The syntax is: product1:comma_separated_control_lists or product2:comma_separated_control_lists or ...
    Example: vcenter:ntp,dns or sddc_manager:ntp,dns or nsxt:ntp
    """

    control_dict = {}
    if input_query:
        # if there is " or " in the query
        queries = input_query.split(" or ")
        for query in queries:
            splits = [item.strip() for item in query.split(":")]
            if len(splits) > 1:
                if splits[0] not in control_dict.keys():
                    control_dict[splits[0]] = _str_to_set(splits[1])
                else:
                    control_dict[splits[0]] |= _str_to_set(splits[1])

    return control_dict


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Configuration html test report
    """
    if not os.path.exists("functional_tests/central_test/reports"):
        os.makedirs("functional_tests/central_test/reports")
    config.option.htmlpath = "functional_tests/central_test/reports/functional_test.html"
    config.option.self_contained_html = True


def pytest_sessionstart(session):
    # post racetrack tests has started
    race_track.test_set_id = os.getenv("TEST_SET_ID")


def _validate_file(file):
    if len(file) == 0:
        raise Exception(f"file name is empty.")
    path = Path.cwd().joinpath(file) if not file.startswith("/") else Path(file)
    if not path.exists():
        raise Exception(f"{file} doesn't exist.")
    elif path.is_dir():
        raise Exception(f"file '{file}' is a directory.")
    return path


def _str_to_set(str_list):
    return set(filter(None, [item.strip() for item in str_list.split(",")])) if len(str_list) > 0 else {}
