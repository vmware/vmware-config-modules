# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from _pytest.outcomes import fail
from jsonschema.validators import Draft7Validator

from config_modules_vmware.schemas.schema_utility import retrieve_reference_schema
from config_modules_vmware.schemas.schema_utility import validate_input_against_schema


def test_retrieve_reference_schema():
    """
    Test to retrieve reference schema
    """
    reference_schema = retrieve_reference_schema('compliance')
    assert reference_schema is not None


def test_retrieve_missing_reference_schema():
    """
    Test to retrieve missing reference schema
    """
    with pytest.raises(Exception):
        reference_schema = retrieve_reference_schema('VCENTER')
        assert reference_schema is None


def test_validate_valid_schema():
    """
    Test to validate input desired state against a given schema
    """
    validate_compliance_schema = {"compliance_config":{"vcenter":{"dns":{"value":{"mode":"is_static","servers":["8.8.8.8"]},"metadata":{"configuration_id":"123","configuration_title":""}}}}}
    try:
        validate_input_against_schema(validate_compliance_schema, "compliance")
    except Exception as e:
        assert False, F'validate_input_against_schema raised an exception {e}'


def test_validate_invalid_schema():
    """
    Test to validate invalid input desired state against a given schema
    """
    validate_compliance_schema = {"compliance_config":{"vcenter":{"dns":{"value":{"mode":"is_static","servers":[]},"metadata":{"configuration_id":123,"configuration_title":""}}}}}
    with pytest.raises(Exception):
        validate_input_against_schema(validate_compliance_schema, "compliance")


def test_valid_compliance_schema():
    """
    Test to validate if compliance schema is valid
    """
    try:
        compliance_schema = retrieve_reference_schema("compliance")
        Draft7Validator.check_schema(compliance_schema)
    except Exception:
        fail("Exception validating compliance schema. Failing the test case.")
