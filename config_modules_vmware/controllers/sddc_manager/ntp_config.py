# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.clients.common import rest_client
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class NtpConfig(BaseController):
    """Operations for Ntp config in SDDC Manager."""

    metadata = ControllerMetadata(
        name="ntp",  # controller name
        path_in_schema="compliance_config.sddc_manager.ntp",  # path in the schema to this controller's definition.
        configuration_id="1601",  # configuration id as defined in compliance kit.
        title="SDDC Manager components must use an authoritative time source [NTP]",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.SDDC_MANAGER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: SDDCManagerContext) -> Tuple[List[Dict], List[Any]]:
        """Get list of NTP Servers from SDDC Manager.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :return: Tuple of dict with key "servers" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting NTP servers.")

        # Get using public API
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.NTP_URL

        errors = []
        try:
            ntp_servers_resp = sddc_manager_rest_client.get_helper(url)
            ntp_servers = [server["ipAddress"] for server in ntp_servers_resp.get("ntpServers", [])]
        except Exception as e:
            errors.append(str(e))
            ntp_servers = []
        return {"servers": ntp_servers}, errors

    def _set_ntp_using_local_url(self, desired_values):
        """Set NTP config in SDDC Manager using local API.

        :param desired_values: Desired values for the NTP config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            url = sddc_manager_consts.LOCAL_NTP_URL
            payload = {"ntpServers": desired_values.get("servers", [])}
            rest_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            smart_rest_client_obj = rest_client.get_smart_rest_client()
            ntp_patch_response = smart_rest_client_obj.patch(
                url=url, timeout=60, headers=rest_headers, body=json.dumps(payload)
            )
            smart_rest_client_obj.raise_for_status(ntp_patch_response, url)
        except Exception as e:
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def set(self, context, desired_values) -> Tuple[str, List[Any]]:
        """Set NTP config in SDDC Manager.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired value for the NTP config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """

        logger.info("Setting NTP control config for audit.")

        # If 'is_local' flag is not present in desired spec or is set as True, then configure using local url.
        if desired_values.get("is_local", True):
            return self._set_ntp_using_local_url(desired_values=desired_values)

        # Set using public API to propagate configuration to all components managed by SDDC-Manager
        sddc_manager_rest_client = context.sddc_manager_rest_client()
        url = sddc_manager_rest_client.get_base_url() + sddc_manager_consts.NTP_URL
        payload = {"ntpServers": [{"ipAddress": server} for server in desired_values.get("servers", [])]}
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            task_info = sddc_manager_rest_client.put_helper(url, body=payload, raise_for_status=True)
            logger.info(f'Remediation Task ID {task_info.get("id")}')
            task_status = sddc_manager_rest_client.monitor_task(task_info.get("id"))
            if not task_status:
                raise Exception(f'Remediation failed for task: {task_info.get("id")} check log for details')
        except Exception as e:
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context: SDDCManagerContext, desired_values: Dict) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: SDDCManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        ntp_desired_value = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values=ntp_desired_value)
