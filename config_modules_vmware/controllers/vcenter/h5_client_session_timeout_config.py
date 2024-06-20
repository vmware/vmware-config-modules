# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import Any
from typing import List
from typing import Tuple
from typing import Union

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

CMD_TIMEOUT = 10
GREP_CMD = "/usr/bin/grep"
SED_CMD = "/usr/bin/sed"
PROPERTY_FILE_PATH = "/etc/vmware/vsphere-ui/webclient.properties"
SESSION_TIMEOUT_GREP_PATTERN = r"^session\.timeout.*="
SESSION_TIMEOUT_VALUE = r"session\.timeout = {}"
SED_REPLACE_PATTERN = r"/^session\.timeout/s/=[[:space:]]*[^[:space:]]*/="
GREP_GET_PROPERTY_CMD = f"{GREP_CMD} -E {SESSION_TIMEOUT_GREP_PATTERN} {PROPERTY_FILE_PATH}"
SED_ADD_CMD = f"{SED_CMD} -i '$ a {SESSION_TIMEOUT_VALUE}' {PROPERTY_FILE_PATH}"


class H5ClientSessionTimeoutConfig(BaseController):
    """Manage vCenter H5 client idle session timeout with get and set methods.

    | Config Id - 422
    | Config Title - The vCenter Server must terminate management sessions after certain period of inactivity.

    """

    metadata = ControllerMetadata(
        name="h5_client_session_timeout",  # controller name
        path_in_schema="compliance_config.vcenter.h5_client_session_timeout",  # path in the schema to this controller's definition.
        configuration_id="422",  # configuration id as defined in compliance kit.
        title="The vCenter Server must terminate management sessions after certain period of inactivity.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["vcenter"],  # location where functional tests are run.
    )

    def get(self, context: VcenterContext) -> Tuple[int, List[str]]:
        """Get H5 client session timeout from vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of session timeout value as int and a list of error messages if any.
        :rtype: tuple
        """
        logger.info("Getting H5 client session timeout for audit.")
        errors = []
        result = None
        try:
            prop_value = self.__get_session_timeout_value()
            if prop_value is not None:
                result = prop_value
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: int) -> Tuple[str, List[Any]]:
        """Sets H5 client session timeout on vCenter.

        | STIG Recommended value: 10 Minutes; default: 120 minutes.
        | Note: For session timeout setting to take effect a restart of the vsphere-ui service is required.
            Please note that service restart is not included as part of this remediation procedure.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired value in minutes for the H5 client session timeout.
        :type desired_values: int
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting H5 client session timeout")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            _update_successful = self.__apply_vcsa_session_timeout_value(desired_value=desired_values)
            if not _update_successful:
                status = RemediateStatus.FAILED
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    @staticmethod
    def __get_session_timeout_value() -> Union[int, None]:
        """Check if the session.timeout property exists in prop file and retrieve value.

        :return: value of property if found in prop file else None
        """
        output_str, _, ret_code = utils.run_shell_cmd(
            command=GREP_GET_PROPERTY_CMD,
            timeout=CMD_TIMEOUT,
            raise_on_non_zero=False,
        )  # nosec
        if ret_code != 0:
            logger.info(f"Error fetching the property {SESSION_TIMEOUT_GREP_PATTERN} from {PROPERTY_FILE_PATH}")
            return None

        session_timeout = None
        # Extract timeout value
        match = re.search(r"session\.timeout\s*=\s*(\d+)", output_str.strip())

        if match:
            session_timeout = int(match.group(1))
        return session_timeout

    @staticmethod
    def __apply_vcsa_session_timeout_value(desired_value: int) -> bool:
        """Apply VCSA session timeout value for H5 client.

        :param: desired_value: Desired value for session timeout
        :type desired_value: int
        :return: True if property update is successful, False otherwise
        """
        current_timeout_value = H5ClientSessionTimeoutConfig.__get_session_timeout_value()

        if current_timeout_value is not None:
            logger.info(f"current timeout value  {current_timeout_value}")

            if current_timeout_value == desired_value:
                logger.info(f"Session timeout is already at desired value {current_timeout_value}")
                return True
            else:
                # Update session.timeout
                H5ClientSessionTimeoutConfig.__replace_property(desired_value)
        else:
            # We assume session.timeout property is missing in prop file.
            H5ClientSessionTimeoutConfig.__add_new_property(desired_value)

        # check if property addition/update was successful
        updated_timeout_value = H5ClientSessionTimeoutConfig.__get_session_timeout_value()

        if updated_timeout_value is not None and updated_timeout_value == desired_value:
            logger.info(f"Successfully updated session timeout value to {updated_timeout_value}")
            return True
        else:
            logger.info(f"Failed to updated session.timeout property in {PROPERTY_FILE_PATH}")
            return False

    @staticmethod
    def __replace_property(desired_value: int) -> None:
        """Replace session timeout property using SED command.

        :param desired_value: Desired value for session timeout
        :type desired_value: int
        :return: None
        """
        sed_replace_command = rf"{SED_CMD} -i '{SED_REPLACE_PATTERN} {desired_value}/'" f" {PROPERTY_FILE_PATH}"
        utils.run_shell_cmd(command=sed_replace_command, timeout=CMD_TIMEOUT)  # nosec
        logger.info(f"Successfully replaced session timeout to {desired_value}")

    @staticmethod
    def __add_new_property(desired_value: int) -> None:
        """Add new property using SED command.

        :param desired_value: desired value for session timeout
        :type desired_value: :class: `int`
        :return: None
        """
        add_sed_cmd = SED_ADD_CMD.format(desired_value)
        utils.run_shell_cmd(command=add_sed_cmd, timeout=CMD_TIMEOUT)  # nosec
        logger.info(f"Successfully added session timeout property with value {desired_value}")
