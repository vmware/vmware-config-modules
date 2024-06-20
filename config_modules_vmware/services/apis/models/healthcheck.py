# Copyright 2024 Broadcom. All Rights Reserved.
from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Class to validate and return when performing a health check."""

    status: str = "OK"
