import json
import logging
import os
import shlex  # nosec CWE-78
import subprocess  # nosec CWE-78

from typing import Dict, Tuple, List, Any

import requests, time
import os.path

from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.aria_suite import vrli_consts

logger = logging.getLogger(__name__)



def sddcm_install_li_agent(vrli_fqdn: str): 
    """install log insight agent.

    :param vrli_fqdn: VRLI fqdn.
    :type vrli_fqdn: string
    :return: None
    :rtype: None
    """

    #workaround for an issue in the install_li_agent.sh where http is hardcoded.  to be removed once script is fixed in future sddc manager version.  
    utils.run_shell_cmd(f"cp /opt/vmware/vcf/commonsvcs/scripts/install_li_agent.sh /tmp/install_li_agent_modified.sh")
    utils.run_shell_cmd(f"sed -i 's#wget http://$VRLI_CLUSTER:9000/api/v1/agent/packages/types/rpm -O /tmp/li-agent.rpm#wget https://$VRLI_CLUSTER:9543/api/v1/agent/packages/types/rpm --no-check-certificate -O /tmp/li-agent.rpm#g' /tmp/install_li_agent_modified.sh")
    utils.run_shell_cmd(f"/tmp/install_li_agent_modified.sh {vrli_fqdn}")

def install_li_agent(vrli_fqdn: str): 
    """install log insight agent.

    :param vrli_fqdn: VRLI fqdn.
    :type vrli_fqdn: string
    :return: None
    :rtype: None
    """

    try:
        with open("/tmp/install_li_agent_modified.sh", 'x') as install_li_agent_file:
            install_li_agent_file.write(vrli_consts.INSTALL_LI_AGENT_SCRIPT)
            utils.run_shell_cmd(f"chmod -R 755 /tmp/install_li_agent_modified.sh")

        #run shell script
        utils.run_shell_cmd(f"/tmp/install_li_agent_modified.sh {vrli_fqdn}")

        #remove temporary shell script
        utils.run_shell_cmd(f"rm /tmp/install_li_agent_modified.sh")
    except Exception as e:
        return False  

def check_li_agent_file_exists() -> bool: 
    """check if log insight agent config file exists.

    :return: if log insight file exists
    :rtype: Boolean
    """

    try:
        return os.path.isfile("/var/lib/loginsight-agent/liagent.ini")
    except Exception as e:
        return False  

def get_vrli_agent_config() -> Tuple[Dict, List[Any]]:
    """
    Read and return the configuration of the log insight agent.
    @return: the requested json file in python object
    @rtype: dict
    """
    errors = []
    try:
        syslog_servers = []

        syslog_host_port = 0
        syslog_hostname = ""
        syslog_protocol = ""

        #if agent is not installed, it's a drift
        if not check_li_agent_file_exists():
            syslog_servers = [{"hostname":"<agent not installed>", "port":0, "protocol":""}]
        else: 
            fileArray = open("/var/lib/loginsight-agent/liagent.ini", "r")
            for line in fileArray.readlines():  
                if "hostname=" in line:
                    syslog_hostname = line.replace("hostname=", "").replace("\n","")
                elif "port=" in line:
                    syslog_host_port = line.replace("port=", "").replace("\n","")
                elif "proto=" in line:
                    syslog_protocol = line.replace("proto=", "").upper().replace("\n","")

            fileArray.close()
            syslog_servers = [{"hostname":syslog_hostname, "port":int(syslog_host_port), "protocol":syslog_protocol}]

    except Exception as e:
        logger.exception(f"Exception retrieving syslog value - {e}")
        message = f"<unable to parse: invalid file format : remediation will update the config file in the proper format : Exception: {e}> "
        syslog_servers =  [{"hostname":message, "port":0, "protocol":""}]

    return syslog_servers, errors


