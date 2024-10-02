# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

SNMP_CONFIG_GET = "system snmp get"
SNMP_CONFIG_SET_V3TARGETS = "system snmp set --v3targets {v3_targets}"
SNMP_CONFIG_SET_ENABLE = "system snmp set --enable {enable}"
SNMP_CONFIG_SET_AUTH = "system snmp set --authentication {auth}"
SNMP_CONFIG_SET_PRIVACY = "system snmp set --privacy {privacy}"
SNMP_CONFIG_SET_COMMUNITIES = "system snmp set --communities {communities}"

CLI_AUTHENTICATION = "Authentication"
AUTHENTICATION = "authentication"
CLI_PRIVACY = "Privacy"
PRIVACY = "privacy"
CLI_COMMUNITIES = "Communities"
COMMUNITIES = "communities"
CLI_ENABLE = "Enable"
ENABLE = "enable"
CLI_V3TARGETS = "V3targets"
V3TARGETS = "v3_targets"
HOSTNAME = "hostname"
PORT = "port"
USERID = "userid"
SECURITY_LEVEL = "security_level"
MESSAGE_TYPE = "message_type"


class SnmpConfig(BaseController):
    """ESXi controller to get/set snmp configurations for ESXi host.

    | Config Id - 1114
    | Config Title - SNMP must be configured properly on the ESXi host.

    """

    metadata = ControllerMetadata(
        name="snmp_config",  # controller name
        path_in_schema="compliance_config.esxi.snmp_config",
        # path in the schema to this controller's definition.
        configuration_id="1114",  # configuration id as defined in compliance kit.
        title="SNMP must be configured properly on the ESXi host.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def _parse_snmp_configs(self, cli_output) -> Dict:
        """Parse snmp configs retrieved from esxi host.

        :param cli_output: snmp configs received from esxcli output.
        :type cli_output: string
        :return: Dict of parsed snmp configs.
        :rtype: Dict
        """

        snmp_configs = {}
        # parse esxcli output line by line
        for line in cli_output.strip().split("\n"):
            key, value = map(str.strip, line.split(":", 1))
            # if it is authentication
            if key == CLI_AUTHENTICATION:
                snmp_configs[AUTHENTICATION] = value.strip() or "none"
            # if it is privacy
            elif key == CLI_PRIVACY:
                snmp_configs[PRIVACY] = value.strip() or "none"
            # if it is community list
            elif key == CLI_COMMUNITIES:
                snmp_configs[COMMUNITIES] = [comm.strip() for comm in value.split(",")]
            # if it is Enabled
            elif key == CLI_ENABLE:
                snmp_configs[ENABLE] = value.strip().lower() == "true"
            # if it is V3targets, if it is, extract V3targets values
            # v3targets contain hostname/IP, port, userid, security level and message type
            elif key == CLI_V3TARGETS:
                logger.debug(f"V3targets: {value}")
                if value:
                    hostname, rest_v3targets = value.split("@", 1)
                    port, userid, security_level, message_type = rest_v3targets.strip().split(maxsplit=3)
                    snmp_configs[V3TARGETS] = {
                        HOSTNAME: hostname.strip(),
                        PORT: int(port),
                        USERID: userid.strip(),
                        SECURITY_LEVEL: security_level.strip(),
                        MESSAGE_TYPE: message_type.strip(),
                    }

        logger.debug(f"Parsed snmp configs: {snmp_configs}")
        return snmp_configs

    def _gen_v3targets_str(self, v3_targets) -> str:
        """Generate V3targets string for esxcli snmp configs.

        :param v3_targets: V3targets configs.
        :type v3_targets: dict
        :return: V3targets string for esxcli set.
        :rtype: string
        """
        return (
            f"{v3_targets[HOSTNAME]}@{v3_targets[PORT]}"
            f"/{v3_targets[USERID]}"
            f"/{v3_targets[SECURITY_LEVEL]}"
            f"/{v3_targets[MESSAGE_TYPE]}"
        )

    def get(self, context: HostContext) -> Tuple[bool, List[str]]:
        """Get snmp configs for esxi host.

        :param context: ESXi context instance.
        :type context: HostContext
        :return: Tuple of boolean value True/False and a list of errors.
        :rtype: Tuple
        """
        logger.info("Getting snmp config for esxi.")
        errors = []
        snmp_configs = {}
        try:
            cli_output, _, _ = context.esx_cli_client().run_esx_cli_cmd(context.hostname, SNMP_CONFIG_GET)
            logger.debug(f"Snmp configs output for esxi: {cli_output}")
            snmp_configs = self._parse_snmp_configs(cli_output)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return snmp_configs, errors

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set snmp config for esxi host based on desired value.

        :param context: Esxi context instance.
        :type context: HostContext
        :param desired_values: boolean value True/False to update config.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting snmp configs for esxi")
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            esxcli = context.esx_cli_client()
            # set snmp authentication
            auth = desired_values.get(AUTHENTICATION)
            if auth:
                esxcli.run_esx_cli_cmd(context.hostname, SNMP_CONFIG_SET_AUTH.format(auth=auth))
            # set snmp privacy
            privacy = desired_values.get(PRIVACY)
            if privacy:
                esxcli.run_esx_cli_cmd(context.hostname, SNMP_CONFIG_SET_PRIVACY.format(privacy=privacy))
            # set snmp v3targets
            v3_targets = desired_values.get(V3TARGETS)
            if v3_targets:
                v3_targets_str = self._gen_v3targets_str(v3_targets)
                esxcli.run_esx_cli_cmd(context.hostname, SNMP_CONFIG_SET_V3TARGETS.format(v3_targets=v3_targets_str))
            # set snmp communities
            communities = desired_values.get(COMMUNITIES)
            if communities:
                communities_str = ",".join(map(str, communities))
                esxcli.run_esx_cli_cmd(
                    context.hostname, SNMP_CONFIG_SET_COMMUNITIES.format(communities=communities_str)
                )
            # set snmp enable
            enable = desired_values.get(ENABLE)
            if enable is not None:
                enable_str = "true" if enable is True else "false"
                esxcli.run_esx_cli_cmd(context.hostname, SNMP_CONFIG_SET_ENABLE.format(enable=enable_str))
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors
