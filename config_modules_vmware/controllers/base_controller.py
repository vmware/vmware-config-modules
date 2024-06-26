# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import Comparator
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList

logger = LoggerAdapter(logging.getLogger(__name__))


class BaseController(ABC):
    def __init__(self):
        self.comparator_option = ComparatorOptionForList.COMPARE_AFTER_SORT
        self.instance_key = "name"

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "metadata"):
            err_str = f'Can\'t instantiate controller class "{cls.__name__}". ' f'"metadata" attribute is not defined'
            logger.error(f"Metadata not created for controller {cls.__name__}")
            raise TypeError(err_str)
        controller_metadata = getattr(cls, "metadata")
        if not isinstance(controller_metadata, ControllerMetadata) or not controller_metadata.validate():
            err_str = (
                f'Can\'t instantiate controller class "{cls.__name__}". '
                f'"metadata" attribute does not have all required fields'
            )
            logger.error(err_str)
            raise TypeError(err_str)
        return super().__init_subclass__(**kwargs)

    @abstractmethod
    def get(self, context: BaseContext, template: dict = None) -> Tuple[Any, List[str]]:
        pass

    @abstractmethod
    def set(self, context: BaseContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        pass

    def check_compliance(self, context: BaseContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance.")
        current_value, errors = self.get(context=context)

        if errors:
            if len(errors) == 1 and errors[0] == consts.SKIPPED:
                return {consts.STATUS: ComplianceStatus.SKIPPED}
            # If errors are seen during get, return "FAILED" status with errors.
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_non_compliant_configs, desired_non_compliant_configs = Comparator.get_non_compliant_configs(
            current_value, desired_values, comparator_option=self.comparator_option, instance_key=self.instance_key
        )
        if current_non_compliant_configs or desired_non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_non_compliant_configs,
                consts.DESIRED: desired_non_compliant_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: BaseContext, desired_values: Any) -> Dict:
        """Remediate current configuration drifts.

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Running remediation.")

        # Call check compliance and check for current compliance status.
        compliance_response = self.check_compliance(context=context, desired_values=desired_values)

        if (
            compliance_response.get(consts.STATUS) == ComplianceStatus.FAILED
            or compliance_response.get(consts.STATUS) == ComplianceStatus.ERROR
        ):
            # For compliance_status as "FAILED" or "ERROR", return FAILED with errors.
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: compliance_response.get(consts.ERRORS, [])}

        elif compliance_response.get(consts.STATUS) == ComplianceStatus.COMPLIANT:
            # For compliant_status as "COMPLIANT", return remediation as skipped.
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ["Control already compliant"]}

        elif compliance_response.get(consts.STATUS) == ComplianceStatus.SKIPPED:
            # For compliance_status as "SKIPPED", return remediation as SKIPPED since no remediation was performed.
            return {
                consts.STATUS: RemediateStatus.SKIPPED,
                consts.ERRORS: ["Remediation Skipped as Check compliance is SKIPPED"],
            }

        elif compliance_response.get(consts.STATUS) != ComplianceStatus.NON_COMPLIANT:
            # Raise exception for unexpected compliance status (other than FAILED, COMPLIANT, NON_COMPLIANT).
            raise Exception("Error during remediation. Unexpected compliant status found.")

        # Configs are non_compliant, call set to remediate them.
        status, errors = self.set(context=context, desired_values=desired_values)
        if not errors:
            result = {
                consts.STATUS: status,
                consts.OLD: compliance_response.get(consts.CURRENT),
                consts.NEW: compliance_response.get(consts.DESIRED),
            }
        else:
            if status == RemediateStatus.SKIPPED:
                # ADD SKIPPED RESPONSE
                result = {
                    consts.STATUS: RemediateStatus.SKIPPED,
                    consts.ERRORS: errors,
                    consts.CURRENT: compliance_response.get(consts.CURRENT),
                    consts.DESIRED: compliance_response.get(consts.DESIRED),
                }
            else:
                result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result
