# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList

# Any logging should be done using a logger which is created like this.
logger = LoggerAdapter(logging.getLogger(__name__))


# Every Controller should extend the BaseController class.
# Pay attention to the docstrings formatting. They are used to autogenerate documentation.
# After writing the controller, you should run ./devops/scripts/generate_markdown_docs.sh.
# It will generate markdown documentation and put it in the api_docs directory.
class SampleController(BaseController):
    """A one line summary of the controller.

    After a blank line, any more details about the controller can be given.

    """

    # This init method is OPTIONAL.
    def __init__(self):
        """
        Based on the configuration data, one can choose different comparator using ComparatorOptionForList enum.
        Please refer Comparator Class and ComparatorOptionForList enum under utils for more details.
        BaseController class has already init method with below values but if controller wants, it can
        override those. These values are used during check_compliance/remediation.
        """
        super().__init__()
        self.comparator_option = ComparatorOptionForList.COMPARE_AFTER_SORT
        self.instance_key = "name"

    metadata = ControllerMetadata(
        name="sample_controller_name",  # controller name
        path_in_schema="compliance_config.sample_product.sample_controller_name",  # path in the schema to this controller's definition.
        configuration_id="-1",  # configuration id as defined in compliance kit.
        title="sample config title defined in compliance kit",  # controller title as defined in compliance kit.
        tags=["sample", "test"],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.DISABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.,
        type=ControllerMetadata.ControllerType.COMPLIANCE,  # controller type i.e. compliance control or whole product configuration
    )

    # This method must be implemented.
    def get(self, context):
        """One line summary of the what is retrieved.

        | Optionally, after a blank line, more details may be given. For example, how the content is retrieved or
            what format it will be in.
        | Also describe any dependencies that may exist on other configurations or external libraries.
        | Vertical bars can be used to add line blocks.
        | Below is an example of a code block for a JSON object.

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
        :type context: BaseContext
        :return: Tuple of current control value and a list of error messages if any.
            NOTE that the control value should be in the same format as the schema for this control.
        :rtype: tuple
        """
        logger.debug("Getting Sample control config.")
        # Use context to connect to product and retrieve control value.
        # The below code is only for use in the unit tests.
        # It uses a VC Context for an example but does not call actual APIs.
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + "/test_url/sample_control"
        errors = []
        try:
            sample_control = vc_rest_client.get_helper(url)
        except Exception as e:
            errors.append(str(e))
            sample_control = -1
        return sample_control, errors

    # This method must be implemented.
    def set(self, context, desired_values):
        """One line summary of what is being set.

        More details about what the expected desired_values being passed in should be. Maybe an example if appropriate.
        This should also describe any pre-requisite or post-requisite required for setting this value.
        i.e. if a host needs to be in maintenance mode first, or needs to be restarted after.

        :param context: The type of context, i.e. VcenterContext.
        :type context: BaseContext
        :param desired_values: The value that is to be set (dict, string, int, etc.).
        :type desired_values: The expected type
        :return: Tuple of a status (from the RemediateStatus enum) and a list of errors encountered if any.
        :rtype: tuple
        """
        logger.debug("Setting sample control to new value.")
        # Use context to connect to product and set control value.
        # The below code is only for use in the unit tests.
        # It uses a VC Context for an example but does not call actual APIs.
        vc_rest_client = context.vc_rest_client()
        url = vc_rest_client.get_base_url() + "/test_url/sample_control"
        payload = {"sample_control": 123}
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            vc_rest_client.put_helper(url, body=payload, raise_for_status=True)
        except Exception as e:
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context, desired_values) -> Dict:
        """Check compliance of current configuration against provided desired values.

        This function has a default implementation in the BaseController. If needed, you can overwrite it with your
        own implementation. It should check the current value of the control against the provided desired_values and
        return a dict with key "status" and a status from the ComplianceStatus enum. If
        the control is NON_COMPLIANT, it should also include keys "current" and "desired" with their respective values.
        If the operation failed, it should include a key "errors" and a list of the error messages.

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired values for this control.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Checking compliance.")
        # do the compliance check.
        current_value, errors = self.get(context=context)
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        if current_value == desired_values:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        else:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_value,
                consts.DESIRED: desired_values,
            }
        return result

    def remediate(self, context, desired_values) -> Dict:
        """Remediate current configuration drifts.

        This function has a default implementation in the BaseController. If needed, you can overwrite it with your
        own implementation. It should run check compliance and set it to the desired value if it is non-compliant.
        This function should return a dict with key "status" and a status from the RemediateStatus enum.
        If the value was changed it should also include keys "old" and "new" with their respective values.
        If the operation failed, it should include a key "errors" and a list of the error messages.

        :param context: Product context instance.
        :type context: BaseContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        logger.debug("Running remediation")

        # Call check compliance and check for current compliance status.
        compliance_response = self.check_compliance(context=context, desired_values=desired_values)

        if compliance_response.get(consts.STATUS) == ComplianceStatus.FAILED:
            # For compliance_status as "FAILED", return FAILED with errors.
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: compliance_response.get(consts.ERRORS, [])}

        elif compliance_response.get(consts.STATUS) == ComplianceStatus.COMPLIANT:
            # For compliant case, return SKIPPED.
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

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
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        return result
