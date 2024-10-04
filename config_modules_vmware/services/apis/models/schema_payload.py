# Copyright 2024 Broadcom. All Rights Reserved.
from enum import Enum

from pydantic import Field
from typing_extensions import List

from config_modules_vmware.services.apis.models.base_response_model import BaseResponseModel
from config_modules_vmware.services.apis.models.error_model import Error
from config_modules_vmware.services.apis.models.target_model import Target

VERSION = "1.0"


class Status(str, Enum):
    """
    Status enum
    """

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Result(BaseResponseModel):
    """Class to represent the results of the schema API call."""

    json_schema: dict = Field(description="Product schema in json_schema format")


class SchemaResponsePayload(BaseResponseModel):
    """Class to represent the response format of a schema API call."""

    schema_version: str = Field(default=VERSION, description="The schema response spec.")
    id: str = Field(default=None, description="The uuid if applicable.")
    name: str = Field(default="Get Schema", description="The name of the function.")
    timestamp: str = Field(description="The timestamp of drift calculation in ISO format (YYYY-MM-DDTHH:MM:SS.mmm)")
    description: str = Field(default=None, description="The description of the function.")
    status: Status = Field(description="The status of the function.")
    result: Result = Field(default=None, description="The drifts.")
    errors: List[Error] = Field(default=None, description="Errors during schema retrieval.")
    target: Target = Field(description="The targeted product.")
