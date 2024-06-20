# Copyright 2024 Broadcom. All Rights Reserved.
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from typing_extensions import List

from config_modules_vmware.framework.models.output_models.configuration_drift_response import Status
from config_modules_vmware.services.apis.models.error_model import Error
from config_modules_vmware.services.apis.models.target_model import Target

VERSION = "1.0-DRAFT"


class Config(BaseModel):
    """Class to represent a drifted configuration"""

    key: str = Field(description="The configuration property.")
    category: str = Field(default=None, description="The component.")


class ConfigAddition(Config):
    """Class to represent the added configuration"""

    value: Any = Field(description="The configuration to be added to the product.")


class ConfigDeletion(Config):
    """Class to represent the configuration to be removed from the product"""

    value: Any = Field(description="The configuration to be removed from the product.")


class ConfigModification(Config):
    """Class to represent the configuration that needs to be modified"""

    current_value: Any = Field(description="The current value from the product.")
    desired_value: Any = Field(description="The desired value from the spec.")


class Result(BaseModel):
    """Class to represent the results of the scan drift API call."""

    additions: List[ConfigAddition] = Field(
        default=None, description="The configurations that needs to be added to the product."
    )
    modifications: List[ConfigModification] = Field(
        default=None, description="The configurations that needs to be " "modified on the product."
    )
    deletions: List[ConfigDeletion] = Field(
        default=None, description="The configurations that needs to be deleted from the product"
    )


class DriftResponsePayload(BaseModel):
    """Class to represent the response format of a scan drift API call."""

    schema_version: str = Field(default=VERSION, description="The drift response spec.")
    id: str = Field(default=None, description="The uuid of the drift.")
    name: str = Field(default="Scan Drifts", description="The name of the function.")
    timestamp: str = Field(description="The timestamp of drift calculation in ISO format (YYYY-MM-DDTHH:MM:SS.mmm)")
    description: str = Field(default=None, description="The description of the function.")
    status: Status = Field(description="The status of the function.")
    result: Result = Field(default=None, description="The drifts.")
    errors: List[Error] = Field(default=None, description="Errors during drift detection.")
    target: Target = Field(description="The targeted product.")
