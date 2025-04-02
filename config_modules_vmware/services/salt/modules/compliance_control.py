# Copyright 2024 Broadcom. All Rights Reserved.
import logging

import salt.exceptions

import config_modules_vmware.services.salt.utils.compliance_control as compliance_control_util
from config_modules_vmware.interfaces.controller_interface import ControllerInterface

logger = logging.getLogger(__name__)

__virtualname__ = "vmware_compliance_control"


def __virtual__():
    return __virtualname__


def control_config_compliance_check(control_config, product, auth_context=None):
    """
    Checks compliance of control config. Control config can be ntp, dns, syslog, etc.
    Returns control compliance response object.

    control_config
        control config dict object.
    product
        appliance name - vcenter, sddc-manager, etc.
    auth_context
        optional auth context to access product.
    """

    logger.info("Running check compliance workflow...")
    if not auth_context:
        config = __opts__
        auth_context = compliance_control_util.create_auth_context(config=config, product=product)

    try:
        controller_interface_obj = ControllerInterface(auth_context)
        response_check_compliance = controller_interface_obj.check_compliance(desired_state_spec=control_config)
        logger.debug(f"Response for compliance check {response_check_compliance}")
        return response_check_compliance
    except Exception as exc:
        logger.error(f"Compliance check encountered an error: {str(exc)}")
        raise salt.exceptions.VMwareRuntimeError(str(exc))


def control_config_remediate(control_config, product, auth_context=None):
    """
    Remediate given compliance control config. Control config can be ntp, dns, syslog, etc.
    Returns remediation response object.

    control_config
        control config dict object.
    product
        appliance name. vcenter, sddc-manager, etc.
    auth_context
        Optional auth context to access product.
    """

    logger.info("Running remediation workflow...")

    if not auth_context:
        config = __opts__
        auth_context = compliance_control_util.create_auth_context(config=config, product=product)

    try:
        controller_interface_obj = ControllerInterface(auth_context)
        response_remediate = controller_interface_obj.remediate_with_desired_state(desired_state_spec=control_config)
        logger.debug(f"Remediation response {response_remediate}")
        return response_remediate

    except Exception as exc:
        # Handle exceptions by setting status as false and including exception details
        logger.error(f"Remediation encountered an error: {str(exc)}")
        raise salt.exceptions.VMwareRuntimeError(str(exc))
