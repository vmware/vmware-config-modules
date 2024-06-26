# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse

logger = LoggerAdapter(logging.getLogger(__name__))


class GetCurrentConfigurationStatus(str, Enum):
    """
    Enum Class to define status of retrieving the configuration.
    """

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    PARTIAL = "PARTIAL"


class GetCurrentConfigurationResponse(OutputResponse):
    """
    Class for handling get current configuration response and status.
    """

    def __init__(self):
        """
        Initialize a new GetCurrentConfigurationResponse instance.
        """
        super().__init__()
        self._status = GetCurrentConfigurationStatus.SUCCESS
        self._result = {}

    @property
    def status(self) -> GetCurrentConfigurationStatus:
        """
        Return the get current configuration status.

        :return: Get current configuration status.
        :rtype: GetCurrentConfigurationStatus
        """
        return self._status

    @property
    def result(self):
        """
        Return the output result.

        :return: Get Current Configuration result.
        :rtype: dict
        """
        return self._result

    @status.setter
    def status(self, status: GetCurrentConfigurationStatus):
        """
        Update the status.

        :param status: Get current configuration status.
        :type status: GetCurrentConfigurationStatus
        """
        self._status = status

    @result.setter
    def result(self, result):
        """
        Update the result.

        :param result: Get Current Configuration result.
        :type result: dict
        """
        self._result = result

    def to_dict(self):
        """
        Get the reformatted get current configuration response as dict.

        :return: Reformatted get current configuration response.
        :rtype: dict
        """
        output_dict = super().to_dict()
        output_dict[consts.STATUS] = self._status
        if self._result:
            output_dict[consts.RESULT] = self._result
        return output_dict
