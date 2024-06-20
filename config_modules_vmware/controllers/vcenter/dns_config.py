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


class DnsConfig(BaseController):
    """Manage DNS config with get and set methods.

    | Config Id - 1271
    | Config Title - DNS should be configured to a global value that is enforced by vCenter.

    """

    metadata = ControllerMetadata(
        name="dns",  # controller name
        path_in_schema="compliance_config.vcenter.dns",  # path in the schema to this controller's definition.
        configuration_id="1271",  # configuration id as defined in compliance kit.
        title="DNS should be configured to a global value that is enforced by vCenter.",
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

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """
        Get DNS config from vCenter.

        | Sample get call output

        .. code-block:: json

            {
              "mode": "is_static",
              "servers": ["8.8.8.8", "1.1.1.1"]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict with keys "servers" and "mode" and a list of error messages if any.
        :rtype: tuple
        """
        logger.info("Getting DNS control config for audit.")
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.DNS_URL
        errors = []
        try:
            dns_servers = vc_rest_client.get_helper(url)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            dns_servers = {"servers": [], "mode": ""}
        return dns_servers, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Sets list of servers and DNS mode.

        | Sample desired state for DNS

        .. code-block:: json

            {
              "mode": "is_static",
              "servers": ["8.8.8.8", "1.1.1.1"]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the DNS config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting DNS control config for audit.")
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + vc_consts.DNS_URL
        payload = {"mode": desired_values.get("mode"), "servers": desired_values.get("servers")}
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
        """Check compliance of current DNS configuration in vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the DNS config.
        :type desired_values: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        dns_desired_value = {"servers": desired_values.get("servers", []), "mode": desired_values.get("mode")}
        return super().check_compliance(context, desired_values=dns_desired_value)

    def remediate(self, context: BaseContext, desired_values: Dict) -> Dict:
        """Remediate DNS configuration drifts in vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the DNS config.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        dns_desired_value = {"servers": desired_values.get("servers", []), "mode": desired_values.get("mode")}
        return super().remediate(context, desired_values=dns_desired_value)
