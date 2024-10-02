# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import uuid
from enum import Enum
from typing import Any
from typing import List

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse

logger = LoggerAdapter(logging.getLogger(__name__))


class Status(str, Enum):
    """
    Drift status enum
    """

    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    FAILED = "FAILED"


class Target:
    """
    Target configuration
    """

    def __init__(self, type: BaseContext.ProductEnum, hostname):  # pylint: disable=W0622
        self._type = type
        self._hostname = hostname

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        target = {}
        if self._hostname:
            target["hostname"] = self._hostname
        if self._type:
            target["type"] = self._type
        return target


class Config:
    """
    Configuration Property base class.
    """

    def __init__(self, key: str, category: str = None):
        self._key = key
        self._category = category

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        config = {}
        if self._key:
            config["key"] = self._key
        if self._category:
            config["category"] = self._category
        return config


class ConfigAddition(Config):
    """
    Configuration addition
    """

    def __init__(self, key: str, category: str = None, value: Any = None):
        super().__init__(key, category)
        self._value = value

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        config = super().to_dict()
        if self._value is not None:
            config["value"] = self._value
        return config


class ConfigDeletion(Config):
    """
    Configuration deletion
    """

    def __init__(self, key: str, category: str = None, value: Any = None):
        super().__init__(key, category)
        self._value = value

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        config = super().to_dict()
        if self._value is not None:
            config["value"] = self._value
        return config


class ConfigModification(Config):
    """
    Configuration modification
    """

    def __init__(self, key: str, category: str = None, current_value: Any = None, desired_value: Any = None):
        super().__init__(key, category)
        self._current_value = current_value
        self._desired_value = desired_value

    @property
    def current_value(self):
        """
        Return current value.

        :return: current value.
        :rtype: Any
        """
        return self._current_value

    @current_value.setter
    def current_value(self, current_value):
        """
        Set current value

        :param current_value: current value.
        :type current_value: Any
        """
        self._current_value = current_value

    @property
    def desired_value(self):
        """
        Return desired value.

        :return: desired value
        :rtype: Any
        """
        return self._desired_value

    @desired_value.setter
    def desired_value(self, desired_value):
        """
        Set desired value.

        :param desired_value: desired value.
        :type desired_value: Any
        """
        self._desired_value = desired_value

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        config = super().to_dict()
        if self._current_value is not None:
            config["current_value"] = self._current_value
        if self._desired_value is not None:
            config["desired_value"] = self._desired_value
        return config


class Result:
    """
    Result
    """

    def __init__(
        self,
        additions: List[ConfigAddition] = None,
        deletions: List[ConfigDeletion] = None,
        modifications: List[ConfigModification] = None,
    ):
        self._additions = additions
        self._deletions = deletions
        self._modifications = modifications

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        result = {}
        if self._additions:
            result["additions"] = [added.to_dict() for added in self._additions]
        if self._deletions:
            result["deletions"] = [deleted.to_dict() for deleted in self._deletions]
        if self._modifications:
            result["modifications"] = [modified.to_dict() for modified in self._modifications]
        return result


class ErrorSource:
    """
    Source of error
    """

    def __init__(
        self,
        type: str,  # pylint: disable=W0622
        server: str = None,
        endpoint: str = None,
    ):
        self._server = server
        self._type = type
        self._endpoint = endpoint

    @property
    def server(self) -> str:
        """
        Return server.

        :return: server
        :rtype: str
        """
        return self._server

    @server.setter
    def server(self, server: str):
        """
        Set server.

        :param server: server.
        :type server: str
        """
        self._server = server

    @property
    def endpoint(self) -> str:
        """
        Return endpoint.

        :return: endpoint
        :rtype: str
        """
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpoint: str):
        """
        Set endpoint.

        :param endpoint: endpoint.
        :type endpoint: str
        """
        self._endpoint = endpoint

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        source = {}
        if self._server:
            source["server"] = self._server
        if self._type:
            source["type"] = self._type
        if self._endpoint:
            source["endpoint"] = self._endpoint
        return source


class Message:
    """
    Error Message
    """

    def __init__(
        self,
        message: str,
        id: str = None,  # pylint: disable=W0622
        localizable_message: str = None,
    ):
        self._message = message
        self._id = id
        self._localizable_message = localizable_message

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        message = {}
        if self._message:
            message["message"] = self._message
        if self._id:
            message["id"] = self._id
        if self._localizable_message:
            message["localizable_message"] = self._localizable_message
        return message


class Error:
    """
    Error object
    """

    def __init__(self, timestamp: str, error: Message, source: ErrorSource = None, remediation: Message = None):
        self._timestamp = timestamp
        self._source = source
        self._error = error
        self._remediation = remediation

    @property
    def remediation(self) -> Message:
        """
        Return remediation message.

        :return: remediation message
        :rtype: Message
        """
        return self._remediation

    @remediation.setter
    def remediation(self, remediation: Message):
        """
        Set remediation message.

        :param remediation: status.
        :type remediation: Message
        """
        self._remediation = remediation

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        error = {}
        if self._timestamp:
            error["timestamp"] = self._timestamp
        if self._error:
            error["error"] = self._error.to_dict()
        if self._source:
            error["source"] = self._source.to_dict()
        if self._remediation:
            error["remediation"] = self._remediation.to_dict()
        return error


class ConfigurationDriftResponse(OutputResponse):
    """
    Class for handling compliance response and status.
    """

    def __init__(
        self,
        name: str,
        description: str,
        timestamp: str,
        target: Target,
        status: Status = None,
        result: Result = None,
        errors: List[Error] = None,
    ):
        """
        Initialize a new ConfigurationDriftResponse instance.
        """
        super().__init__()
        self._schema_version = "1.0-DRAFT"
        self._id = uuid.uuid4()
        self._name = name
        self._timestamp = timestamp
        self._description = description
        self._status = status
        self._result = result
        self._target = target
        self._errors = errors

    @property
    def status(self) -> Status:
        """
        Return drift status.

        :return: status
        :rtype: Status
        """
        return self._status

    @status.setter
    def status(self, status: Status):
        """
        Set drift status.

        :param status: status.
        :type status: Status
        """
        self._status = status

    @property
    def description(self) -> str:
        """
        Return description.

        :return: description
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """
        Set description.

        :param description: description.
        :type description: str
        """
        self._description = description

    @property
    def result(self) -> Result:
        """
        Return drift result.

        :return: drift result
        :rtype: Result
        """
        return self._result

    @result.setter
    def result(self, result: Result):
        """
        Set drift result.

        :param result: drift result.
        :type result: Result
        """
        self._result = result

    @property
    def errors(self) -> List[Error]:
        """
        Return error messages in drift response.

        :return: error messages
        :rtype: List[Error]
        """
        return self._errors

    @errors.setter
    def errors(self, errors: List[Error]):
        """
        Set errors in drift response.

        :param errors: error messages.
        :type errors: List[Error]
        """
        self._errors = errors

    def to_dict(self):
        """
        Convert current state to dict.

        :return: dict output.
        :rtype: dict
        """
        drift_response_spec = {"id": str(self._id), "schema_version": self._schema_version}
        if self._name:
            drift_response_spec["name"] = self._name
        if self._description:
            drift_response_spec["description"] = self._description
        if self._target:
            drift_response_spec["target"] = self._target.to_dict()
        if self._status:
            drift_response_spec["status"] = self._status
        if self._timestamp:
            drift_response_spec["timestamp"] = str(self._timestamp)
        if self._result:
            drift_response_spec["result"] = self._result.to_dict()
        if self._errors:
            drift_response_spec["errors"] = [error.to_dict() for error in self._errors]
        return drift_response_spec
