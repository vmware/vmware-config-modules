# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

GLOBAL_CONFIG = "global"


class VsanIscsiTargetsMchapConfig(BaseController):
    """
    Manage vsan iscsi targets mutual chap authentication configuration for vsan enabled clusters.

    | Config Id - 1212
    | Config Title - Configure Mutual CHAP for vSAN iSCSI targets.

    """

    metadata = ControllerMetadata(
        name="vsan_iscsi_targets_mutual_chap_config",  # controller name
        path_in_schema="compliance_config.vcenter.vsan_iscsi_targets_mutual_chap_config",
        # path in the schema to this controller's definition.
        configuration_id="1212",  # configuration id as defined in compliance kit.
        title="Configure Mutual CHAP for vSAN iSCSI targets",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple:
        """
        Get vSAN iSCSI configurations for all clusters.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Returns tuple with dict of vSAN iSCSI configurations for each cluster and list of error messages.
        :rtype: Tuple
        """
        logger.info("Get config")
        errors = []
        result = []
        vc_vsan_vmomi_client = context.vc_vsan_vmomi_client()
        try:
            # get all vsan enabled clusters
            all_vsan_enabled_clusters = vc_vsan_vmomi_client.get_all_vsan_enabled_clusters()
            for cluster_ref in all_vsan_enabled_clusters:
                # check vsan iscsi target service config (cluster level config)
                auth_type = vc_vsan_vmomi_client.get_vsan_iscsi_targets_auth_type_for_cluster(cluster_ref)
                if auth_type is not None:
                    result.append({f"{self.__get_dc_cluster_target_path(cluster_ref)}": auth_type})

                # check each individual targets
                if vc_vsan_vmomi_client.is_vsan_iscsi_targets_enabled_for_cluster(cluster_ref):
                    cluster_iscsi_targets = vc_vsan_vmomi_client.get_vsan_iscsi_targets_for_cluster()
                    iscsi_targets = cluster_iscsi_targets.GetIscsiTargets(cluster_ref)
                    for iscsi_target in iscsi_targets:
                        auth_type = iscsi_target.authSpec.authType
                        result.append(
                            {
                                f"{self.__get_dc_cluster_target_path(cluster_ref, target_name=iscsi_target.alias)}": auth_type
                            }
                        )

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """
        Set is not implemented for this control since modifying config would impact existing auth.
        Refer to Jira : VCFSC-202 and VCFSC-274

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired value for iscsi auth configuration
        :type desired_values: String or list of strings
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        :rtype: Tuple
        """

        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        logger.info(consts.REMEDIATION_SKIPPED_MESSAGE)
        status = RemediateStatus.SKIPPED
        return status, errors

    def __get_dc_cluster_target_path(self, cluster_ref, target_name=None) -> str:
        if target_name:
            return f"{cluster_ref.parent.parent.name}/{cluster_ref.name}/{target_name}"
        return f"{cluster_ref.parent.parent.name}/{cluster_ref.name}"

    def __get_auth_type_for_target(self, target_path, desired_values):
        # check exact path match
        auth_type = desired_values.get(target_path)
        if auth_type:
            return auth_type

        # check which level target it is
        path_component = target_path.split("/")
        if len(path_component) == 2:
            # cluster level default target
            return desired_values[GLOBAL_CONFIG]

        # target level target, need to check its parent path is no match
        cluster_target_path = "/".join(path_component[:-1])
        auth_type = desired_values.get(cluster_target_path)
        if auth_type:
            return auth_type

        return desired_values[GLOBAL_CONFIG]

    def __is_auth_type_match(self, current_config, desired_values):
        for target_path, auth_type in current_config.items():
            if auth_type == self.__get_auth_type_for_target(target_path, desired_values):
                return True

        return False

    def check_compliance(self, context, desired_values) -> Dict:
        """

        Check compliance of vsan iscsi targets config in vCenter server. If no clusters are enabled for vSAN or
        if vSAN is enabled but iSCSI is not enabled, this is not applicable (compliant). If iscsi targets is
        enabled, mutual chap should be configured as authentication type.
        The desired value is for remediation.

        | Sample desired_values spec

        .. code-block:: json

            {
                'global': 'CHAP_Mutual',
                'SDDC-Datacenter/SDDC-Cluster1': 'CHAP_Mutual',
                'SDDC-Datacenter/SDDC-Cluster1/target_01': 'CHAP_Mutual'
            }

        :param context: Product context instance.
        :param desired_values: Desired value for iscsi auth configuration.
        :return: Dict of status and current/desired value or errors (for failure).
        :rtype: dict
        """
        logger.info("Checking compliance")
        current_configs, errors = self.get(context=context)
        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        for current_config in current_configs:
            if not self.__is_auth_type_match(current_config, desired_values):
                result = {
                    consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                    consts.CURRENT: current_configs,
                    consts.DESIRED: desired_values,
                }
                return result

        result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
