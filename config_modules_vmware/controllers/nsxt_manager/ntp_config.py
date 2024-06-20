# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))


class NsxtNtpCommon:
    """Manage Ntp config with get and set methods."""

    @staticmethod
    def add_ntp(server: str) -> bool:
        """
        Add NTP server.
        :param server: NTP server.
        :type server: str
        :return: True
        :rtype: bool
        """
        logger.info(f"Adding ntp server {server}")
        utils.run_shell_cmd(f"su -c 'set ntp-server {server}' admin")
        return True

    @staticmethod
    def del_ntp(server: str) -> bool:
        """
        Delete NTP server
        :param server: NTP server.
        :type server: str
        :return: True
        :rtype: bool
        """
        logger.info(f"Deleting ntp server {server}")
        utils.run_shell_cmd(f"su -c 'del ntp-server {server}' admin")
        return True

    @staticmethod
    def set_ntp(context: BaseContext, desired_values: Dict) -> None:
        """
        Set NTP config in NSXT.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for NTP.

        .. code-block:: json

            {
              "servers": ["time.vmware.com", "time.google.com"]
            }

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired value for the NTP config. Dict with keys "servers".
        :raises Exception: If there is an exception when trying to get NTP
        """
        logger.info(f"Setting NTP control config for {context.product_category.value}.")
        current_ntp_servers, get_errors = NsxtNtpCommon.get_ntp(context)
        if get_errors:
            raise Exception(f"Exception getting current NTP servers: {get_errors[0]}")

        current_ntp_servers = current_ntp_servers.get("servers", [])
        desired_ntp_servers = desired_values.get("servers", [])

        logger.debug(f"Current NTP servers: {current_ntp_servers}")
        logger.debug(f"Desired NTP servers: {desired_ntp_servers}")

        for ntp_server in set(desired_ntp_servers) - set(current_ntp_servers):
            NsxtNtpCommon.add_ntp(ntp_server)

        for ntp_server in set(current_ntp_servers) - set(desired_ntp_servers):
            NsxtNtpCommon.del_ntp(ntp_server)
        return None

    @staticmethod
    def get_ntp(context):
        logger.info(f"Getting NTP servers for {context.product_category.value}")
        errors = []
        try:
            command_output = utils.run_shell_cmd("su -c 'get ntp-servers' admin")[0]
            ntp_servers = list(command_output.strip().split("\n"))
        except Exception as e:
            logger.exception(f"Exception retrieving ntp value - {e}")
            errors.append(str(e))
            ntp_servers = []
        return {"servers": ntp_servers}, errors


class NtpConfig(BaseController):
    """Manage Ntp config with get and set methods.

    | Config Id - 1401
    | Config Title - Synchronize system clocks to an authoritative time source.

    """

    metadata = ControllerMetadata(
        name="ntp",  # controller name
        path_in_schema="compliance_config.nsxt_manager.ntp",  # path in the schema to this controller's definition.
        configuration_id="1401",  # configuration id as defined in compliance kit.
        title="Configure NTP servers for the NSX-T manager.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[
            BaseContext.ProductEnum.NSXT_MANAGER,
        ],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsxt_manager"],  # location where functional tests are run.
    )

    def get(self, context: BaseContext) -> Tuple[Dict, List[Any]]:
        """
        Get NTP config from NSXT manager.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["time.vmware.com", "time.google.com"]
            }

        :param context: BaseContext, since this controller doesn't require product specific context.
        :type context: BaseContext
        :return: Tuple of Dict containing ntp servers and a list of error messages.
        :rtype: Tuple
        """
        return NsxtNtpCommon.get_ntp(context)

    def set(self, context: BaseContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set NTP config in NSXT manager.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for NTP.

        .. code-block:: json

            {
              "servers": ["time.vmware.com", "time.google.com"]
            }

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired value for the NTP config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting NTP control config for audit.")
        errors = []
        try:
            NsxtNtpCommon.set_ntp(context, desired_values)
            if self.check_compliance(context, desired_values).get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Failed to update NTP servers")
            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting ntp value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors
