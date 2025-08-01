import json
import logging
from typing import Dict, Tuple, List, Any

import requests
import os.path

from config_modules_vmware.framework.auth.contexts.vrli_context import VrliContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

class DnsConfig(BaseController):
    """Manage DNS config with get and set methods.

    | Config Id - 0000
    | Config Title - Placeholder title for Vrli DNS control

    """

    metadata = ControllerMetadata(
        name="dns",  # controller name
        path_in_schema="compliance_config.vrli.dns",  # path in the schema to this controller's definition.
        configuration_id="0",  # configuration id as defined in compliance kit.
        title="Placeholder title for VRLI DNS control",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[VrliContext.ProductEnum.VRLI],  # product from enum in VrliContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    http_headers = None

    @staticmethod
    def _check_older_vrli_version() -> bool:
        try:
            return os.path.isfile('/opt/vmware/share/vami/vami_set_dns')

        except Exception as e:
            logger.exception(f"Exception retrieving dns value - {e}")
            errors.append(str(e))
            return False

        return False

    def get(self, context: VrliContext) -> Tuple[Dict, List[Any]]:
        """
        Get DNS config from Vrli.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: Vrli context
        :type context: VrliContext
        :return: Tuple of Dict containing dns servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting DNS servers.")
        errors = []
        try:
            dns_name_array = []
            command_output = utils.run_shell_cmd("resolvectl status")[0]
            logger.info("dns_config: command_output: " + command_output)
            response_lines = command_output.split("\n")
            dns_line = False
            older_vrli_version = self._check_older_vrli_version()
            for response_line in response_lines:
                if older_vrli_version:
                    if "DNS Servers: " in response_line:
                        dns_line = True
                        dns_server = response_line.split(": ")[1].strip().replace("'", '"')
                        dns_name_array.append(dns_server)
                    elif dns_line is True:
                        dns_server = response_line.strip().replace("'", '"')
                        dns_name_array.append(dns_server)
                        break
                else:
                    if "DNS Servers: " in response_line:
                        dns_line = True
                        dns_names = response_line.split(": ")[1].split(" ")
                        for dns_name in dns_names:
                            if dns_name:
                                dns_name_array.append(dns_name.strip().replace("'", '"'))
                        break

                    
        except Exception as e:
            logger.exception(f"Exception retrieving dns value - {e}")
            errors.append(str(e))
            dns_name_array = []

        return {"servers": dns_name_array}, errors

    def check_compliance(self, context: VrliContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: VRLI product context instance.
        :type context: VrliContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # vrli only needs servers for DNS control
        desired_servers = desired_values.get("servers", [])
        logger.info(f"desired_values.get {desired_servers}")
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().check_compliance(context, desired_values)

    def set(self, context: VrliContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set DNS config in VRLI.
        This will delete any existing DNS entries and create the new desired ones as each DNS entry requires a unique name associated with it.

        | Sample desired state for DNS.

        .. code-block:: json

            {
              "servers": ["8.8.8.8", "4.4.4.4"]
            }

        :param context: VRLI context instance.
        :type context: VrliContext
        :param desired_values: Desired value for the DNS config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting DNS control config for audit.")
        errors = []
        status = RemediateStatus.SUCCESS
        dns_string = ""
        command_output = ""
        try:
            desired_values = desired_values.get("servers", [])
            dns_string = " ".join(desired_values)

            domain = context.hostname.partition(".")[2]

            #if vrli version is older than 8.14
            if self._check_older_vrli_version():
                command = f"/opt/vmware/share/vami/vami_set_dns -d {domain} -s {domain} {dns_string}"
                logger.info(f"running command: {command}")
                command_output = utils.run_shell_cmd(command)[0]
                logger.info("dns_config: command_output: " + command_output)
            else:
                utils.run_shell_cmd(f"cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.bak")
                utils.run_shell_cmd(f"cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.temp")

                fileArray = open("/etc/systemd/resolved.conf", "r")

                with open("/etc/systemd/resolved.conf", "r") as f1:
                    lines = f1.readlines()
                with open("/etc/systemd/resolved.conf.temp", "w") as f2:
                    for line in lines:
                        if line.startswith("DNS="):  
                            f2.write(f"DNS={dns_string}\n")  
                        else:
                            f2.write(line)
                    f2.close()
                    f1.close()

                #update live file with new file
                utils.run_shell_cmd(f"cp -rf /etc/systemd/resolved.conf.temp /etc/systemd/resolved.conf")                    

                utils.run_shell_cmd(f"systemctl restart systemd-resolved")

                command_output = utils.run_shell_cmd("systemctl status systemd-resolved")[0]
                logger.info(f"command output from systemd-resolved status: {command_output}")

                success_log_strings = ["Started Network Name Resolution."]

                success = False
                for success_log_string in success_log_strings:
                    if success_log_string in command_output:
                        logger.info(f"systemd-resolved service has been restarted successfully.")
                        success = True

                if not success:
                    logger.info(f"systemd-resolved service has failed to restart")
                    #rollback file changes
                    utils.run_shell_cmd(f"cp -rf /etc/systemd/resolved.conf.bak /etc/systemd/resolved.conf")
                    raise Exception(f"systemd-resolved service has failed to restart: {command_output}.  restoring backup file.  ")

                #remove temp and backup if successful.
                utils.run_shell_cmd(f"rm /etc/systemd/resolved.conf.temp")
                utils.run_shell_cmd(f"rm /etc/systemd/resolved.conf.bak")
                
                    
        except Exception as e:
            logger.exception(f"Exception retrieving dns value - {e}")
            errors.append(str(e))
            dns_name_array = []
            status = RemediateStatus.FAILED
        return status, errors

    def remediate(self, context: VrliContext, desired_values: Any) -> Dict:
        """Remediate current DNS configuration drifts.

        :param context: VRLI context instance.
        :type context: VrliContext
        :param desired_values: Desired values for DNS control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # vrli only needs servers for DNS control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
