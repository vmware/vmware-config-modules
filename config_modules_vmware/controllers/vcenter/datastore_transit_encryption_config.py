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
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

DATA_IN_TRANSIT_ENCRYPTION_CONFIG_PYVMOMI_KEY = "dataInTransitEncryptionConfig"
REKEY_INTERVAL_PYVMOMI_KEY = "rekeyInterval"
ENABLED_PYVMOMI_KEY = "enabled"
CLUSTER_NAME_KEY = "cluster_name"
TRANSIT_ENCRYPTION_ENABLED = "transit_encryption_enabled"
REKEY_INTERVAL_KEY = "rekey_interval"
DATA_CENTER_NAME_KEY = "datacenter_name"
PER_HOST_TASK_TIMEOUT = 10
BASE_TASK_TIMEOUT = 30


class DatastoreTransitEncryptionPolicy(BaseController):
    """Manage data in transit encryption policy for vSAN clusters with get and set method.

    | Config Id - 0000
    | Config Title - Configure Data in Transit Encryption Keys to be re-issued at regular intervals
        for the vSAN Data in Transit encryption enabled clusters.

    """

    metadata = ControllerMetadata(
        name="vsan_datastore_transit_encryption_config",  # controller name
        path_in_schema="compliance_config.vcenter.vsan_datastore_transit_encryption_config",
        # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Configure Data in Transit Encryption Keys to be re-issued at regular intervals "
        "for the vSAN Data in Transit encryption enabled clusters.",  # controller title.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """Get transit encryption policy for all encrypted vSAN based clusters.

        | Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
            Support for version 5xxx will be added soon.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of List of dicts with transit encryption policy and a list of error messages.
        :rtype: Tuple
        """
        errors = []
        try:
            result = self.__get_rekey_interval_encryption_policy_for_vsan_clusters(context)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def __get_transit_encryption_config_for_clusters(self, context: VcenterContext) -> List[Tuple]:
        """Helper method to get all encrypted vSAN clusters and their data in transit encryption configuration.

        :param context: VC product context instance.
        :type context: VcenterContext
        :return: List of tuple of cluster refs and their transit encryption configurations.
        :rtype: List
        """
        data_in_transit_encryption_configs = []
        vc_vsan_vmomi_client = context.vc_vsan_vmomi_client()

        vsan_clusters = vc_vsan_vmomi_client.get_all_vsan_enabled_clusters()
        logger.info(f"Retrieved all vSAN enabled clusters {vsan_clusters}")

        vsan_ccs = vc_vsan_vmomi_client.get_vsan_cluster_config_system()
        logger.info(f"Retrieved vSAN cluster config system {vsan_ccs}")

        for cluster_ref in vsan_clusters:
            vsan_cluster_config = vsan_ccs.VsanClusterGetConfig(cluster_ref)
            data_in_transit_encryption_config = getattr(
                vsan_cluster_config, DATA_IN_TRANSIT_ENCRYPTION_CONFIG_PYVMOMI_KEY, None
            )
            if data_in_transit_encryption_config:
                data_in_transit_encryption_configs.append((cluster_ref, data_in_transit_encryption_config))

        logger.debug(
            f"Retrieved transit encryption configs for vSAN data in transit encryption enabled"
            f" clusters {data_in_transit_encryption_configs}"
        )
        return data_in_transit_encryption_configs

    def __get_rekey_interval_encryption_policy_for_vsan_clusters(self, context: VcenterContext) -> List[Dict]:
        """Get transit encryption policy for all encryption enabled vSAN clusters.

        :param context: VC product context instance.
        :type context: VcenterContext
        :return: List of dicts with transit encryption policies for all vSAN encryption enabled clusters.
        :rtype: List
        """
        all_cluster_transit_encryption_configs = []
        data_in_transit_encryption_configs = self.__get_transit_encryption_config_for_clusters(context)
        vc_vmomi_client = context.vc_vmomi_client()

        for cluster_ref, transit_encryption_config in data_in_transit_encryption_configs:
            cluster_transit_encryption_config = {}
            is_enabled = getattr(transit_encryption_config, ENABLED_PYVMOMI_KEY, None)
            rekey_interval = getattr(transit_encryption_config, REKEY_INTERVAL_PYVMOMI_KEY, None)
            datacenter_obj = vc_vmomi_client.find_datacenter_for_obj(cluster_ref)
            data_center_name = getattr(datacenter_obj, "name", "")
            cluster_transit_encryption_config[DATA_CENTER_NAME_KEY] = data_center_name
            cluster_transit_encryption_config[CLUSTER_NAME_KEY] = cluster_ref.name
            cluster_transit_encryption_config[TRANSIT_ENCRYPTION_ENABLED] = is_enabled
            cluster_transit_encryption_config[REKEY_INTERVAL_KEY] = rekey_interval
            all_cluster_transit_encryption_configs.append(cluster_transit_encryption_config)

        logger.info(
            f"Retrieved transit encryption configs for all vSAN data in transit encryption enabled"
            f" clusters {all_cluster_transit_encryption_configs}"
        )
        return all_cluster_transit_encryption_configs

    def __set_transit_encryption_config_for_vsan_clusters(self, context: VcenterContext, desired_values: dict) -> None:
        """Set transit encryption policy for all vSAN enabled clusters.

        :param context: VC product context.
        :type context: VcenterContext
        :param desired_values: Desired values for transit encryption policy.
        :type desired_values: dict
        :return: None.
        """
        vc_vsan_vmomi_client = context.vc_vsan_vmomi_client()
        vc_vmomi_client = context.vc_vmomi_client()

        data_in_transit_encryption_configs = self.__get_transit_encryption_config_for_clusters(context)
        vsan_ccs = vc_vsan_vmomi_client.get_vsan_cluster_config_system()

        for cluster_ref, transit_encryption_config in data_in_transit_encryption_configs:
            current_is_enabled = getattr(transit_encryption_config, ENABLED_PYVMOMI_KEY, None)
            current_rekey_interval = getattr(transit_encryption_config, REKEY_INTERVAL_PYVMOMI_KEY, None)

            desired_is_enabled = desired_values.get(TRANSIT_ENCRYPTION_ENABLED)
            desired_rekey_interval = desired_values.get(REKEY_INTERVAL_KEY)
            if (
                current_is_enabled is not None
                and current_rekey_interval is not None
                and current_is_enabled == desired_is_enabled
                and current_rekey_interval == desired_rekey_interval
            ):
                logger.info(
                    f"Cluster {cluster_ref.name} already has desired transmit encryption configs"
                    f" is_enabled {current_is_enabled} rekey_interval {current_rekey_interval}"
                )
            else:
                # Reconfig spec
                cluster_reconfig_spec = vim.vsan.ReconfigSpec()
                cluster_reconfig_spec.dataInTransitEncryptionConfig = vim.vsan.DataInTransitEncryptionConfig()
                cluster_reconfig_spec.dataInTransitEncryptionConfig.enabled = desired_is_enabled
                cluster_reconfig_spec.dataInTransitEncryptionConfig.rekeyInterval = desired_rekey_interval
                # reconfigure vSAN cluster
                encryption_config_task = vsan_ccs.ReconfigureEx(cluster_ref, cluster_reconfig_spec)
                vc_task = vc_vsan_vmomi_client.convert_vsan_to_vc_task(encryption_config_task)
                # Set timeout based on number of hosts in cluster
                task_timeout = len(cluster_ref.host) * PER_HOST_TASK_TIMEOUT if cluster_ref.host else BASE_TASK_TIMEOUT
                vc_vmomi_client.wait_for_task(vc_task, timeout=task_timeout)

    def set(self, context: VcenterContext, desired_values: dict) -> Tuple[str, List[Any]]:
        """Set transit encryption policy for encryption enabled vSAN clusters.

        | Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
            Support for version 5xxx will be added soon.

        | Sample desired state for transit encryption policy. Rekey interval range lies
            between 30 minutes - 10080 (7 days).

        .. code-block:: json

            {
                "rekey_interval": 30,
                "transit_encryption_enabled": true
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for transit encryption policy.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            self.__set_transit_encryption_config_for_vsan_clusters(context, desired_values)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context: VcenterContext, desired_values: dict) -> Dict:
        """Check transit encryption policy compliance for encrypted vSAN enabled clusters.

        | Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
            Support for version 5xxx will be added soon.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for transit encryption policy.
        :type desired_values: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        cluster_rekey_policies, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs = [
            config
            for config in cluster_rekey_policies
            if config.get(REKEY_INTERVAL_KEY) != desired_values.get(REKEY_INTERVAL_KEY)
            or config.get(TRANSIT_ENCRYPTION_ENABLED) != desired_values.get(TRANSIT_ENCRYPTION_ENABLED)
        ]

        if non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: desired_values,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: VcenterContext, desired_values: dict) -> Dict:
        """Remediate transit encryption policy drifts on encryption enabled vSAN based clusters.

        | Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
            Support for version 5xxx will be added soon.

        | Sample desired state for transit encryption policy. Rekey interval range
            lies between 30 minutes - 10080 (7 days).

        .. code-block:: json

            {
                "rekey_interval": 30,
                "transit_encryption_enabled": true
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for transit encryption policy.
        :type desired_values: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running remediation")
        cluster_rekey_policies, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs = [
            config
            for config in cluster_rekey_policies
            if config.get(REKEY_INTERVAL_KEY) != desired_values.get(REKEY_INTERVAL_KEY)
            or config.get(TRANSIT_ENCRYPTION_ENABLED) != desired_values.get(TRANSIT_ENCRYPTION_ENABLED)
        ]

        if not non_compliant_configs:
            return {consts.STATUS: RemediateStatus.SUCCESS}

        status, errors = self.set(context=context, desired_values=desired_values)

        if not errors:
            result = {consts.STATUS: status, consts.OLD: non_compliant_configs, consts.NEW: desired_values}
        else:
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result
