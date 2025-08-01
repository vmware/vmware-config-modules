# Copyright 2024 Broadcom. All Rights Reserved.
from pydantic import BaseModel
from pydantic import Field

from config_modules_vmware.services.apis.models.target_model import RequestTarget


class GetConfigurationRequest(BaseModel):
    """Class to represent the request format of a get configuration API call."""

    target: RequestTarget = Field(description="The product target information.")
    template: dict = Field(default=None, description="Filter spec to filter, based on the product schema.")


class ScanDriftsRequest(BaseModel):
    """Class to represent the request format of a scan drifts API call."""

    target: RequestTarget = Field(description="The product target information.")
    input_spec: dict = Field(description="Desired state input spec, based on the product schema.")
