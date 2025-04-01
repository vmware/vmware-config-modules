# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging

import config_modules_vmware.services.salt.utils.compliance_control as compliance_control_util
from config_modules_vmware.framework.models.output_models.compliance_response import (
    ComplianceStatus,
)
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = logging.getLogger(__name__)

__virtualname__ = "vmware_compliance_control"
__proxyenabled__ = ["vmware_compliance_control"]


def __virtual__():
    return __virtualname__


def check_control(name, control_config, product, ids=None):
    """
    Check and apply vcenter control configs. Control config can be ntp, dns, syslog, etc.
    Return control compliance response if test=true. Otherwise, return remediate response.

    name
        Config name
    control_config
        vc control config dict object.
    product
        appliance name. vcenter, nsx, etc.
    ids
        List of product ids within the parent product.
    """

    logger.info(f"Starting compliance check for {name}")

    config = __opts__
    auth_context = compliance_control_util.create_auth_context(config=config, product=product, ids=ids)
    control_config = json.loads(json.dumps(control_config))

    try:
        compliance_config = control_config.get("compliance_config")
        if not isinstance(compliance_config, dict) or not compliance_config:
            raise Exception("Desired spec is empty or not in correct format")
        else:
            product_control_config = control_config.get("compliance_config", {}).get(product)
            if product_control_config:
                control_config = {"compliance_config": {product: product_control_config}}
            else:
                err_msg = f"Desired spec is empty for {product}"
                logger.error(err_msg)
                return {
                    "name": name,
                    "result": None,
                    "changes": {},
                    "comment": err_msg,
                }

        if __opts__["test"]:
            # If in test mode, perform audit
            logger.info("Running in test mode. Performing check compliance.")
            compliance_response = __salt__["vmware_compliance_control.control_config_compliance_check"](
                control_config=control_config,
                product=product,
                auth_context=auth_context,
            )

            compliance_status = compliance_response["status"]
            logger.debug(f"Compliance check completed with {compliance_status} status.")
            if compliance_status == ComplianceStatus.COMPLIANT or compliance_status == ComplianceStatus.SKIPPED:
                ret = {
                    "name": name,
                    "result": True,
                    "comment": compliance_status,
                    "changes": compliance_response.get("changes", {}),
                }
            elif compliance_status == ComplianceStatus.NON_COMPLIANT or compliance_status == ComplianceStatus.FAILED:
                ret = {
                    "name": name,
                    "result": (None if compliance_status == ComplianceStatus.NON_COMPLIANT else False),
                    "comment": compliance_status,
                    "changes": compliance_response.get("changes", {}),
                }
            else:
                # Exception running compliance workflow
                ret = {
                    "name": name,
                    "result": False,
                    "comment": compliance_status,
                    "changes": {"message": compliance_response.get("message", "Exception running compliance.")},
                }
        else:
            # Not in test mode, proceed with pre-check and remediation
            logger.debug("Performing remediation.")
            remediate_response = __salt__["vmware_compliance_control.control_config_remediate"](
                control_config=control_config,
                product=product,
                auth_context=auth_context,
            )
            remediate_status = remediate_response["status"]
            logger.debug(f"Remediation completed with {remediate_status} status.")
            if remediate_status == RemediateStatus.SUCCESS or remediate_status == RemediateStatus.SKIPPED:
                ret = {
                    "name": name,
                    "result": True,
                    "comment": remediate_status,
                    "changes": remediate_response.get("changes", {}),
                }
            elif remediate_status == RemediateStatus.FAILED or remediate_status == RemediateStatus.PARTIAL:
                ret = {
                    "name": name,
                    "result": False,
                    "comment": remediate_status,
                    "changes": remediate_response.get("changes", {}),
                }
            else:
                # Exception running remediation workflow
                ret = {
                    "name": name,
                    "result": False,
                    "comment": remediate_status,
                    "changes": {
                        "message": remediate_response.get("message", "Exception running remediation."),
                    },
                }

    except Exception as e:
        # Exception occurred
        error_message = f"An error occurred: {str(e)}"
        return {
            "name": name,
            "result": False,
            "changes": {},
            "comment": error_message,
        }

    logger.debug(f"Completed workflow for {name}")
    return ret
