import logging
from typing import Dict, Tuple, List, Any

import requests, re, socket

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


class SecureSSH(BaseController):
    """Manage NSX SSH key size.
    This is a common controller implementation for both nsxt manager and nsxt edge.

    | Config Id - 0000
    | Config Title - NSX Manager must use SSHv2 with at least 2048 modulus key size

    """

    metadata = ControllerMetadata(
        name="secure_ssh",  # controller name
        path_in_schema="compliance_config.nsxt_manager.secure_ssh",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate the SSH key length on NSX-T nodes.",  # controller title as defined in compliance kit.
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

    def _get_ssh_key_len(self) -> int:
        """
        Get SSh key helper.

        :return: SSH key length
        :rtype: int
        """
        logger.info(f"Getting SSh key lenth")
        command_output = utils.run_shell_cmd("ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key")[0]
        logger.debug(f"command_output: {command_output}")
        ssh_key_len = list(command_output.strip().split(" "))[0]
        return int(ssh_key_len)
    
    
    def _get_ssh_version(self) -> str:
        """
        Get SSh key helper.

        :return: SSH key length
        :rtype: int
        """
        ssh_version = None
        timeout=5
        host='localhost'
        port=22
        logger.info(f"Getting SSH protocol version")
        #Use socket to localhost to get SSH banner
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:            
            sock.settimeout(timeout)
            sock.connect((host, port))

            #get banner with SSH protocol version. e.g. "SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.5"
            banner = sock.recv(1024).decode('utf-8').strip()
            #extract SSH version
            pattern = "^(.*?)(?=-OpenSSH)"
            match = re.match(pattern, banner)
            ssh_version = match.group(1).split('-')[1]
            logger.debug(f"ssh version: {ssh_version}")
        except Exception as e:
            sock.close()
            error = f"Exception retrieving SSH key length value - {e}"
            logger.exception(error)
            raise  Exception(error)
        finally:
            sock.close()

        return ssh_version


    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get SSH key length config from NSX.

        | Sample get output

        .. code-block:: json

            {
              "sh_key_len": 2048,
              "ssh_version": '2.0'
            }

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing SSh key length  and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting SSH key config.")
        errors = []
        ssh_key_len = None
        ssh_version = None

        try:
            ssh_key_len = self._get_ssh_key_len()
            ssh_version = self._get_ssh_version()
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))
        
        logger.info(f"ssh_key_len: {ssh_key_len}")    
        logger.info(f"ssh_version: {ssh_version}")    
        return {"ssh_key_len": ssh_key_len, "ssh_version": ssh_version}, errors
    
    def set(self, context: NSXTManagerContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}


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

        current_values,errors = self.get(context=context)

         # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}
        
        logger.info(f"current_values: {current_values}")
        logger.info(f"desired_values: {desired_values}") 
        
        desired_key_len = desired_values.get("ssh_key_len", [])
        desired_ssh_version = desired_values.get("ssh_version", [])

        if not desired_key_len or not desired_ssh_version:
            raise  Exception(f"Exception getting desired value")

        current_key_len = current_values.get("ssh_key_len", 0)
        current_ssh_version = current_values.get("ssh_version", 0)

        if not current_key_len or not current_ssh_version:
             raise  Exception(f"Exception getting current value")
        
        #Check if ssh key len is equal or larger than desired value
        #Check if current ssh version is greater or equal to desired version
        if (current_key_len < desired_key_len) or (current_ssh_version != desired_ssh_version): 
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_values,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
                          

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current SSH key length configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for SSH key length.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """

        logger.info("Remediation is not implemented. Manual intervention required.")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
    
