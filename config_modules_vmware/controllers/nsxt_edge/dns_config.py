import logging
import json
from typing import Dict, Tuple, List, Any

from config_modules_vmware.framework.auth.contexts.nsxt_edge_context import NSXTEdgeContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class DnsConfig(BaseController):
    """Manage dns config with get and set methods.
    This is a common controller implementation for both nsxt manager and nsxt edge.

    | Config Id - 0000
    | Config Title - DNS should be configured to a global value.

    """

    metadata = ControllerMetadata(
        name="dns",  # controller name
        path_in_schema="compliance_config.nsxt_edge.dns",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Configure DNS servers for the NSX-T nodes.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[

            NSXTEdgeContext.ProductEnum.NSXT_EDGE,
        ],  # product from enum in NSXTEdgeContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsx_edge"],  # location where functional tests are run.
    )

    def _validate_input(self, desired_values) -> bool:
        to_validate = desired_values.get("servers", [])
        #check for duplicates
        if len(to_validate) != len(set(to_validate)):
            raise ValueError(f"Found duplicate input entries for DNS servers. {desired_values}")
        
        for item in to_validate:
            if not (utils.isValidIp(item) or utils.isValidFqdn(item)):
                    raise ValueError(f"{item} is not a valid IP or FQDN.")

    @staticmethod
    def _add_dns(server: str) -> bool:
        """
        Add dns server.
        :param server: dns server.
        :type server: str
        :return: True
        :rtype: bool
        """
        logger.info(f"Adding dns server {server}")
        utils.run_shell_cmd(f"su -c 'set name-server {server}' admin")
        return True

    @staticmethod
    def _del_dns(server: str) -> bool:
        """
        Delete dns server
        :param server: dns server.
        :type server: str
        :return: True
        :rtype: bool
        """
        logger.info(f"Deleting dns server {server}")
        utils.run_shell_cmd(f"su -c 'del name-server {server} ' admin")
        return True

    def get(self, context: NSXTEdgeContext) -> Tuple[Dict, List[Any]]:
        """
        Get dns config from NSX.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["10.0.10.10", "10.0.10.11"]
            }

        :param context: NSXTEdgeContext, since this controller doesn't require product specific context.
        :type context: NSXTEdgeContext
        :return: Tuple of Dict containing dns servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting dns servers.")
        errors = []
        try:
            command_output = utils.run_shell_cmd("su -c 'get name-servers | json' admin")[0]
            result = nsx_utils.strip_nsxcli_json_output(context,command_output)
        except Exception as e:
            raise Exception(f"Exception retrieving dns value from NSXCLI: {str(e)}")

        return {"servers": result["name_servers"]}, errors

    def check_compliance(self, context: NSXTEdgeContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.
        [Note: This needs to be moved as part of framework input validation once available.]

        :param context: Product context instance.
        :type context: NSXTEdgeContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # NSX only needs servers for dns control
        desired_values = {"servers": desired_values.get("servers", [])}
        logger.debug(f"Desired values:  {desired_values}")
        self._validate_input(desired_values)
        return super().check_compliance(context, desired_values)

    def set(self, context: NSXTEdgeContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set dns config in NSX.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for dns.

        .. code-block:: json

            {
              "servers": ["10.0.10.10","10.0.10.11"]
            }

        :param context: Product context instance.
        :type context: NSXTEdgeContext
        :param desired_values: Desired value for the dns config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting dns control config for audit.")
        errors = []
        try:
            current_dns_servers, get_errors = self.get(context)
            if get_errors:
                raise Exception(f"Exception getting current dns servers: {get_errors[0]}")

            current_dns_servers = current_dns_servers.get("servers", [])
            desired_dns_servers = desired_values.get("servers", [])

            logger.debug(f"Current dns servers: {current_dns_servers}")
            logger.debug(f"Desired dns servers: {desired_dns_servers}")

            num_servers = len(current_dns_servers)
            
            #NSX supports a max of 3 DNS servers. Adding the desired servers prior to deleting current ones may cause an error
            #during the add. To mitigate a failure to add a DNS server resulting in no DNS servers configured after remediation. The DNS servers
            #are added one at a time up to the limit of 3, then undesired servers removed one at a time.
            #Replace undesired DNS entries one at a time.
            for dns_server in set(desired_dns_servers) - set(current_dns_servers):
                logger.debug(f"checking {dns_server} in {current_dns_servers}")
                #check if server is already configured
                if dns_server not in current_dns_servers:
                    #if current server less than 3 add
                    if len(current_dns_servers) < 3:
                        logger.debug(f"Adding {dns_server}")
                        self._add_dns(dns_server)
                        current_dns_servers.append(dns_server)
                    #current servers >3, remove an undesired server first.
                    else:
                        for item in current_dns_servers:
                            logger.debug(f"List >3 checking {item} in {current_dns_servers}")
                            if item not in desired_dns_servers:
                                logger.debug(f"Deleting {item}")
                                self._del_dns(item)
                                current_dns_servers.remove(item)
                                break
                        logger.debug(f"Adding {dns_server}")
                        #Add desired server
                        self._add_dns(dns_server)
            
            #remove any remaining undesired servers
            for dns_server in current_dns_servers:
                if dns_server not in desired_dns_servers:
                    logger.debug(f"Deleting {dns_server}")
                    self._del_dns(dns_server)


            if self.check_compliance(context, desired_values).get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Failed to update dns servers")

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting dns value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: NSXTEdgeContext, desired_values: Any) -> Dict:
        """Remediate current dns configuration drifts.

        :param context: Product context instance.
        :type context: NSXTEdgeContext
        :param desired_values: Desired values for dns control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # NSX only needs servers for dns control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
