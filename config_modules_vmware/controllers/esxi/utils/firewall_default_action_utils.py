# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import List
from typing import Tuple

from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))


def get_firewall_default_action(context: HostContext) -> Tuple[str, List[str]]:
    """
    :param context: ESXi context instance.
    :type context: HostContext
    :return: Tuple of str value DROP/PASS and a list of errors.
    :rtype: Tuple
    """
    errors = []
    default_action = None
    try:
        firewall_system = context.host_ref.configManager.firewallSystem
        is_incoming_blocked = firewall_system.firewallInfo.defaultPolicy.incomingBlocked
        default_action = "DROP" if is_incoming_blocked else "PASS"
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        errors.append(str(e))
    return default_action, errors


def set_firewall_default_action(context: HostContext, desired_values: str) -> Tuple[RemediateStatus, List[str]]:
    """
    :param context: Esxi context instance.
    :type context: HostContext
    :param desired_values: DROP/PASS to block/allow the network traffic.
    :type desired_values: str
    :return: Tuple of "status" and list of error messages.
    :rtype: Tuple
    """
    errors = []
    status = RemediateStatus.SUCCESS
    try:
        is_blocked = True if desired_values == "DROP" else False
        firewall_system = context.host_ref.configManager.firewallSystem
        default_policy = firewall_system.firewallInfo.defaultPolicy
        # Both incoming and outgoing policy needs to be same
        default_policy.incomingBlocked = is_blocked
        default_policy.outgoingBlocked = is_blocked
        firewall_system.UpdateDefaultPolicy(default_policy)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        errors.append(str(e))
        status = RemediateStatus.FAILED
    return status, errors
