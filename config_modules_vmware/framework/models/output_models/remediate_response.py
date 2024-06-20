# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse

logger = LoggerAdapter(logging.getLogger(__name__))


class RemediateStatus(str, Enum):
    """
    Enum Class to define status for remediation/set of the config.
    """

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    PARTIAL = "PARTIAL"


class RemediateResponse(OutputResponse):
    """
    Class for handling remediation response and status.
    """

    def __init__(self):
        """
        Initialize a new RemediateResponse instance.
        """
        super().__init__()
        self._status = RemediateStatus.SUCCESS
        self._changes = {}

    @property
    def status(self) -> RemediateStatus:
        """
        Return the remediation status.

        :return: Remediation status.
        :rtype: RemediateStatus
        """
        return self._status

    @property
    def changes(self):
        """
        Return the output with current and desired values.

        :return: Changes required or done to be compliant.
        :rtype: dict
        """
        return self._changes

    @status.setter
    def status(self, status: RemediateStatus):
        """
        Update the status.

        :param status: Remediation status.
        :type status: RemediateStatus
        """
        self._status = status

    @changes.setter
    def changes(self, changes):
        """
        Update the changes (current/desired) values.

        :param changes: Changes to be compliant.
        :type changes: dict
        """
        self._changes = changes

    def to_dict(self):
        """
        Get the reformatted remediation response as dict.

        :return: Reformatted remediation response.
        :rtype: dict
        """
        output_dict = super().to_dict()
        output_dict[consts.STATUS] = self._status
        if self._changes:
            output_dict[consts.CHANGES] = self._changes
        return output_dict
