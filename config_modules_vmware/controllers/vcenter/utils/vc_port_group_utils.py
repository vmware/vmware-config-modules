# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

NSX_BACKING_TYPE = "nsx"
SWITCH_NAME = "switch_name"
PORT_GROUP_NAME = "port_group_name"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"


class PortGroupSecurityConfigEnum(Enum):
    MAC_CHANGES = "macChanges"
    FORGED_TRANSMITS = "forgedTransmits"
    ALLOW_PROMISCUOUS = "allowPromiscuous"


def get_all_non_uplink_non_nsx_port_group_and_security_configs(
    vc_vmomi_client: VcVmomiClient, security_config: PortGroupSecurityConfigEnum
) -> List[Tuple]:
    """Helper method to get all non-uplink, non-nsx dv port group objects and corresponding security policy config.

    :param vc_vmomi_client: VC vmomi client instance.
    :type vc_vmomi_client: VcVmomiClient
    :param security_config: Security policy config to fetch from DV port group.
    :type security_config: PortGroupSecurityConfigEnum
    :return: List of tuple of non-nsx, non-uplink dv_pg_refs and their security policy config.
    :rtype: List
    :return:
    """
    non_uplink_non_nsx_port_group_and_security_configs = []
    all_dv_port_group_refs = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualPortgroup)

    for dv_pg in all_dv_port_group_refs:
        is_nsx_backed = getattr(dv_pg.config, "backingType", "") == NSX_BACKING_TYPE
        is_uplink_port_group = getattr(dv_pg.config, "uplink", False)

        # Skip NSX backed or uplink port group types.
        if is_nsx_backed or is_uplink_port_group:
            logger.info(f"Skipping NSX backed or uplink port group {dv_pg.name}")
            continue

        has_security_policy_config = (
            hasattr(dv_pg.config, "defaultPortConfig")
            and hasattr(dv_pg.config.defaultPortConfig, "securityPolicy")
            and hasattr(dv_pg.config.defaultPortConfig.securityPolicy, security_config.value)
        )

        if has_security_policy_config:
            security_policy_config = getattr(dv_pg.config.defaultPortConfig.securityPolicy, security_config.value)
            non_uplink_non_nsx_port_group_and_security_configs.append(
                (dv_pg, security_policy_config.value if security_policy_config is not None else False)
            )
    return non_uplink_non_nsx_port_group_and_security_configs


def get_non_compliant_security_policy_configs(dv_pg_configs: List, desired_values: Dict, desired_key: str) -> List:
    """Get all non-compliant security policy config for the given desired state spec.

    :return:
    :meta private:
    """
    non_compliant_configs = []
    desired_configs = []

    global_desired_value = desired_values.get(GLOBAL, {}).get(desired_key)
    overrides = desired_values.get(OVERRIDES, [])

    overrides_pgs_config_map = {}
    for override in overrides:
        switch_name = override.get(SWITCH_NAME)
        port_group_name = override.get(PORT_GROUP_NAME)
        key = (switch_name, port_group_name)
        overrides_pgs_config_map[key] = override.get(desired_key)

    for config in dv_pg_configs:
        switch_name = config.get(SWITCH_NAME)
        port_group_name = config.get(PORT_GROUP_NAME)
        key = (switch_name, port_group_name)
        if key in overrides_pgs_config_map:
            desired_value = overrides_pgs_config_map[key]
        else:
            desired_value = global_desired_value

        if desired_value != config.get(desired_key):
            non_compliant_configs.append(config)
            desired_configs.append(
                {SWITCH_NAME: switch_name, PORT_GROUP_NAME: port_group_name, desired_key: desired_value}
            )

    return non_compliant_configs, desired_configs
