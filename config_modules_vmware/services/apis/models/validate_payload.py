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

    VALID = "VALID"
    INVALID = "INVALID"
    FAILED = "FAILED"


class ValidateResult(BaseResponseModel):
    """Class to represent the result of the validate API"""

    warnings: List[dict] = Field(default=None, description="List of warnings")
    errors: List[dict] = Field(default=None, description="List of errors")
    info: List[dict] = Field(default=None, description="List of info")


class ValidateResponsePayload(BaseResponseModel):
    """Class to represent the response format of the validate response API call."""

    schema_version: str = Field(default=VERSION, description="The validate response spec.")
    id: str = Field(default=None, description="The uuid if applicable.")
    name: str = Field(default="Validate Configuration", description="The name of the function.")
    timestamp: str = Field(description="The timestamp of validate operation in ISO format (YYYY-MM-DDTHH:MM:SS.mmm)")
    description: str = Field(default=None, description="The description of the function.")
    status: Status = Field(description="The status of the function.")
    result: ValidateResult = Field(default=None, description="The validate response.")
    errors: List[Error] = Field(default=None, description="Errors during validation.")
    target: Target = Field(description="The targeted product.")
