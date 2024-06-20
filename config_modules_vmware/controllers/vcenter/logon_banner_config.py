# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import os
import re
import tempfile
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

LOGON_BANNER_FILE = "logon_banner.txt"
LOGON_BANNER_TITLE = "logon_banner_title"
LOGON_BANNER_CONTENT = "logon_banner_content"
LOGON_BANNER_CHECKBOX = "checkbox_enabled"
VC_SSO_CONFIG_CMD_GET_LOGON_BANNER = "/opt/vmware/bin/sso-config.sh -print_logon_banner"
VC_SSO_CONFIG_CMD_SET_LOGON_BANNER = (
    '/opt/vmware/bin/sso-config.sh -set_logon_banner -title "{title}" {file} -enable_checkbox {checkbox}'
)


class LogonBannerConfig(BaseController):
    """
    Class for logon banner config with get and set methods.

    | Config Id - 1209
    | Config Title - Configure a logon message

    """

    metadata = ControllerMetadata(
        name="logon_banner_config",  # controller name
        path_in_schema="compliance_config.vcenter.logon_banner_config",  # path in the schema to this controller's definition.
        configuration_id="1209",  # configuration id as defined in compliance kit.
        title="Configure a logon message",
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

    def __parse_logon_banner(self, output):
        # extract Logon Banner Title
        title_match = re.search(r"Logon Banner Title:\s*(.*)", output)
        logon_banner_title = title_match.group(1) if title_match else None

        # extract Logon Banner Content
        # 1). if contens are between double ", use pattern 1 to extract the content and remove ";
        # 2). if contents are not between double ", extract the content until we see Checkbox enabled.
        pattern = r'Logon Banner Content:\s*"([^"]*)"|Logon Banner Content:(.*?)(?=Checkbox enabled :)'
        content_match = re.search(pattern, output, re.DOTALL)
        if content_match:
            logon_banner_content = (
                content_match.group(1).strip() if content_match.group(1) else content_match.group(2).strip()
            )
        else:
            logon_banner_content = None

        # extract Checkbox enabled
        checkbox_match = re.search(r"Checkbox enabled : (.*)", output)
        checkbox_enabled = checkbox_match.group(1).strip() if checkbox_match else None
        checkbox_bool_value = True if checkbox_enabled == "true" else False

        return {
            LOGON_BANNER_TITLE: logon_banner_title,
            LOGON_BANNER_CONTENT: logon_banner_content,
            LOGON_BANNER_CHECKBOX: checkbox_bool_value,
        }

    def get(self, context: VcenterContext) -> Tuple[Dict, List[Any]]:
        """
        Function to get logon banner details of vcenter server for audit.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Details of the current logon banner
        :rtype: tuple
        """
        logger.info("Getting logon banner for audit.")
        errors = []
        result = {}
        vc_sso_config_cmd_get_logon_banner = VC_SSO_CONFIG_CMD_GET_LOGON_BANNER
        try:
            command_output, _, _ = utils.run_shell_cmd(vc_sso_config_cmd_get_logon_banner)
            result = self.__parse_logon_banner(command_output)
        except Exception as e:
            logger.exception(f"Unable to fetch logon banner details {e}")
            errors.append(str(e))

        return result, errors

    def __format_content(self, desired_values):
        desired_values[LOGON_BANNER_CONTENT] = desired_values[LOGON_BANNER_CONTENT].replace("\\n", "\n")
        return desired_values

    def set(self, context: VcenterContext, desired_values) -> Tuple:
        """
        Set to replace logon banner with desired config.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the vcenter logon banner
        :type desired_config: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: tuple
        """
        errors = []
        title = desired_values.get(LOGON_BANNER_TITLE)
        content = desired_values.get(LOGON_BANNER_CONTENT)
        checkbox = desired_values.get(LOGON_BANNER_CHECKBOX)
        checkbox_value = "Y" if checkbox else "N"
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                logon_banner_file = os.path.join(temp_dir, LOGON_BANNER_FILE)
                # open the file in the temporary directory
                with open(logon_banner_file, "w", encoding="UTF-8") as f:
                    # put the content in logon banner file
                    f.write('"{}"\n'.format(content))

                vc_sso_config_cmd_set_logon_banner = VC_SSO_CONFIG_CMD_SET_LOGON_BANNER.format(
                    title=title, file=logon_banner_file, checkbox=checkbox_value
                )
                _, _, _ = utils.run_shell_cmd(vc_sso_config_cmd_set_logon_banner)
            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Unable to fetch logon banner details {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED

        return status, errors

    def check_compliance(self, context, desired_values) -> Dict:
        """
        Check compliance of logon banner in vCenter server. Customer desired logon message need to
        be provided as shown in the below sample format.

        | Sample desired_values spec

        .. code-block:: json

            {
                "logon_banner_title":
                    "vCenter Server Managed by SDDC Manager",
                "logon_banner_content":
                    "This vCenter Server is managed by SDDC Manager (sddc-manager.vrack.vsphere.local).
                     Making modifications directly in vCenter Server may break SDDC Manager workflows.
                     Please consult the product documentation before making changes through the vSphere Client.",
                "checkbox_enabled": True
            }

        :param context: Product context instance.
        :param desired_values: Desired value for the logon banner.
        :return: Dict of status and current/desired value or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance")
        desired_values = self.__format_content(desired_values)
        return super().check_compliance(context, desired_values)

    def remediate(self, context, desired_values) -> Dict:
        """
        Replace logon banner with the one in desired value.

        :param context: Product context instance.
        :param desired_values: Desired value for the logon banner.
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        """
        logger.info("Running remediation")
        desired_values = self.__format_content(desired_values)
        return super().remediate(context, desired_values)
