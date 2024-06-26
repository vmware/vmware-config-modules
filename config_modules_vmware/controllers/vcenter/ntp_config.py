# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class NtpConfig(BaseController):
    """Manage Ntp config with get and set methods.

    | Config Id - 1246
    | Config Title - The system must configure NTP time synchronization.
    """

    metadata = ControllerMetadata(
        name="ntp",  # controller name
        path_in_schema="compliance_config.vcenter.ntp",  # path in the schema to this controller's definition.
        configuration_id="1246",  # configuration id as defined in compliance kit.
        title="The system must configure NTP time synchronization.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def _get_ntp_mode(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Get NTP mode.
        Supported values - [DISABLED, NTP, HOST].

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict with key "mode" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting NTP mode.")
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.TIMESYNC_URL

        errors = []
        try:
            ntp_mode = vc_rest_client.get_helper(url)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            ntp_mode = ""
        return ntp_mode, errors

    def _get_ntp_servers(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Get ntp servers.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict with key "servers" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting NTP servers.")
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.NTP_URL

        errors = []
        try:
            ntp_servers = vc_rest_client.get_helper(url)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            ntp_servers = []
        return ntp_servers, errors

    def _set_ntp_mode(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set NTP mode.
        Supported values - [DISABLED, NTP, HOST].
        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the NTP mode. Dict with key "mode".
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        logger.info("Setting NTP mode.")
        vc_rest_client = context.vc_rest_client()
        payload = {"mode": desired_values.get("mode")}
        url = vc_rest_client.get_base_url() + vc_consts.TIMESYNC_URL

        errors = []
        status = RemediateStatus.SUCCESS
        try:
            vc_rest_client.put_helper(url, body=payload, raise_for_status=True)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def _set_ntp_servers(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set ntp servers.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the NTP servers. Dict with key "servers".
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        logger.info("Setting NTP servers.")
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.NTP_URL
        payload = {"servers": desired_values.get("servers")}

        errors = []
        status = RemediateStatus.SUCCESS
        try:
            vc_rest_client.put_helper(url, body=payload, raise_for_status=True)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Get NTP config from vCenter.

        | Sample get output

        .. code-block:: json

            {
              "mode": "NTP",
              "servers": ["time.vmware.com", "time.google.com"]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict with key "servers", "mode" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting NTP config")
        errors = []
        ntp_servers, servers_errors = self._get_ntp_servers(context)
        errors.extend(servers_errors)

        ntp_mode, mode_errors = self._get_ntp_mode(context)
        errors.extend(mode_errors)
        return {"mode": ntp_mode, "servers": ntp_servers}, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set NTP config in vCenter.

        | Sample desired state for NTP.

        .. code-block:: json

            {
              "mode": "NTP",
              "servers": ["time.vmware.com", "time.google.com"]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired value for the NTP config. Dict with keys "servers" and "mode".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting NTP control config for audit.")
        errors = []

        server_status, err = self._set_ntp_servers(context, desired_values)
        logger.info(f"server_status: '{server_status}'")
        errors.extend(err)

        mode_status, err = self._set_ntp_mode(context, desired_values)
        logger.info(f"mode_status: '{mode_status}'")
        errors.extend(err)

        status = RemediateStatus.SUCCESS
        if errors:
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context, desired_values: Dict) -> Dict:
        """Check compliance of current NTP configuration in vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for NTP config.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        ntp_desired_value = {"servers": desired_values.get("servers", []), "mode": desired_values.get("mode")}
        return super().check_compliance(context, desired_values=ntp_desired_value)

    def remediate(self, context, desired_values: Dict) -> Dict:
        """Remediate configuration drifts for NTP config in vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for NTP config.
        :type desired_values: dict
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        ntp_desired_value = {"servers": desired_values.get("servers", []), "mode": desired_values.get("mode")}
        return super().remediate(context, desired_values=ntp_desired_value)
