# Copyright 2024 Broadcom. All Rights Reserved.
from contextvars import ContextVar
from contextvars import Token


class LoggingContext:
    """
    Holds the current context used for logging.
    """

    _controller_metadata_context = ContextVar("controller_metadata")
    _hostname_context = ContextVar("hostname")

    @classmethod
    def get_controller_metadata_context(cls):
        """
        Get controller metadata context.
        :return: The controller metadata context if available else None
        :rtype: ControllerMetadata or None
        """
        return cls._controller_metadata_context.get(None)

    @classmethod
    def set_controller_metadata_context(cls, metadata) -> Token:
        """
        Set controller metadata context.
        :param metadata: The controller metadata
        :type metadata: ControllerMetadata
        :return: The token of the set ContextVar
        :rtype: Token
        """
        return cls._controller_metadata_context.set(metadata)

    @classmethod
    def reset_controller_metadata_context(cls, token: Token):
        """
        Reset the controller metadata context.
        :param token: The ContextVar token
        :type token: Token
        """
        cls._controller_metadata_context.reset(token)

    @classmethod
    def get_hostname_context(cls) -> str or None:
        """
        Get hostname context.
        :return: The hostname context if available else None
        :rtype: str or None
        """
        return cls._hostname_context.get(None)

    @classmethod
    def set_hostname_context(cls, hostname: str) -> Token:
        """
        Set hostname context.
        :param hostname: The hostname
        :type hostname: str
        :return: The token of the set ContextVar
        :rtype: Token
        """
        return cls._hostname_context.set(hostname)

    @classmethod
    def reset_hostname_context(cls, token: Token):
        """
        Reset the hostname context.
        :param token: The ContextVar token
        :type token: Token
        """
        cls._hostname_context.reset(token)


class ControllerMetadataLoggingContext:
    """
    Context Manager to hold controller metadata context for logging.
    """

    _metadata = None
    _token = None

    def __init__(self, metadata):
        self._metadata = metadata

    def __enter__(self):
        self._token = LoggingContext.set_controller_metadata_context(self._metadata)

    def __exit__(self, exc_type, exc_val, exc_tb):
        LoggingContext.reset_controller_metadata_context(self._token)
        self._token = None


class HostnameLoggingContext:
    """
    Context Manager to hold hostname context for logging.
    """

    _hostname = None
    _token = None

    def __init__(self, hostname: str):
        self._hostname = hostname

    def __enter__(self):
        self._token = LoggingContext.set_hostname_context(self._hostname)

    def __exit__(self, exc_type, exc_val, exc_tb):
        LoggingContext.reset_hostname_context(self._token)
        self._token = None
