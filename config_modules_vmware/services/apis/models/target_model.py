# Copyright 2024 Broadcom. All Rights Reserved.
from enum import Enum

from pydantic import BaseModel
from pydantic import Field
from typing_extensions import List

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext


class AuthType(str, Enum):
    """
    Enum Class to define various authentication types.
    """

    SSO = "SSO"
    BASIC = "BASIC"
    SSH = "SSH"


class Auth(BaseModel):
    """Class to represent authentication parameters."""

    username: str = Field(default=None, description="Username.")
    password: str = Field(default=None, description="Password.")
    ssl_thumbprint: str = Field(default=None, description="Optional SSL thumbprint, in case certs are not available.")
    type: AuthType = Field(default=None, description="Type of authentication.")


class Target(BaseModel):
    """Class to represent a target."""

    hostname: str = Field(description="The hostname of the product.")
    type: BaseContext.ProductEnum = Field(default=None, description="The product type.")


class RequestTarget(Target, BaseModel):
    """Class to represent the request target."""

    auth: List[Auth] = Field(default=None, description="The authentication to use.")
