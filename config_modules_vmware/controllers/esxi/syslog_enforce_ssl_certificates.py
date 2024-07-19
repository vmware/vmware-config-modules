# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class SyslogEnforceSslCertificates(BaseController):
    """ESXi controller to get/set/check_compliance/remediate policy for enforcing checking of SSL certificates for syslog.

    | Config Id - 1115
    | Config Title - The ESXi host must verify certificates for SSL syslog endpoints.

    """

    metadata = ControllerMetadata(
        name="syslog_enforce_ssl_certificates",  # controller name
        path_in_schema="compliance_config.esxi.syslog_enforce_ssl_certificates",
        # path in the schema to this controller's definition.
        configuration_id="1115",  # configuration id as defined in compliance kit.
        title="The ESXi host must verify certificates for SSL syslog endpoints",
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
        """Get SSL certificates enforcement policy for syslog for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of boolean value True/False and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting SSL certificates enforcement policy for syslog for esxi.")
        errors = []
        enabled = None
        try:
            enforce_ssl_certs_get_command = "system syslog config get"
            cli_output, _, _ = context.esx_cli_client().run_esx_cli_cmd(context.hostname, enforce_ssl_certs_get_command)
            logger.debug(f"cli_output is {cli_output}")
            match = re.search(r"Enforce SSLCertificates:\s*(\w+)", cli_output)
            if not match:
                err_msg = f"Unable to fetch enforce ssl certs using command esxcli {enforce_ssl_certs_get_command}"
                raise Exception(err_msg)
            else:
                enabled = match.group(1).lower() == "true"
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return enabled, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set SSL certificates enforcement policy for syslog for esxi host.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: boolean value True/False to enable/disable SSL certs checking.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting SSL certificates enforcement policy for syslog for esxi.")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            enabled_str = "true" if desired_values is True else "false"
            enforce_ssl_certs_set_command = f"system syslog config set --check-ssl-certs={enabled_str}"
            context.esx_cli_client().run_esx_cli_cmd(context.hostname, enforce_ssl_certs_set_command)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
