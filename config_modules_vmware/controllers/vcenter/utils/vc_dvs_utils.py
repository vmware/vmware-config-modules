# Copyright 2025 Broadcom. All Rights Reserved.
import logging

from pyVmomi import vmodl  # pylint: disable=E0401

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


def is_host_disconnect_exception(e):
    # if all host issue are host disconnect, then return True
    # if any other host issue causing exception, return False
    if e.hostFault:
        for hostfault in e.hostFault:
            logger.debug(f"hostfault detail in exception: {hostfault}")
            if not isinstance(hostfault.fault, vmodl.fault.HostNotConnected):
                return False
    return True
