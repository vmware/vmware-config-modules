# Copyright 2024 Broadcom. All Rights Reserved.
from enum import Enum

from pydantic import BaseModel
from pydantic import Field
from typing_extensions import List

from config_modules_vmware.services.apis.models.error_model import Error
from config_modules_vmware.services.apis.models.target_model import Target

VERSION = "1.0-DRAFT"


class GetConfigStatus(str, Enum):
    """
    Enum Class to define status of retrieving the configuration.
    """

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class GetConfigResponsePayload(BaseModel):
    """Class to represent the response format of a scan drift API call."""

    schema_version: str = Field(default=VERSION, description="The get configuration spec.")
    name: str = Field(default="Get Configuration", description="The name of the function.")
    timestamp: str = Field(description="The timestamp of drift calculation in ISO format (YYYY-MM-DDTHH:MM:SS.mmm)")
    description: str = Field(default=None, description="The description of the function.")
    status: GetConfigStatus = Field(description="The status of the get configuration function.")
    result: dict = Field(default=None, description="The current configuration as retrieved from the target product.")
    errors: List[Error] = Field(default=None, description="Errors while retrieving current configuration.")
    target: Target = Field(description="The targeted product.")
