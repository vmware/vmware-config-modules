# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client import VcVsanVmomiClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.utils.comparator import Comparator

logger = LoggerAdapter(logging.getLogger(__name__))

# HCL Proxy config constants
HCL_PROXY_DESIRED_KEYS_FOR_AUDIT = ["internet_access_enabled", "host", "port", "user"]


class VSANHCLProxyConfig(BaseController):
    """
    Manage vSAN proxy configuration for vSAN enabled clusters.

    | Config Id - 418
    | Config Title - Configure a proxy for the download of the public Hardware Compatibility List.

    """

    metadata = ControllerMetadata(
        name="vsan_proxy",  # controller name
        path_in_schema="compliance_config.vcenter.vsan_proxy",  # path in the schema to this controller's definition.
        configuration_id="418",  # configuration id as defined in compliance kit.
        title="Configure a proxy for the download of the public Hardware Compatibility List.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple:
        """
        Get vSAN proxy configuration for all cluster.

        | Sample get call output

        .. code-block:: json

            [
              {
                "host": "time.vmware.com",
                "port": 100,
                "user": "proxy_user_1",
                "internet_access_enabled": false,
                "cluster_name": "sfo-m01-cl01"
              },
              {
                "host": "abc.vmware.com",
                "port": 50,
                "user": "proxy_user_2",
                "internet_access_enabled": true,
                "cluster_name": "sfo-m01-cl02"
              },
              {
                "host": "time.vmware.com",
                "port": 60,
                "user": "proxy_user_3",
                "internet_access_enabled": false,
                "cluster_name": "sfo-m01-cl03"
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Returns tuple with dict of vSAN proxy configurations for each cluster and list of error messages.
        :rtype: Tuple
        """
        errors = []
        vc_vsan_vmomi_client = context.vc_vsan_vmomi_client()
        try:
            result = self.__get_proxy_config_for_all_vsan_clusters(vc_vsan_vmomi_client)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple:
        """
        Set vSAN proxy configuration for each cluster.

        | Sample desired state for proxy config.

        .. code-block:: json

            {
                "internet_access_enabled": true,
                "host": "hcl.vmware.com",
                "port": 80,
                "user": "proxy_user",
                "password": "super_complex_string"
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for vSAN cluster proxy configuration.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        errors = []
        status = RemediateStatus.SUCCESS
        vc_vsan_vmomi_client = context.vc_vsan_vmomi_client()
        try:
            self.__set_proxy_config_for_all_vsan_clusters(vc_vsan_vmomi_client, desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def __get_non_compliant_configs(self, current_configs: List, desired_config: Dict, desired_keys: List) -> List:
        """
        Retrieve a list of vSAN-enabled clusters with proxy configurations that do not comply with desired state.

        :param current_configs: List containing current proxy configurations for vSAN-enabled clusters.
        :type current_configs: List
        :param desired_config: Dictionary representing the desired values for proxy configuration.
        :type desired_config: Dict
        :param desired_keys: List of keys to be used for compliance checks.
        :type desired_keys: List
        :return: List of non-compliant proxy configurations for vSAN-enabled clusters.
        :rtype: List
        """
        logger.info("Get non-compliant cluster configurations")
        non_compliant_configs = []
        for config in current_configs:
            filtered_proxy_config = utils.filter_dict_keys(config, desired_keys)
            current, desired = Comparator.get_non_compliant_configs(filtered_proxy_config, desired_config)
            if current or desired:
                non_compliant_configs.append(config)
        return non_compliant_configs

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Check compliance of vSAN proxy configuration for all clusters.

        | Password is not considered during compliance check.
        | Password gets masked as (not shown) when we do a get call so we are ignoring this property from compliance
            check.But it is still used for remediation.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for vSAN proxy config.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        proxy_config_all_clusters, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        filtered_desired_config = utils.filter_dict_keys(desired_values, HCL_PROXY_DESIRED_KEYS_FOR_AUDIT)

        non_compliant_configs = self.__get_non_compliant_configs(
            current_configs=proxy_config_all_clusters,
            desired_config=filtered_desired_config,
            desired_keys=HCL_PROXY_DESIRED_KEYS_FOR_AUDIT,
        )
        if non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: filtered_desired_config,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Function to remediate configuration drifts.

        | Sample desired state for proxy config.

        .. code-block:: json

            {
                "internet_access_enabled": true,
                "host": "hcl.vmware.com",
                "port": 80,
                "user": "proxy_user",
                "password": "super_complex_string"
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for vSAN proxy config.
        :type desired_values: Dict
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running remediation")
        proxy_config_all_clusters, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        filtered_desired_config = utils.filter_dict_keys(desired_values, HCL_PROXY_DESIRED_KEYS_FOR_AUDIT)

        non_compliant_configs = self.__get_non_compliant_configs(
            current_configs=proxy_config_all_clusters,
            desired_config=filtered_desired_config,
            desired_keys=HCL_PROXY_DESIRED_KEYS_FOR_AUDIT,
        )
        if not non_compliant_configs:
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ["Control already compliant"]}

        status, errors = self.set(context=context, desired_values=desired_values)

        if not errors:
            result = {consts.STATUS: status, consts.OLD: non_compliant_configs, consts.NEW: filtered_desired_config}
        else:
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result

    def __set_proxy_config_for_all_vsan_clusters(
        self, vc_vsan_vmomi_client: VcVsanVmomiClient, desired_values: Dict
    ) -> None:
        """
        Set proxy configurations for all vSAN enabled clusters

        :param vc_vsan_vmomi_client: vSAN vmomi client.
        :type vc_vsan_vmomi_client: VcVsanVmomiClient
        :param desired_values: Desired values for vSAN cluster proxy configuration.
        :type desired_values: dict
        :return: None.
        """
        # get all vSAN enabled clusters
        all_vsan_enabled_clusters = vc_vsan_vmomi_client.get_all_vsan_enabled_clusters()
        for cluster_ref in all_vsan_enabled_clusters:
            cluster_proxy_config = vc_vsan_vmomi_client.get_vsan_cluster_health_config_for_cluster(cluster_ref)
            cluster_proxy_config.vsanTelemetryProxy.host = desired_values.get("host")
            cluster_proxy_config.vsanTelemetryProxy.port = desired_values.get("port")
            cluster_proxy_config.vsanTelemetryProxy.user = desired_values.get("user")
            cluster_proxy_config.vsanTelemetryProxy.password = desired_values.get("password")
            # Get Internet access config for cluster
            internet_access_config = vc_vsan_vmomi_client.get_vsan_config_by_key_for_cluster(
                "enableinternetaccess", cluster_ref
            )

            internet_access_config.value = "true" if desired_values.get("internet_access_enabled") else "false"
            cluster_proxy_config.configs.append(internet_access_config)
            # get vSAN health system
            vsan_health_system = vc_vsan_vmomi_client.get_vsan_health_system()
            vsan_health_system.SetVsanClusterTelemetryConfig(cluster_ref, cluster_proxy_config)

    def __get_proxy_config_for_all_vsan_clusters(self, vc_vsan_vmomi_client: VcVsanVmomiClient) -> List:
        """
        Get vsan proxy config for all vSAN enabled clusters

        :param vc_vsan_vmomi_client: vSAN vmomi client.
        :type vc_vsan_vmomi_client: VcVsanVmomiClient
        :return: List of proxy configurations for all clusters.
        :rtype: List
        """
        proxy_configs = []
        all_vsan_enabled_clusters = vc_vsan_vmomi_client.get_all_vsan_enabled_clusters()
        for cluster_ref in all_vsan_enabled_clusters:
            telemetry_proxy_config = vc_vsan_vmomi_client.get_vsan_proxy_config_for_cluster(cluster_ref)
            telemetry_proxy_config["cluster_name"] = cluster_ref.name
            proxy_configs.append(telemetry_proxy_config)
        return proxy_configs
