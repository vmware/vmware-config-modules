# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

DATASTORE_TYPE = "vsan"
NON_COMPLIANT_DATASTORE_NAME = "vsanDatastore"
DATASTORE_NAME_KEY = "datastore_name"
CLUSTER_NAME_KEY = "cluster_name"
DATACENTER_NAME_KEY = "datacenter_name"


class DatastoreUniqueNamePolicy(BaseController):
    """Manage vSAN datastore name uniqueness with get and set methods.

    | Config Id - 420
    | Config Title - The vCenter Server must configure the vSAN Datastore name to a unique name.

    """

    metadata = ControllerMetadata(
        name="vsan_datastore_naming_policy",  # controller name
        path_in_schema="compliance_config.vcenter.vsan_datastore_naming_policy",  # path in the schema to this controller's definition.
        configuration_id="420",  # configuration id as defined in compliance kit.
        title="The vCenter Server must configure the vSAN Datastore name to a unique name.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """Get all vSAN datastore info.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of List of dicts with vSAN datastore info and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = self.__get_all_vsan_enabled_datastore_config(vc_vmomi_client)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    @staticmethod
    def __get_all_vsan_enabled_datastore_config(vc_vmomi_client: VcVmomiClient) -> List[Dict]:
        """Get all vSAN enabled datastore info from vCenter.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of dicts with datastore configs.
        :rtype: List
        """
        vsan_datastore_configs = []
        all_datacenter_refs = vc_vmomi_client.get_objects_by_vimtype(vim.Datacenter)
        logger.info(f"All datacenter mo-refs in vCenter {all_datacenter_refs}")

        for datacenter in all_datacenter_refs:
            if hasattr(datacenter, "datastore"):
                for datastore in datacenter.datastore:
                    if hasattr(datastore, "summary") and getattr(datastore, "summary"):
                        if hasattr(datastore.summary, "type") and getattr(datastore.summary, "type") == DATASTORE_TYPE:
                            if hasattr(datastore, "host") and datastore.host:
                                vsan_datastore_configs.append(
                                    {
                                        DATACENTER_NAME_KEY: getattr(datacenter, "name", ""),
                                        CLUSTER_NAME_KEY: getattr(datastore.host[0].key.parent, "name", ""),
                                        DATASTORE_NAME_KEY: getattr(datastore, "name", ""),
                                    }
                                )
        logger.info(f"Retrieved vSAN enabled cluster configs {vsan_datastore_configs}")
        return vsan_datastore_configs

    def set(self, context: VcenterContext, desired_values: bool) -> Tuple[str, List[Any]]:
        """Set will not be implemented until we have a proper remediation workflow is in place with fail safes
        and rollback mechanism.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: When set to true (the only allowed value), the audit process flags a datastore
         as non-compliant only if its name is 'vsanDatastore.' No other names are checked for compliance.
        :type desired_values: bool
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def check_compliance(self, context: VcenterContext, desired_values: bool) -> Dict:
        """Check compliance of datastore names among all vSAN-based datastores.

        | The audit process flags a datastore as non-compliant only if its name is 'vsanDatastore.'
            No other names are checked for compliance.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: When set to true (the only allowed value), the audit process flags a datastore as
         non-compliant only if its name is 'vsanDatastore.' No other names are checked for compliance.
        :type desired_values: bool
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        vsan_datastore_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_datastore_configs = [
            config
            for config in vsan_datastore_configs
            if config.get(DATASTORE_NAME_KEY) == NON_COMPLIANT_DATASTORE_NAME
        ]

        if non_compliant_datastore_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_datastore_configs,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
