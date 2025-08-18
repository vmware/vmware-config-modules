import json
import logging
from typing import Dict, Tuple, List, Any

import requests

from config_modules_vmware.framework.auth.contexts.vro_context import VroContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

class SyslogConfig(BaseController):
    """Manage SYSLOG config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for VRO SYSLOG control

    """

    metadata = ControllerMetadata(
        name="syslog",  # controller name
        path_in_schema="compliance_config.vro.syslog",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for VRO SYSLOG control",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[VroContext.ProductEnum.VRO],  # product from enum in VroContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    http_headers = None

    @staticmethod
    def _update_syslog(hostname: str, port: int) -> bool:
        """
        Add SYSLOG server.
        :param server: SYSLOG server.
        :type server: str
        :return: True
        :rtype: bool
        """

        command = "vracli vrli set {hostname}:{port} --force".format(hostname=hostname, port=port) 
        logger.info(f"update syslog: {command}")
        utils.run_shell_cmd(command)
        return True

    @staticmethod
    def __disable_configs():
        cmd_text = "vracli vrli unset"  
        logger.info("running command: " + cmd_text)

        cmd_response = utils.run_shell_cmd(cmd_text)
        logger.info("cmd_response: " + str(cmd_response))

        return cmd_response

    def get(self, context: VroContext) -> Tuple[Dict, List[Any]]:
        """
        Get SYSLOG config from Vro.

        | Sample get output

        .. code-block:: json

            {
              "syslog": {"hostName":"fqdn","portNumber":"9543","protocol":"CFAPI"}
            }

        :param context: VRO context
        :type context: VroContext
        :return: Tuple of Dict containing syslog servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting SYSLOG syslog.")
        errors = []
        command_output = ""
        error = ""
        ret_code = ""
        command_output = {"hostname":"","port":0}
        try:
            command_output, error, ret_code = utils.run_shell_cmd('vracli vrli')
            #command: str, timeout: int = None, raise_on_non_zero: bool = True, input_to_stdin: str = None, env: dict = None
            if (command_output == "No vRLI integration configured"):
                command_output = {"hostname":"","port":0}
            else:
                output_json = json.loads(command_output)
                command_output = {"hostname":output_json["host"],"port":output_json["port"]}

            syslog_servers = [command_output]
            logger.info(f"syslog_servers: {syslog_servers}")
        except Exception as e:
            logger.exception(f"Exception retrieving syslog values - {e}")
            #errors.append(str(e))
            logger.info(f"***ret_code: {ret_code}***")
            command_output = {"hostname":"","port":0}
            syslog_servers = [command_output]
            #syslog_servers = []
        return {"servers": syslog_servers}, errors

    def check_compliance(self, context: VroContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: VRO product context instance.
        :type context: VroContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # vro only needs servers for SYSLOG control
        # protocol is not set in the vrli integration for vro.  removing from the comparision
        desired_value = {"hostname":"","port":0}
        desired_values = desired_values.get("servers", [])[0]
        logger.info(f"desired_values: {desired_values}")
        desired_value = {"hostname":desired_values["hostname"],"port":desired_values["port"]}
        desired_values = {"servers": [desired_value]}
        return super().check_compliance(context, desired_values)

    def set(self, context: VroContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set SYSLOG config in VRO.
        This will delete any existing SYSLOG entries and create the new desired ones as each SYSLOG entry requires a unique name associated with it.

        | Sample desired state for SYSLOG.

        .. code-block:: json

            {
              "syslog": {"hostName":"fqdn","portNumber":"9543","protocol":"CFAPI"}
            }

        :param context: vRO context instance.
        :type context: VroContext
        :param desired_values: Desired value for the SYSLOG config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting SYSLOG control config for audit.")
        errors = []
        try:
            current_syslog_servers, get_errors = self.get(context)
            if get_errors:
                raise Exception(f"Exception getting current SYSLOG servers: {get_errors[0]}")

            current_syslog_servers = current_syslog_servers.get("servers", [])

            desired_value = {"hostname":"","port":0}
            desired_syslog_server = desired_values.get("servers", [])[0]
            desired_syslog_servers = [{"hostname":desired_syslog_server["hostname"],"port":desired_syslog_server["port"]}]

            logger.info(f"Current VRO SYSLOG servers: {current_syslog_servers}")
            logger.info(f"Desired VRO SYSLOG servers: {desired_syslog_servers}")

            if desired_syslog_servers != "":
                control_server_name = desired_syslog_servers[0]["hostname"].lower()
                control_port = desired_syslog_servers[0]["port"]
                self.__disable_configs()
                self._update_syslog(control_server_name, control_port)
            elif desired_syslog_servers == "":
                self.__disable_configs()

            if self.check_compliance(context, desired_values).get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Failed to update SYSLOG servers")

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting syslog value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: VroContext, desired_values: Any) -> Dict:
        """Remediate current SYSLOG configuration drifts.

        :param context: VRO context instance.
        :type context: VroContext
        :param desired_values: Desired values for SYSLOG control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # vro only needs servers for SYSLOG control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
