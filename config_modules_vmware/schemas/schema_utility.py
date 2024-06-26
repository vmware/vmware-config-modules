# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging
import os

import jsonschema  # pylint: disable=E0401

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

solution_schema_mapping = {"compliance": "compliance_reference_schema.json"}


def retrieve_reference_schema(solution: str) -> dict:
    """
    Retrieve reference schema for given product.
    @param solution: Supported product or category.
    @type solution: str
    @return: the schema in jsonSchema format.
    @rtype: dict
    """
    if solution.lower() not in solution_schema_mapping:
        raise Exception(f"Schema file for {solution} not defined")

    schema_path = os.path.join(os.path.dirname(__file__), solution_schema_mapping.get(solution.lower()))
    if os.path.exists(schema_path) and os.path.isfile(schema_path):
        try:
            with open(schema_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Exception loading schema file: {e}") from e
    else:
        raise Exception(f"Missing schema file for {solution}")


def validate_input_against_schema(input_desired_state: dict, schema_category: str):
    """
    Validates the input desired state against the reference schema for a given product.
    @param input_desired_state: Input desired state.
    @type input_desired_state: dict
    @param schema_category: Supported product.
    @type schema_category: str
    """
    schema = retrieve_reference_schema(schema_category)
    jsonschema.validate(input_desired_state, schema)
