import logging
import socket
import requests
import json
import time
from typing import Dict
from typing import List
from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.utils import utils


ERROR_MSG_NOT_VIP = "This NSX Manager node is not the cluster leader/vip. Skipping compliance check."
API_TIMEOUT = 120
API_RETRY_INTERVAL = 5

logger = LoggerAdapter(logging.getLogger(__name__))
http_headers = {'Content-Type': 'application/json'}

def get_hostname():
    return socket.getfqdn()

def get_cluster_status(context) -> str:
    """
    Call NSX-T Manager API to get current config.

    :return: response body
    :rtype: dict
    """   

    max_duration = API_TIMEOUT
    interval = API_RETRY_INTERVAL
    start_time = time.time()
    remaining_time = max_duration
    
    while (time.time() - start_time) < max_duration:
        try:
            nsx_request = requests.get(
                f"https://localhost/api/v1/cluster/status",
                headers=http_headers,
                auth=(context._username, context._password),
                verify=False,
                timeout=5,
            )
            nsx_request.raise_for_status()
            nsx_request_body = nsx_request.json()
            logger.debug(f"NSX API query response body: {nsx_request_body}")
            return nsx_request_body
        except requests.exceptions.HTTPError as e:
            raise Exception(f"NSX Request failed with error: {e}")
        except Exception as e:
            logger.info(f"NSX API connectione error: will retry in {interval} seconds")
            remaining_time = max_duration - (time.time() - start_time)
            if remaining_time <= 0:
                break
            time.sleep(min(interval, remaining_time))
           	           
    raise Exception(f"NSX Request failed after trying for {max_duration} seconds. Unable to get cluster status.")


def isLeader(context):
    #Check if current node is NSX leader/vip owner
    bLeader = False

    #get the hostname
    hostname = get_hostname()
  
    #get cluster details
    cluster_status = get_cluster_status(context)
    detailed_status = cluster_status["detailed_cluster_status"]
  
    #loop through service groups for HTTPS group
    for group in detailed_status["groups"]:
        if group["group_type"] == "HTTPS":
            leaders = group["leaders"]
            leader_id = leaders[0]["leader_uuid"]

            #get node members uuids
            members = group["members"]

            #try to match hostname to uuid
            for member in members:
                if member["member_uuid"] == leader_id:
                    if hostname  in member["member_fqdn"]:
                        bLeader = True
            logger.info(f"HTTP members: {members}")
            break

    return bLeader

    
def strip_nsxcli_json_output(context, cli_output):
    #remove any empty lines in output that begin with "Warning:"
    lines = cli_output.split('\n')
    new_lines = [line for line in lines if not line.strip().startswith("Warning:")]
    result = json.loads('\n'.join(new_lines))
    return result
    
def strip_nsxcli_output(context, cli_output):
    #remove any empty lines in output that begin with "Warning:"
    lines = cli_output.split('\n')
    new_lines = [line for line in lines if not line.strip().startswith("Warning:")]
    return new_lines


def get_nsx_version(context) -> tuple:
    """
    Call NSXCLI to get current version.

    :return: response body
    :rtype: dict
    """   
    try:
        command_output = utils.run_shell_cmd("su -c 'get version | json' admin")[0]
        result = strip_nsxcli_json_output(context,command_output)
        version_arr = result["version"].split(".")
        product_version = "{}.{}.{}".format(
                version_arr[0],
                version_arr[1] if len(version_arr) > 1 else 0,
                version_arr[2] if len(version_arr) > 2 else 0,
            )
        return product_version
    except Exception as e:
        logger.exception(f"Exception retrieving NSX version from NSXCLI - {e}")

 
