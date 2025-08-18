import logging
from typing import Dict, Tuple, List, Any

from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


class AllowedPorts(BaseController):
    """Check local listening ports.
    This is a common controller implementation for both nsxt manager and nsxt edge.

    | Config Id - 0000
    | Config Title - Only necessary ports should be listening

    """

    metadata = ControllerMetadata(
        name="allowed_ports",  # controller name
        path_in_schema="compliance_config.nsxt_manager.allowed_ports",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Only necessary ports should be listening on NSX manager",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[
            NSXTManagerContext.ProductEnum.NSXT_MANAGER
        ],  # product from enum in NSXTManagerContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsx_manager"],  # location where functional tests are run.
    )

 
    def _get_listening_ports(self, context: NSXTManagerContext) -> List[str]:
        port_list = []
        logger.info("Getting local ports.")
        tcp_ports = set()
        udp_ports = set()

        #Run lsof command to get active ports. Filter with awk to retrive ports that are 
        #listening for external connections 
        #
        #lsof output example:
        #COMMAND     PID            USER   FD   TYPE     DEVICE SIZE/OFF NODE NAME
        #
        #python3    7717            root    3u  IPv4      37509      0t0  UDP *:55284
        #sshd      11574            root    3u  IPv4 2029912624      0t0  TCP *:22 (LISTEN)
        #java      12981           corfu  101u  IPv4      55310      0t0  TCP 10.75.185.107:9000 (LISTEN)

        command_output = utils.run_shell_cmd("lsof -i -P -n ")[0]
        grep_output = utils.run_shell_cmd("awk '/LISTEN/ && !/127.0.0/'",input_to_stdin=command_output)[0]
        for line in grep_output.strip().splitlines():
            parts = line.split()
            port = parts[8].split(':')[1]
            protocol = parts[7]      
            if protocol == "TCP":
                tcp_ports.add(int(port))
            else:
                udp_ports.add(int(port))

        open_ports = {"tcp": list(tcp_ports), "udp": list(udp_ports)}
        logger.info(f"open_ports: {open_ports}")
        
        return open_ports
        

    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get open listening ports from OS.

        | Sample get output

        .. code-block:: json

            {
              "tcp": [22,443,9000,1234],
              "udp": [126]
            }

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing local accounts and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting open ports.")
        errors = []
        open_ports = []
        try:
            open_ports = self._get_listening_ports(context)
            logger.info(f"found listening ports: {open_ports}")
        except Exception as e:
            logger.exception(f"Exception retrieving listening ports - {e}")
            errors.append(str(e))
        return open_ports, errors

    def check_compliance(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.
        [Note: This needs to be moved as part of framework input validation once available.]

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        logger.debug("checking compliance")

        errors = None
        try:
            current_values = self._get_listening_ports(context=context)
        except Exception as e:
            errors.append(str(e))
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}
 
        desired_tcp = desired_values.get("tcp",[])
        current_tcp = current_values.get("tcp",[])
        desired_udp = desired_values.get("udp",[])
        current_udp = current_values.get("udp",[])
      
        # Use set difference to get any ports in current config which are not in the desired state
        tcp_drift = set(current_tcp) - set(desired_tcp)
        udp_drift = set(current_udp) - set(desired_udp)

        if (len(udp_drift) > 0 ) or (len(tcp_drift) > 0): 
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_values,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
    
    def set(self, context: NSXTManagerContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set NTP config in NSX.
        Also post set, check_compliance is run again to validate that the values are set.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired value for the local accounts.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current local account configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for local accounts.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
    