def set_vrli_agent_config(desired_values: Dict) -> Tuple[str, List[Any]]:
    """
    Set SYSLOG config in Log Insight Agent Configuration.
    Will install the Log Insight Agent if it is not installed on the appliance.
    This will delete any existing SYSLOG entries and create the new desired ones as each SYSLOG entry requires a unique name associated with it.

    | Sample desired state for SYSLOG.

    .. code-block:: json

        {
            "syslog": {"hostName":"127.0.0.1","portNumber":"9000","protocol":"CFAPI"}
        }

    :param desired_values: Desired value for the SYSLOG config. Dict with keys "servers".
    :type desired_values: dict
    :return: Tuple of "status" and list of error messages.
    :rtype: Tuple
    """

    logger.info("Setting SYSLOG control config for audit.")
    errors = []
    status = RemediateStatus.SUCCESS
    ssl_default = "no"
    try:
        desired_syslog_servers = desired_values.get("servers", [])
        control_server_name = desired_syslog_servers[0]["hostname"].lower()
        control_port = desired_syslog_servers[0]["port"]
        control_protocol = desired_syslog_servers[0]["protocol"].lower()    

         #if agent is not installed, it's a drift
        if not check_li_agent_file_exists():   
            logger.info("log insight agent not installed, installing li agent now...")
            install_li_agent(control_server_name) 

        #backup existing file
        logger.info("performing backup of /var/lib/loginsight-agent/liagent.ini to /var/lib/loginsight-agent/liagent.ini.bak")
        utils.run_shell_cmd(f"cp /var/lib/loginsight-agent/liagent.ini /var/lib/loginsight-agent/liagent.ini.bak")

        logger.info("creating temp file /var/lib/loginsight-agent/liagent.tmp")

        #create new file with updates
        with open("/var/lib/loginsight-agent/liagent.ini", "r") as file_input:
            with open("/var/lib/loginsight-agent/liagent.tmp", "w") as output: 
                for line in file_input:
                    if line.find("hostname=") == 0 or line.find(";hostname=") == 0:
                        line = f"hostname={control_server_name}\n"
                    elif line.find("port=") == 0 or line.find(";port=") == 0:
                        line = f"port={control_port}\n"
                    elif line.find("proto=") == 0 or line.find(";proto=") == 0:
                        line = f"proto={control_protocol.lower()}\n"
                    elif line.find("ssl=") == 0 or line.find(";ssl=") == 0:
                        line = f"ssl={ssl_default}\n"

                    output.write(line)

        output.close()
        file_input.close()

        #update live file with new file
        utils.run_shell_cmd(f"cp -rf /var/lib/loginsight-agent/liagent.tmp /var/lib/loginsight-agent/liagent.ini")

        utils.run_shell_cmd(f"systemctl restart liagentd")
        time.sleep(5)

        command_output = utils.run_shell_cmd("systemctl status liagentd")[0]
        logger.info(f"command output from liagentd status: {command_output}")

        success_log_strings = ["Started Log Insight Agent.", "Started Operations for Logs Agent."]

        success = False
        for success_log_string in success_log_strings:
            if success_log_string in command_output:
                logger.info(f"Log Insight service has been restarted successfully.")
                success = True

        if not success:
            logger.info(f"Log Insight service has failed to restart")
            #rollback file changes
            utils.run_shell_cmd(f"cp -rf /var/lib/loginsight-agent/liagent.ini.bak /var/lib/loginsight-agent/liagent.ini")
            raise Exception(f"Log Insight service has failed to restart: {command_output}.  restoring backup file.  ")

        
        #remove temp and backup if successful.  
        utils.run_shell_cmd(f"rm /var/lib/loginsight-agent/liagent.tmp")
        utils.run_shell_cmd(f"rm /var/lib/loginsight-agent/liagent.ini.bak")

    except Exception as e:
        logger.exception(f"Exception setting syslog value - {e}")
        status = RemediateStatus.FAILED
        errors.append(str(e))
    return status, errors

