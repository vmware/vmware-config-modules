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


class SyslogConfig(BaseController):
    """Manage Syslog config with get and set methods.

    | Config Id - 1218
    | Config Title - The vCenter Server must be configured to send logs to a central log server.

    """

    metadata = ControllerMetadata(
        name="syslog",  # controller name
        path_in_schema="compliance_config.vcenter.syslog",  # path in the schema to this controller's definition.
        configuration_id="1218",  # configuration id as defined in compliance kit.
        title="The vCenter Server must be configured to send logs to a central log server.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Get Syslog config from vCenter.

        | sample get call output

        .. code-block:: json

            {
              "servers": [
                {
                  "hostname": "8.8.4.4",
                  "port": 90,
                  "protocol": "TLS"
                },
                {
                  "hostname": "8.8.1.8",
                  "port": 90,
                  "protocol": "TLS"
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict with key "servers" and list of error messages.
        :rtype: tuple
        """
        logger.info("Getting Syslog config.")
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.SYSLOG_URL
        errors = []
        try:
            syslog_config = vc_rest_client.get_helper(url)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            syslog_config = []
        return {"servers": syslog_config}, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set Syslog config for the audit control.

        | Sample desired state for syslog config

        .. code-block:: json

            {
              "servers": [
                {
                  "hostname": "10.0.0.250",
                  "port": 514,
                  "protocol": "TLS"
                },
                {
                  "hostname": "10.0.0.251",
                  "port": 514,
                  "protocol": "TLS"
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the Syslog config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        logger.info("Setting Syslog control config for remediation.")
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.SYSLOG_URL
        payload = {"cfg_list": desired_values.get("servers")}

        errors = []
        status = RemediateStatus.SUCCESS
        try:
            vc_rest_client.put_helper(url, body=payload, raise_for_status=True)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context, desired_values: Dict) -> Dict:
        """Check compliance of current syslog configuration in vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the syslog config.
        :type desired_values: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        syslog_desired_value = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values=syslog_desired_value)

    def remediate(self, context: BaseContext, desired_values: Dict) -> Dict:
        """Remediate syslog configuration drifts in vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the syslog config.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        syslog_desired_value = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values=syslog_desired_value)
