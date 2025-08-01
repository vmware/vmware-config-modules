import logging
import json
import socket
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


class SyslogConfig(BaseController):
    """Manage syslog config with get and set methods.
    This is a common controller implementation for both nsxt manager and nsxt edge.

    | Config Id - 0000
    | Config Title - Configure Syslog servers.

    """
    metadata = ControllerMetadata(
        name="syslog",  # controller name
        path_in_schema="compliance_config.nsxt_edge.syslog",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Configure Syslog servers for the NSX-T nodes.",  # controller title as defined in compliance kit.
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

    
     
    def _hostnameResolvable(self, hostname: str) -> bool:
        try:
            ip_address = socket.gethostbyname(hostname)
            return True
        except:
            return False
        
    def _get_cmd_args(self, server: dict) -> str:
        #transform into payload for NSX CLI command. CLi expects lowercase for string arguments
        hostname = server['hostname']
        port = server['port']
        proto = server['protocol'].lower()

        cmd_args = f"{hostname}:{port} proto {proto}"
        if (server.get("level")):
            level = server['level'].lower()
            cmd_args += f" level {level}"
        cmd_args = f"{hostname}:{port} proto {proto} level {level}"
        if (server.get("facility")):
            facility = ','.join(server['facility']).lower() 
            cmd_args += f" facility {facility}"
        
        return cmd_args
        
    
   
    def _add_syslog(self, server: dict) -> bool:
        """
        Add syslog server.
        :param server: syslog server.
        :type server: str
        :return: True
        :rtype: bool
        """
        logger.info(f"Adding syslog server {server}")
        args = self._get_cmd_args(server)
        utils.run_shell_cmd(f"su -c 'set logging-server {args}' admin")
        return True

 
    def _del_syslog(self, server: dict, context) -> bool:
        """
        Delete syslog server
        :param server: syslog server.
        :type server: str
        :return: True
        :rtype: bool
        """

        logger.info(f"Deleting syslog server {server}")
        args = self._get_cmd_args(server)        
        try:
            utils.run_shell_cmd(f"su -c 'del logging-server {args}' admin")
        except Exception as e:
            #If exception, check if syslog server was successfully deleted.
            #In some cases syslog delete command return an error but the deletion did succeed. This is a bug resolved in NSX 4.1
            #This check allows the control to continue in this case
            logger.info(f"Received exception {e} from delete")
            current_syslog_servers, get_errors = self.get(context)
            if get_errors:
                raise Exception(f"Exception getting current syslog servers: {get_errors[0]}")
            for item in current_syslog_servers.get("servers"):
                if (item["hostname"] == server["hostname"]):
                    logger.info(f"Failed to delete syslog server {server}")
                    raise Exception(f"ERROR: Failed to delete syslog server {server['hostname']}: {e}")
            logger.info(f"Got exception but successfully deleted syslog server {server}. Will continue.")
        return True

    def get(self, context: NSXTEdgeContext) -> Tuple[Dict, List[Any]]:
        """
        Get syslog config from NSX.

        | Sample get output

        .. code-block:: json

            {
              "servers": ["hostname": "syslog.local", "port": 514, "protocol": TCP, "level": "INFO", "facility": ["AUTH', "LOCAL6"]]
            }

        :param context: NSXTEdgeContext, since this controller doesn't require product specific context.
        :type context: NSXTEdgeContext
        :return: Tuple of Dict containing syslog servers and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting syslog servers.")        
        errors = []
        
        try:
            command_output = utils.run_shell_cmd("su -c 'get logging-servers | json' admin")[0]
            result = nsx_utils.strip_nsxcli_json_output(context,command_output)
            product_version = nsx_utils.get_nsx_version(context)
        except Exception as e:
            raise Exception(f"Exception retrieving dns value from NSXCLI: {str(e)}")

        #transform JSON    
        sysLogList = []    
        for item in result:
            item['port'] = int(item['server'].split(':')[1])
            item['hostname'] = item['server'].split(':')[0]
            item['protocol'] = (item['proto']).upper()   
            #facility is optional in NSX syslog config. Only transform if the key exists.       
            if 'facility' in item:  
                item['facility'] = (item['facility']).upper().split(',')
            item['level'] = (item['level']).upper()
            del item['server']
            del item['proto']
            #in NSX 4.x 'exporter_name' is an additional property. Not requred to set, but if not filtered out will produce drift when there is none.
            #Check NSX version, if 4.x filter out the 'exporter_name'
            if utils.is_newer_or_same_version(product_version, "4.0.0"):
                if 'exporter_name' in item:
                    del item['exporter_name']
      
        return {"servers": result}, errors

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
        # NSX only needs servers for syslog control
        desired_values = {"servers": desired_values.get("servers", [])}
        logger.error(f"Desired values:  {desired_values}")
        return super().check_compliance(context, desired_values)

    def set(self, context: NSXTEdgeContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set syslog config in NSX.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for syslog.

        .. code-block:: json

            {
              "servers": ["hostname": "syslog.local", "port": 514, "protocol": TCP, "level": "INFO", "facility": ["AUTH', "LOCAL6"]]
            }

        :param context: Product context instance.
        :type context: NSXTEdgeContext
        :param desired_values: Desired value for the syslog config. Dict with keys "servers".
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting syslog control config for audit.")
        errors = []
        try:
            current_syslog_servers, get_errors = self.get(context)
            if get_errors:
                raise Exception(f"Exception getting current syslog servers: {get_errors[0]}")

            desired_syslog_servers = desired_values#{"servers": desired_values.get("servers", [])}

            logger.debug(f"Current syslog servers: {current_syslog_servers}")
            logger.debug(f"Desired syslog servers: {desired_syslog_servers}")

            #First, check if syslog servers are resolvable. If not the NSX cli will fail to update syslog server config
            for syslog_server in desired_syslog_servers.get("servers",[]):
                hostname = syslog_server["hostname"]
                if not self._hostnameResolvable(hostname):   
                    raise Exception(f"Hostname {hostname} is not resolvable. Unable to configure syslog. Please check hostname or DNS configuration and try again.")

            toDel = []
            toAdd = []

            if len(current_syslog_servers) == 0:
                #No current syslog servers. add all desired
                toAdd = desired_syslog_servers.get("servers",[])
            else:       
                #get servers to add that do not exist in current list
                for desired in desired_syslog_servers.get("servers",[]): 
                    found = False
                    for current in current_syslog_servers.get("servers",[]):
                        if current['hostname'] == desired['hostname']:
                            #syslog server config exists
                            found = True
                            break
                    if not found:
                        #desired syslog server config does not exist
                        toAdd.append(desired)
                #check all current servers for any configs that drift or servers that should not be configured
                for current in current_syslog_servers.get("servers",[]):                                    
                    for desired in desired_syslog_servers.get("servers",[]):
                        match = False                        
                        #sort facility array, otherwise dict compare does not match when array elements are the same but in different order
                        if "facility" in current:
                            current["facility"].sort()
                        if "facility" in desired:
                            desired["facility"].sort()
                        
                        if current == desired:
                            #if matched skip  
                            match = True           
                            break          
                        elif current['hostname'] == desired['hostname']:
                            #if not matched but hostname is the same then config paramaters drift
                            #add the current entry to delete list
                            #add the desired to add list
                            toDel.append(current)
                            toAdd.append(desired)
                            match = True
                            break
                    logger.info("Checking if desired was found")
                    if not match:    
                        #current server is not in desired. add to delete list                
                        logger.info(f"current server {current} does not match any desired state. adding to list to update")
                        toDel.append(current)

            logger.debug(f"to add: {toAdd}")
            logger.debug(f"to Del: f{toDel}")   

            #Delete syslog servers that need update
            for server_to_del in toDel:
                self._del_syslog(server_to_del,context)

            #add missing syslog servers and updated syslog server
            for server_to_add in toAdd:
                self._add_syslog(server_to_add)

            if self.check_compliance(context, desired_values).get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Failed to update syslog servers")

            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting syslog value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors

    def remediate(self, context: NSXTEdgeContext, desired_values: Any) -> Dict:
        """Remediate current syslog configuration drifts.

        :param context: Product context instance.
        :type context: NSXTEdgeContext
        :param desired_values: Desired values for syslog control.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        # NSX only needs servers for syslog control
        desired_values = {"servers": desired_values.get("servers", [])}
        return super().remediate(context, desired_values)
