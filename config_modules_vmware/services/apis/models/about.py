# Copyright 2024 Broadcom. All Rights Reserved.
from pydantic import BaseModel

import config_modules_vmware


class About(BaseModel):
    """Class to represent the package information."""

    name: str = config_modules_vmware.name
    description: str = config_modules_vmware.description
    version: str = config_modules_vmware.version
    author: str = config_modules_vmware.author
