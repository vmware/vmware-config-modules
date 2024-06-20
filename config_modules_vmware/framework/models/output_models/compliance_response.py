# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse

logger = LoggerAdapter(logging.getLogger(__name__))


class ComplianceStatus(str, Enum):
    """
    Enum Class to define status of compliance for the config.
    """

    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class ComplianceResponse(OutputResponse):
    """
    Class for handling compliance response and status.
    """

    def __init__(self):
        """
        Initialize a new ComplianceResponse instance.
        """
        super().__init__()
        self._status = ComplianceStatus.COMPLIANT
        self._changes = {}

    @property
    def status(self) -> ComplianceStatus:
        """
        Return the compliance status.

        :return: Compliance status.
        :rtype: ComplianceStatus
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
    def status(self, status: ComplianceStatus):
        """
        Update the status.

        :param status: Compliance status.
        :type status: ComplianceStatus
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
        Get the reformatted compliance response as dict.

        :return: Reformatted compliance response.
        :rtype: dict
        """
        output_dict = super().to_dict()
        output_dict[consts.STATUS] = self._status
        if self._changes:
            output_dict[consts.CHANGES] = self._changes
        return output_dict
