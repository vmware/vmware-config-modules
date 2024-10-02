# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Callable

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import EsxiContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.logging.logging_context import ControllerMetadataLoggingContext
from config_modules_vmware.framework.logging.logging_context import HostnameLoggingContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.schemas import schema_utility
from config_modules_vmware.services.config import Config
from config_modules_vmware.services.mapper import mapper_utils
from config_modules_vmware.services.workflows.operations_interface import Operations
from config_modules_vmware.services.workflows.operations_interface import OperationsInterface

logger = LoggerAdapter(logging.getLogger(__name__))


class ComplianceOperations(OperationsInterface):
    """
    Provides framework for performing get, check_compliance and remediate functions on a set of compliance Controllers.
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
        Performs requested Operation on the compliance controls
        :param context: The Context that can be used by the config classes to retrieve value.
        :type context: Context
        :param operation: Operation to perform
        :type operation: Operations
        :param input_values: For set/remediate/precheck new values that should be set or checked.
        :type input_values: dict
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        """

        # For ESXi product, call esxi_workflow and return the result
        if isinstance(context, EsxiContext):
            default_status = {
                Operations.CHECK_COMPLIANCE: ComplianceStatus.COMPLIANT,
                Operations.REMEDIATE: RemediateStatus.SKIPPED,
                Operations.GET_CURRENT: GetCurrentConfigurationStatus.SUCCESS,
            }[operation]
            result = {consts.STATUS: default_status}
            cls._esxi_workflow(result, input_values, context, operation, metadata_filter)
            # Remove empty result
            if not result[consts.RESULT]:
                del result[consts.RESULT]
            return result

        # For Non ESXi products
        config_template = mapper_utils.get_mapping_template(mapper_utils.COMPLIANCE_MAPPING_FILE)

        if consts.COMPLIANCE_CONFIG not in config_template or not isinstance(
            config_template.get(consts.COMPLIANCE_CONFIG), dict
        ):
            raise Exception("Incorrect config template.")

        if operation == Operations.GET_CURRENT:
            get_current_output = {}
            successful_configs = []
            failed_configs = []
            skipped_configs = []
            cls._get_current_items(
                config_template,
                get_current_output,
                context,
                successful_configs,
                failed_configs,
                skipped_configs,
                metadata_filter,
            )
            result = {
                consts.RESULT: get_current_output,
                consts.STATUS: GetCurrentConfigurationStatus.SUCCESS,
            }
            # Set message
            if failed_configs and skipped_configs:
                result[
                    consts.MESSAGE
                ] = f"Failed to get configuration for - {failed_configs}, Skipped for - {skipped_configs}"
            elif failed_configs:
                result[consts.MESSAGE] = f"Failed to get configuration for - {failed_configs}"
            elif skipped_configs:
                result[consts.MESSAGE] = f"Skipped get configuration for - {skipped_configs}"

            # If there are both failed and success, mark as PARTIAL
            if failed_configs and successful_configs:
                result[consts.STATUS] = GetCurrentConfigurationStatus.PARTIAL
            elif failed_configs:
                result[consts.STATUS] = GetCurrentConfigurationStatus.FAILED

            # Remove empty result
            if not result[consts.RESULT]:
                del result[consts.RESULT]
            return result

        elif operation == Operations.CHECK_COMPLIANCE or operation == Operations.REMEDIATE:
            # For CHECK_COMPLIANCE and REMEDIATE operation, validate desired input spec against schema
            # and perform check compliance/remediation calling iterate_desired_state
            if input_values is None:
                err_msg = f"input_values cannot be None for {operation.name} operation."
                logger.error(err_msg)
                raise Exception(err_msg)
            schema_utility.validate_input_against_schema(input_values, "compliance")
            operation_output = {}
            overall_status = RemediateStatus.SKIPPED if operation == Operations.REMEDIATE else ComplianceStatus.SKIPPED
            return cls._iterate_desired_state(
                config_template,
                input_values,
                context,
                operation_output,
                operation.value,
                metadata_filter,
                overall_status,
            )
        else:
            err_msg = f"{operation.name} is not a valid operation for compliance controls."
            logger.error(err_msg)
            raise Exception(err_msg)

    @classmethod
    def _get_current_items(
        cls,
        config_template: dict,
        result_config: dict,
        context: BaseContext,
        successful_configs: list,
        failed_configs: list,
        skipped_configs: list,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
    ):
        """
        Get requested configs which will be populated in result_config.
        :param config_template: Map of requested config values to be operated on.
        :type config_template: dict
        :param result_config: Map to store result of each get configuration
        :type result_config: dict
        :param context: The Context that can be used by the config classes to retrieve value.
        :type context: Context
        :param successful_configs: Configs that are successful
        :type successful_configs: list
        :param failed_configs: Configs that have failed
        :type failed_configs: list
        :param skipped_configs: Configs that have been skipped
        :type skipped_configs: list
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        """

        if context.product_category.value in config_template[consts.COMPLIANCE_CONFIG]:
            result_config["compliance_config"] = {}
            product_controls_template = config_template[consts.COMPLIANCE_CONFIG][context.product_category.value]
            if not product_controls_template or not isinstance(product_controls_template, dict):
                raise Exception(f"Valid template is not present for product {context.product_category.value}")

            # Template for product is present and there are controls for this product.
            result_config[consts.COMPLIANCE_CONFIG][context.product_category.value] = {}
            controls_config_result = {}
            for control_name, control_class_ref in product_controls_template.items():
                config_obj = None
                try:
                    class_ref = mapper_utils.get_class(control_class_ref)
                    if cls.should_skip_controller(class_ref, metadata_filter):
                        logger.info(f"Skipping control {class_ref.metadata.path_in_schema} with metadata filter")
                    else:
                        config_obj = class_ref()
                        with ControllerMetadataLoggingContext(config_obj.metadata):
                            result, errors = config_obj.get(context)
                        if errors:
                            if len(errors) == 1 and errors[0] == consts.SKIPPED:
                                logger.info(f"Skipping control {control_name}.{config_obj.metadata.path_in_schema}")
                                skipped_configs.append(f"{control_name}.{config_obj.metadata.path_in_schema}")
                            else:
                                logger.error(
                                    f"Get current configuration for {config_obj.metadata.path_in_schema} "
                                    f"returned errors - {errors}"
                                )
                                failed_configs.append(f"{control_name}.{config_obj.metadata.path_in_schema}")
                        else:
                            controls_config_result[control_name] = {consts.VALUE: result}
                            successful_configs.append(f"{control_name}.{config_obj.metadata.path_in_schema}")
                except Exception as e:
                    logger.error(f"Exception in get current configuration {e}.")
                    failed_configs.append(
                        f"{control_name}.{config_obj.metadata.path_in_schema if config_obj else control_class_ref}"
                    )
            if controls_config_result:
                result_config[consts.COMPLIANCE_CONFIG][context.product_category.value] = controls_config_result
            else:
                del result_config[consts.COMPLIANCE_CONFIG]

    @classmethod
    def _update_overall_status(cls, operation, control_status: str, overall_status: str) -> str:
        if operation == Operations.CHECK_COMPLIANCE.value:
            if control_status == ComplianceStatus.FAILED or overall_status == ComplianceStatus.FAILED:
                return ComplianceStatus.FAILED
            elif control_status == ComplianceStatus.NON_COMPLIANT or overall_status == ComplianceStatus.NON_COMPLIANT:
                return ComplianceStatus.NON_COMPLIANT
            elif control_status == ComplianceStatus.COMPLIANT or overall_status == ComplianceStatus.COMPLIANT:
                return ComplianceStatus.COMPLIANT
        else:
            if (
                control_status == RemediateStatus.FAILED
                or control_status == RemediateStatus.PARTIAL
                or overall_status == RemediateStatus.FAILED
            ):
                return RemediateStatus.FAILED
            elif control_status == RemediateStatus.SUCCESS or overall_status == RemediateStatus.SUCCESS:
                return RemediateStatus.SUCCESS
        return overall_status

    @classmethod
    def _iterate_desired_state(
        cls, mapping, desired_state_spec, context, result_config, operation, metadata_filter, overall_status
    ):
        """
        Return the check compliance/remediation response for the desired state spec..
        :param mapping: Map of requested config values to be operated on.
        :type mapping: dict
        :param desired_state_spec: Desired state spec to operate on.
        :type desired_state_spec: dict
        :param context: The Context that can be used by the config classes to retrieve value.
        :type context: Context
        :param result_config: Map to store result of each get configuration
        :type result_config: dict
        :param operation: Operation type - check compliance or remediation
        :type operation: Operations
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        :param overall_status: Overall status of the compliance/remediation operation
        :type overall_status: str - ComplianceStatus/RemediateStatus
        """
        skipped_status = (
            ComplianceStatus.SKIPPED if operation == Operations.CHECK_COMPLIANCE.value else RemediateStatus.SKIPPED
        )
        failed_status = (
            ComplianceStatus.FAILED if operation == Operations.CHECK_COMPLIANCE.value else RemediateStatus.FAILED
        )
        if context.product_category.value not in desired_state_spec[consts.COMPLIANCE_CONFIG]:
            logger.info(f"Desired spec does not include {context.product_category.value}")

        result_config[consts.COMPLIANCE_CONFIG] = {}

        include_metadata_config = Config().get_section("metadata").getboolean("PublishMetadata", fallback=False)
        # Iterate over all the products and populate result config for the product
        for product in desired_state_spec[consts.COMPLIANCE_CONFIG]:
            result_config[consts.COMPLIANCE_CONFIG][product] = {}
            if product != context.product_category.value:
                # For products not part of the context, append status as SKIPPED and error message as not applicable
                result_config[consts.COMPLIANCE_CONFIG][product] = {
                    consts.STATUS: skipped_status,
                    consts.ERRORS: [f"Controls are not applicable for product {context.product_category.value}"],
                }
            else:
                # Desired spec is already validated against schema.Fetch check compliance or remediation for the product
                # Iterate over all the controls for the product and populate result config with their responses.
                for control_name, control_data in desired_state_spec[consts.COMPLIANCE_CONFIG][product].items():
                    control_class_ref = mapping.get(consts.COMPLIANCE_CONFIG, {}).get(product, {}).get(control_name)
                    if not control_class_ref:
                        raise Exception(
                            f"Mapping for {control_name} not defined for product {context.product_category}"
                        )
                    else:
                        try:
                            class_ref = mapper_utils.get_class(control_class_ref)
                            if cls.should_skip_controller(class_ref, metadata_filter):
                                logger.info(
                                    f"Skipping control {class_ref.metadata.path_in_schema} with metadata filter"
                                )
                                result_config[consts.COMPLIANCE_CONFIG][product][control_name] = {
                                    consts.STATUS: skipped_status
                                }
                            else:
                                config_obj = class_ref()
                                operation_function = getattr(config_obj, operation)
                                if consts.VALUE not in control_data:
                                    raise Exception("Value key is missing.")
                                with ControllerMetadataLoggingContext(config_obj.metadata):
                                    control_result = operation_function(context, control_data[consts.VALUE])
                                # For the controls which are skipped during compliance or remediation with errors set,
                                # Convert 'errors' key to 'message' key.
                                if consts.ERRORS in control_result and (
                                    control_result.get(consts.STATUS) == RemediateStatus.SKIPPED
                                    or control_result.get(consts.STATUS) == ComplianceStatus.SKIPPED
                                ):
                                    control_result[consts.MESSAGE] = control_result.get(consts.ERRORS)
                                    del control_result[consts.ERRORS]
                                # For 'remediate' operation, only add the result in the result_config when there
                                # are some changes done or some errors occurred or remediation is not implemented
                                if (
                                    operation != Operations.REMEDIATE.value
                                    or consts.OLD in control_result
                                    or consts.NEW in control_result
                                    or consts.ERRORS in control_result
                                    or consts.MESSAGE in control_result
                                    or include_metadata_config
                                ):
                                    result_config[consts.COMPLIANCE_CONFIG][product][control_name] = control_result
                                overall_status = cls._update_overall_status(
                                    operation, control_result.get(consts.STATUS), overall_status
                                )
                            if include_metadata_config:
                                result_config[consts.COMPLIANCE_CONFIG][product][control_name][
                                    consts.METADATA
                                ] = class_ref.metadata.to_dict()
                        except Exception as e:
                            logger.error(f"Exception in control {control_name} for {operation} operation {e}.")
                            result_config[consts.COMPLIANCE_CONFIG][product][control_name] = {
                                consts.STATUS: failed_status,
                                consts.ERRORS: [str(e)],
                            }
                            overall_status = failed_status
            # Delete the empty product keys
            if not result_config[consts.COMPLIANCE_CONFIG][product]:
                del result_config[consts.COMPLIANCE_CONFIG][product]

        # Delete the empty compliance config
        if not result_config[consts.COMPLIANCE_CONFIG]:
            del result_config[consts.COMPLIANCE_CONFIG]

        return {consts.RESULT: result_config, consts.STATUS: overall_status}

    @classmethod
    def _esxi_workflow(
        cls,
        result_config: dict,
        desired_state_spec: dict,
        context: EsxiContext,
        operation: Operations,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
    ):
        """
        Invoke workflow for esxi hosts.
        :param result_config: Map to store result of each get configuration
        :type result_config: dict
        :param desired_state_spec: The input desired state spec.
        :type desired_state_spec: dict
        :param context: The Context that can be used by the config classes to retrieve value.
        :type context: Context
        :param operation: Operation to perform
        :type operation: Operations
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        """
        hosts_changes = {}
        successful_hosts = []
        failed_hosts = []
        skipped_hosts = []
        hosts_info = context.vc_rest_client().get_filtered_hosts_info(esxi_host_names=context.esxi_host_names)
        # Iterate over all the host_info and collect host_changes.
        overall_status = result_config[consts.STATUS]
        for host_name, host_moid in hosts_info.items():
            if host_moid:
                # TBD Make the below method _get_esxi_host_workflow_result to run as a thread task.
                logger.info(f"Invoke workflow for host {host_name}.")
                try:
                    host_result = cls._get_esxi_host_workflow_result(
                        desired_state_spec=desired_state_spec,
                        context=context,
                        operation=operation,
                        metadata_filter=metadata_filter,
                        host_moid=host_moid,
                        hostname=host_name,
                    )
                    # For remediate operation, do not add the esxi host result with no host_changes
                    if (
                        operation == Operations.REMEDIATE
                        and host_result.get(consts.STATUS) == RemediateStatus.SUCCESS
                        and not host_result.get(consts.HOST_CHANGES)
                    ):
                        continue
                    hosts_changes[host_name] = host_result
                    if hosts_changes[host_name].get(consts.STATUS) in {
                        ComplianceStatus.FAILED,
                        RemediateStatus.FAILED,
                        GetCurrentConfigurationStatus.FAILED,
                        GetCurrentConfigurationStatus.PARTIAL,
                    }:
                        failed_hosts.append(host_name)
                    elif hosts_changes[host_name].get(consts.STATUS) in {
                        ComplianceStatus.COMPLIANT,
                        RemediateStatus.SUCCESS,
                        GetCurrentConfigurationStatus.SUCCESS,
                    }:
                        successful_hosts.append(host_name)
                    elif hosts_changes[host_name].get(consts.STATUS) in {
                        ComplianceStatus.SKIPPED,
                        RemediateStatus.SKIPPED,
                        GetCurrentConfigurationStatus.SKIPPED,
                    }:
                        skipped_hosts.append(host_name)
                except Exception as e:
                    logging.error(f"Exception in host workflow for the host {host_name}: {e}")
                    failed_status = {
                        Operations.CHECK_COMPLIANCE: ComplianceStatus.FAILED,
                        Operations.REMEDIATE: RemediateStatus.FAILED,
                        Operations.GET_CURRENT: GetCurrentConfigurationStatus.FAILED,
                    }[operation]
                    hosts_changes[host_name] = {consts.STATUS: failed_status, consts.ERRORS: [str(e)]}
                    # Only overwrite if not already PARTIAL
                    if (
                        consts.STATUS not in result_config
                        or result_config.get(consts.STATUS) != GetCurrentConfigurationStatus.PARTIAL
                    ):
                        result_config[consts.STATUS] = failed_status
                    failed_hosts.append(host_name)
            else:
                skipped_status = {
                    Operations.CHECK_COMPLIANCE: ComplianceStatus.SKIPPED,
                    Operations.REMEDIATE: RemediateStatus.SKIPPED,
                    Operations.GET_CURRENT: GetCurrentConfigurationStatus.SKIPPED,
                }[operation]
                hosts_changes[host_name] = {
                    consts.STATUS: skipped_status,
                    consts.ERRORS: [f"Host '{host_name}' is not managed by this vCenter."],
                }
                skipped_hosts.append(host_name)
            # Only store SUCCESS for GET_CURRENT operation
            if (
                operation == Operations.GET_CURRENT
                and hosts_changes[host_name].get(consts.STATUS) != GetCurrentConfigurationStatus.SUCCESS
            ):
                del hosts_changes[host_name]
            if operation == Operations.CHECK_COMPLIANCE or operation == Operations.REMEDIATE:
                # Update overall status. host_status acts as control status to decide overall status for the operation
                # performed on list of hosts
                host_status = hosts_changes.get(host_name, {}).get(consts.STATUS)
                overall_status = cls._update_overall_status(
                    operation=operation.value, control_status=host_status, overall_status=overall_status
                )

        result_config[consts.RESULT] = hosts_changes
        result_config[consts.STATUS] = overall_status

        # Set message
        if failed_hosts and skipped_hosts:
            result_config[
                consts.MESSAGE
            ] = f"Operation failed for hosts - {failed_hosts}, Skipped for hosts - {skipped_hosts}"
        elif failed_hosts:
            result_config[consts.MESSAGE] = f"Operation failed for hosts - {failed_hosts}"
        elif skipped_hosts:
            result_config[consts.MESSAGE] = f"Skipped for hosts - {skipped_hosts}"

        # For GET_CURRENT operation, update the overall status based on list of failed/skipped/success hosts
        if operation == Operations.GET_CURRENT:
            if not failed_hosts:
                result_config[consts.STATUS] = GetCurrentConfigurationStatus.SUCCESS
            elif failed_hosts and successful_hosts:
                result_config[consts.STATUS] = GetCurrentConfigurationStatus.PARTIAL
            else:
                result_config[consts.STATUS] = GetCurrentConfigurationStatus.FAILED

    @classmethod
    def _get_esxi_host_workflow_result(
        cls,
        desired_state_spec: dict,
        context: EsxiContext,
        operation: Operations,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
        host_moid: str = None,
        hostname: str = None,
    ):
        """
        Get host_changes and status for the single host for the respective workflow.
        :param desired_state_spec: The input desired state spec.
        :param context: The Context that can be used by the config classes to retrieve value.
        :param operation: The operation to invoke.
        :param metadata_filter: Function used to filter controllers based on metadata.
        :param host_moid: Host MOID.
        :param hostname: ESXi hostname
        :return: Dict with keys 'STATUS' and 'HOST_CHANGES'/'HOST_RESULTS' for the provided host.
        :rtype: dict
        """
        host_ref = context.vc_vmomi_client().get_host_ref_for_moid(host_moid)
        if host_ref is None:
            raise Exception("Unable to retrieve host_ref. Not proceeding for this host")

        host_context = HostContext(
            host_ref=host_ref,
            vc_rest_client_func=context.vc_rest_client,
            vc_vmomi_client_func=context.vc_vmomi_client,
            esx_cli_client_func=context.esx_cli_client,
            hostname=hostname,
        )

        with HostnameLoggingContext(host_context.hostname):
            workflow_response = cls.operate(
                host_context,
                operation,
                input_values=desired_state_spec,
                metadata_filter=metadata_filter,
            )

        host_result = {
            consts.STATUS: workflow_response.get(consts.STATUS),
        }
        if operation == Operations.GET_CURRENT:
            host_result[consts.HOST_RESULTS] = workflow_response.get(consts.RESULT, {})
        else:
            host_result[consts.HOST_CHANGES] = workflow_response.get(consts.RESULT, {})

        if workflow_response.get(consts.MESSAGE):
            host_result[consts.MESSAGE] = workflow_response.get(consts.MESSAGE)
        return host_result
