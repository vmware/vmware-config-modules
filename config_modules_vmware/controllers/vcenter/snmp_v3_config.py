import logging
import re
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

# Timeouts
CMD_TIMEOUT = 10
# Commands
APPLIANCE_SHELL_CMD_PREFIX = "/bin/appliancesh --connect {}:'{}'@localhost -c "
SNMP_GET_CMD = "snmp.get"
ENABLE_SNMP_CMD = "snmp.enable"
DISABLE_SNMP_CMD = "snmp.disable"
SNMP_SET_CMD = "snmp.set --{} {}"
# Regex patterns
SNMP_FIELDS_TO_CHECK_PATTERN = r"(Enable|Authentication|Privacy):\s*(.+)"
# Keys
PRIVACY = "privacy"
AUTHENTICATION = "authentication"
ENABLE = "enable"


class SNMPv3SecurityPolicy(BaseController):
    """Manage vCenter SNMP v3 security config with get and set methods.

    | Config Id - 1222
    | Config Title - The vCenter server must enforce SNMPv3 security features where SNMP is required.
    """

    metadata = ControllerMetadata(
        name="snmp_v3",  # controller name
        path_in_schema="compliance_config.vcenter.snmp_v3",  # path in the schema to this controller's definition.
        configuration_id="1222",  # configuration id as defined in compliance kit.
        title="The vCenter server must enforce SNMPv3 security features where SNMP is required.",
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

    def get(self, context: VcenterContext) -> Tuple[dict, List[Any]]:
        """Get SNMP v3 security config.

        | Sample get call output:

        .. code-block:: json

            {
              "enable": true,
              "authentication": "SHA1",  # none, SHA1, SHA256, SHA384, SHA512
              "privacy": "AES128"  # none, AES128, AES192, AES256.
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of dict and a list of error messages if any.
        :rtype: tuple
        """
        logger.info("Getting SNMP v3 config from vCenter")
        result = None
        errors = []
        try:
            result = self.__get_snmp_config(context)
            if not result:
                raise Exception("Unable to fetch SNMP config")
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """Sets SNMP v3 security config. Enables/disables configuration and sets privacy and authentication protocols.

        | If SNMP is enabled, recommendation is to configure Authentication as SHA1 and Privacy as AES128;
            if SNMP is disabled, consider the system compliant.

        | Sample desired state for SNMP security config

        .. code-block:: json

            {
              "enable": true,
              "authentication": "SHA1",  # none, SHA1, SHA256, SHA384, SHA512
              "privacy": "AES128"  # none, AES128, AES192, AES256.
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the DNS config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting SNMP config")
        errors = []
        status = RemediateStatus.SUCCESS

        try:
            self.__apply_snmp_config(context, desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED

        return status, errors

    @staticmethod
    def __get_snmp_config(context: VcenterContext) -> Dict:
        """Get SNMP security config.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: SNMP security config as Dict
        :rtype: Dict
        """
        appliancesh_cmd_prefix = APPLIANCE_SHELL_CMD_PREFIX.format(context._username, context._password)
        snmp_get_cmd = appliancesh_cmd_prefix + SNMP_GET_CMD

        out, _, _ = utils.run_shell_cmd(command=snmp_get_cmd, timeout=CMD_TIMEOUT)

        snmp_config = {}
        for match in re.finditer(SNMP_FIELDS_TO_CHECK_PATTERN, out):
            if match.groups():
                key, value = match.groups()
                key = key.lower().strip()
                if key == ENABLE:
                    value = value.strip().lower() == "true"
                snmp_config[key] = value

        logger.info(f"SNMP config: {snmp_config}")
        return snmp_config

    @staticmethod
    def __apply_snmp_config(context: VcenterContext, desired_values: dict) -> None:
        """Applies SNMP configuration based on desired values.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired state for SNMP config.
        :type desired_values: dict
        """
        enable_snmp_config = desired_values.get(ENABLE)
        privacy_algorithm = desired_values.get(PRIVACY)
        authentication_algorithm = desired_values.get(AUTHENTICATION)

        if enable_snmp_config:
            SNMPv3SecurityPolicy.__set_snmp_config(context, ENABLE_SNMP_CMD)

            snmp_set_authentication_algorithm_cmd = SNMP_SET_CMD.format(AUTHENTICATION, authentication_algorithm)
            SNMPv3SecurityPolicy.__set_snmp_config(context, snmp_set_authentication_algorithm_cmd)

            snmp_set_privacy_algorithm_cmd = SNMP_SET_CMD.format(PRIVACY, privacy_algorithm)
            SNMPv3SecurityPolicy.__set_snmp_config(context, snmp_set_privacy_algorithm_cmd)
        else:
            SNMPv3SecurityPolicy.__set_snmp_config(context, DISABLE_SNMP_CMD)

    @staticmethod
    def __set_snmp_config(context: VcenterContext, snmp_cmd: str):
        """Logs into vCenter appliance shell and sets SNMP config property.

        :param context: Product context instance.
        :type context: VcenterContext
        :param snmp_cmd: SNMP command to execute
        :type snmp_cmd: str
        :return: None
        """
        appliancesh_cmd_prefix = APPLIANCE_SHELL_CMD_PREFIX.format(context._username, context._password)
        set_snmp_cmd = appliancesh_cmd_prefix + f'"{snmp_cmd}"'
        utils.run_shell_cmd(command=set_snmp_cmd, timeout=CMD_TIMEOUT)
