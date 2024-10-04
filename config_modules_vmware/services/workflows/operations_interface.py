# Copyright 2024 Broadcom. All Rights Reserved.
from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Callable
from typing import Type

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata


class Operations(Enum):
    """
    Enum Class to define config operations.
    """

    GET_CURRENT = "get_current"
    REMEDIATE = "remediate"
    CHECK_COMPLIANCE = "check_compliance"
    GET_SCHEMA = "get_schema"
    VALIDATE = "validate"


class OperationsInterface(ABC):
    """
    Base class for controller operations.
    """

    @classmethod
    @abstractmethod
    def operate(
        cls,
        context,
        operation: Operations,
        input_values=None,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
    ):
        """
        Performs the requested Operation on a set of controls.
        :param context: The Context that can be used by the config classes to retrieve value.
        :type context: Context
        :param operation: Operation to perform
        :type operation: Operations
        :param input_values: For get template to populate, for check_compliance/remediate new values that should be set or checked.
        :type input_values: dict
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        """

    @classmethod
    def should_skip_controller(
        cls,
        controller_class_ref: Type[BaseController],
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
    ):
        """
        Should the controller be skipped based off the given metadata filter.
        :param controller_class_ref: The controller class
        :type controller_class_ref: BaseConfigProperty subclass
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        :return: True/False if the controller should be skipped
        :rtype: bool
        """
        if not hasattr(controller_class_ref, "metadata"):
            return True
        if isinstance(metadata_filter, Callable) and not metadata_filter(controller_class_ref.metadata):
            return True
        if controller_class_ref.metadata.status == ControllerMetadata.ControllerStatus.DISABLED:
            return True
        return False
