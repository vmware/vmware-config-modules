# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse

logger = LoggerAdapter(logging.getLogger(__name__))


class ValidateConfigurationStatus(str, Enum):
    """
    Enum Class to define status of validating the desired state.
    """

    VALID = "VALID"
    INVALID = "INVALID"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ValidateConfigurationResponse(OutputResponse):
    """
    Class for handling validate response and status.
    """

    def __init__(self):
        """
        Initialize a new ValidateConfigurationResponse instance.
        """
        super().__init__()
        self._status = ValidateConfigurationStatus.VALID
        self._result = {}

    @property
    def status(self) -> ValidateConfigurationStatus:
        """
        Return the validate status.

        :return: Get Validate status.
        :rtype: ValidateConfigurationStatus
        """
        return self._status

    @property
    def result(self):
        """
        Return the output result.

        :return: Validate result.
        :rtype: dict
        """
        return self._result

    @status.setter
    def status(self, status: ValidateConfigurationStatus):
        """
        Update the status.

        :param status: Get Validate status.
        :type status: ValidateConfigurationStatus
        """
        self._status = status

    @result.setter
    def result(self, result):
        """
        Update the result.

        :param result: Validate result.
        :type result: dict
        """
        self._result = result

    def to_dict(self):
        """
        Get the reformatted validate response as dict.

        :return: Reformatted validate response.
        :rtype: dict
        """
        output_dict = super().to_dict()
        output_dict[consts.STATUS] = self._status
        if self._result:
            output_dict[consts.RESULT] = self._result
        return output_dict
