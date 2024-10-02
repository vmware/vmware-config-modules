# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse

logger = LoggerAdapter(logging.getLogger(__name__))


class GetSchemaStatus(str, Enum):
    """
    Enum Class to define status of retrieving the schema.
    """

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class GetSchemaResponse(OutputResponse):
    """
    Class for handling get schema response and status.
    """

    def __init__(self):
        """
        Initialize a new GetSchemaResponse instance.
        """
        super().__init__()
        self._status = GetSchemaStatus.SUCCESS
        self._result = {}

    @property
    def status(self) -> GetSchemaStatus:
        """
        Return the get schema status.

        :return: Get schema status.
        :rtype: GetSchemaStatus
        """
        return self._status

    @property
    def result(self):
        """
        Return the output result.

        :return: Get schema result.
        :rtype: dict
        """
        return self._result

    @status.setter
    def status(self, status: GetSchemaStatus):
        """
        Update the status.

        :param status: Get schema status.
        :type status: GetSchemaStatus
        """
        self._status = status

    @result.setter
    def result(self, result):
        """
        Update the result.

        :param result: Get schema result.
        :type result: dict
        """
        self._result = result

    def to_dict(self):
        """
        Get the reformatted get schema response as dict.

        :return: Reformatted get schema response.
        :rtype: dict
        """
        output_dict = super().to_dict()
        output_dict[consts.STATUS] = self._status
        if self._result:
            output_dict[consts.RESULT] = self._result
        return output_dict