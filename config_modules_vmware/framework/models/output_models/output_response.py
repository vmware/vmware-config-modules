# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


class OutputResponse:
    """
    Class for handling output response and status.
    """

    def __init__(self):
        """
        Initialize a new OutputResponse instance.
        """
        self._message = None

    @property
    def message(self):
        """
        Return the status message, if any.

        :return: status message.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """
        Update the status message.

        :param message: Status message.
        :type message: str
        """
        self._message = message

    def to_dict(self):
        """
        Get the reformatted output response as dict.

        :return: Reformatted output response.
        :rtype: dict
        """
        output_dict = {}
        if self._message:
            output_dict[consts.MESSAGE] = self._message
        return output_dict
