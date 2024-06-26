# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Callable

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.logging.logging_context import ControllerMetadataLoggingContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.services.mapper import mapper_utils
from config_modules_vmware.services.workflows.operations_interface import Operations
from config_modules_vmware.services.workflows.operations_interface import OperationsInterface

logger = LoggerAdapter(logging.getLogger(__name__))


class ConfigurationOperations(OperationsInterface):
    """
    Provides framework for performing get, check_compliance and remediate functions on a set of configuration Controllers.
    """

    @classmethod
    def operate(
        cls,
        context,
        operation: Operations,
        input_values=None,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
    ):
        """
        Performs requested Operation on the configuration controls
        :param context: The Context that can be used by the config classes to retrieve value.
        :type context: Context
        :param operation: Operation to perform
        :type operation: Operations
        :param input_values: For set/remediate/precheck new values that should be set or checked.
        :type input_values: dict
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        """
        config_template = mapper_utils.get_mapping_template(mapper_utils.CONFIGURATION_MAPPING_FILE)
        if operation in (Operations.CHECK_COMPLIANCE, Operations.REMEDIATE) and input_values is None:
            err_msg = f"input_values cannot be None for {operation.name} operation."
            logger.error(err_msg)
            raise Exception(err_msg)
        result_config = {}
        cls._invoke_product_configuration(
            config_template,
            result_config,
            operation,
            context,
            input_values,
            metadata_filter,
        )
        return result_config

    @classmethod
    def _invoke_product_configuration(
        cls,
        config_template,
        result_config,
        operation,
        context: BaseContext,
        input_values,
        metadata_filter,
    ):
        """
        Performs the requested Operation on the given product configuration
        :param config_template: Map of requested config values to be operated on.
        :type config_template: dict
        :param result_config: Map to store result of the configuration
        :type result_config: dict
        :param operation: Operation to perform
        :type operation: Operations
        :param context: The Context that can be used by the config classes to retrieve value.
        :type context: Context
        :param input_values: For set/remediate/precheck new values that should be set or checked.
        :type input_values: dict
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        """
        skipped_status = {
            Operations.CHECK_COMPLIANCE: ComplianceStatus.SKIPPED,
            Operations.REMEDIATE: RemediateStatus.SKIPPED,
            Operations.GET_CURRENT: GetCurrentConfigurationStatus.SKIPPED,
        }[operation]
        if context.product_category.value not in config_template:
            msg = f"{context.product_category.value} is not a supported product configuration"
            logger.info(msg)
            result = {consts.STATUS: skipped_status, consts.MESSAGE: msg}
        else:
            result = {}
            product_version = context.product_version
            supported_versions = config_template[context.product_category.value]
            class_file = None
            if product_version in supported_versions:
                class_file = supported_versions[product_version]
            if class_file is None:
                msg = f"Version [{product_version}] is not supported for product [{context.product_category}]"
                logger.info(msg)
                result = {consts.STATUS: skipped_status, consts.MESSAGE: msg}
            else:
                class_ref = mapper_utils.get_class(class_file)
                config_obj = class_ref()
                if cls.should_skip_controller(class_ref, metadata_filter):
                    logger.debug(f"Skipping configuration {config_obj.metadata.name} with metadata filter")
                    result = {consts.STATUS: skipped_status}
                else:
                    if operation == Operations.GET_CURRENT:
                        with ControllerMetadataLoggingContext(config_obj.metadata):
                            output, errors = config_obj.get(context, input_values)
                        if errors:
                            logger.error(
                                f"Get current configuration for {config_obj.metadata.name} returned errors - {errors}"
                            )
                            result = {
                                consts.STATUS: GetCurrentConfigurationStatus.FAILED,
                                consts.MESSAGE: f"{errors[0]}" if len(errors) == 1 else f"{errors}",
                            }
                        else:
                            result = {consts.STATUS: GetCurrentConfigurationStatus.SUCCESS, consts.RESULT: output}
                    elif operation == Operations.CHECK_COMPLIANCE:
                        with ControllerMetadataLoggingContext(config_obj.metadata):
                            result = config_obj.check_compliance(context, input_values)
                    elif operation == Operations.REMEDIATE:
                        with ControllerMetadataLoggingContext(config_obj.metadata):
                            result = config_obj.remediate(context, input_values)

        result_config.update(result)
