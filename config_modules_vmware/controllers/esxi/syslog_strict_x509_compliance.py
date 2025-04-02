# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils import esxi_advanced_settings_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

SETTINGS_NAME = "Syslog.global.certificate.strictX509Compliance"


class SyslogStrictX509Compliance(BaseController):
    """ESXi controller to get/set/check_compliance/remediate policy for strict x509 verification for SSL syslog endpoints.

    | Config Id - 1121
    | Config Title - The ESXi host must enable strict x509 verification for SSL syslog endpoints.

    """

    metadata = ControllerMetadata(
        name="syslog_strict_x509_compliance",  # controller name
        path_in_schema="compliance_config.esxi.syslog_strict_x509_compliance",
        # path in the schema to this controller's definition.
        configuration_id="1121",  # configuration id as defined in compliance kit.
        title="The ESXi host must enable strict x509 verification for SSL syslog endpoints",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: HostContext) -> Tuple[bool, List[str]]:
        """Get SSL x509 verification policy for syslog for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of boolean value True/False and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting SSL x509 verification policy for syslog for esxi.")
        errors = []
        ssl_x509_certs_enabled = False
        try:
            result = esxi_advanced_settings_utils.invoke_advanced_option_query(context.host_ref, prefix=SETTINGS_NAME)
            ssl_x509_certs_enabled = result[0].value

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors = [str(e)]
        return ssl_x509_certs_enabled, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set SSL x509 verification policy for syslog for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: boolean value True/False to enable/disable SSL x509 verification.
        :type desired_values: bool
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting SSL x509 verification policy for syslog for esxi.")
        host_option = vim.option.OptionValue(key=SETTINGS_NAME, value=desired_values)
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxi_advanced_settings_utils.update_advanced_option(context.host_ref, host_option=host_option)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
