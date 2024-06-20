# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.nsxt_manager.ntp_config import NsxtNtpCommon
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


class NtpConfig(BaseController):
    """Manage Ntp config with get and set methods..

    | Config Id - 1401
    | Config Title - Synchronize system clocks to an authoritative time source.

    """

    metadata = ControllerMetadata(
        name="ntp",  # controller name
        path_in_schema="compliance_config.nsxt_edge.ntp",  # path in the schema to this controller's definition.
        configuration_id="1401",  # configuration id as defined in compliance kit.
        title="Configure NTP servers for the NSX-T edge.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[
            BaseContext.ProductEnum.NSXT_EDGE,
        ],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsxt_edge"],  # location where functional tests are run.
    )

    def get(self, context: BaseContext) -> Tuple[Dict, List[Any]]:
        """
        Get NTP config from NSXT edge.

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
        return NsxtNtpCommon.get_ntp(context=context)

    def set(self, context: BaseContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set NTP config in NSXT edge.
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
