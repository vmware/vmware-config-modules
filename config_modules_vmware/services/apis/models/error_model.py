# Copyright 2024 Broadcom. All Rights Reserved.
import socket

from pydantic import BaseModel
from pydantic import Field


class ErrorSource(BaseModel):
    """Class to represent the error source."""

    server: str = Field(default=socket.gethostbyname(""), description="The server hostname.")
    type: str = Field(default="ConfigModules", description="The type of server.")
    endpoint: str = Field(default=None, description="The endpoint for which error occurred.")


class Message(BaseModel):
    """Class to represent the message object."""

    id: str = Field(
        default=None, description="The fully qualified identifier. Useful to identify the localizable_message."
    )
    localizable_message: str = Field(default=None, description="The localizable message.")
    message: str = Field(description="The message.")


class Error(BaseModel):
    """Class to represent the errors caught during the workflow."""

    timestamp: str = Field(description="Timestamp of error occurrence in ISO format (YYYY-MM-DDTHH:MM:SS.mmm)")
    source: ErrorSource = Field(description="The source of the error.")
    error: Message = Field(description="The error message.")
    remediation: Message = Field(default=None, description="The remediation for the error.")
