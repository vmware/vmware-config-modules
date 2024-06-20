# Copyright 2024 Broadcom. All Rights Reserved.
from enum import Enum


class TargetEnum(Enum):
    """
    Enum class for TARGET.
    """

    REMOTE = "remote"  # running on remote jump host, not the actual appliance
    NSXT_MANAGER = "nsxt_manager"
    NSXT_EDGE = "nsxt_edge"
