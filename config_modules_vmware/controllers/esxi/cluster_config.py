# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.esxi.utils import cluster_config_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import EsxiContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.models.utils import drift_utils
from config_modules_vmware.services.config import Config

logger = LoggerAdapter(logging.getLogger(__name__))

DESIRED_STATE_SCAN_URL = "api/esx/settings/clusters/{}/configuration?action=checkCompliance&vmw-task=true"


class ClusterConfig(BaseController):
    """
    Class for managing desired config of an ESX cluster.
    """

    metadata = ControllerMetadata(
        name="cluster_config",  # controller name
        path_in_schema="",  # path in the schema to this controller's definition.
        configuration_id="-1",  # configuration id as defined in compliance kit.
        title="ESX cluster configuration",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        type=ControllerMetadata.ControllerType.CONFIGURATION,
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def __init__(self):
        super().__init__()
        self.esx_cluster_config = Config.get_section("esx.cluster.config")

    def get(self, context: EsxiContext, template: dict = None) -> Tuple[dict, List[str]]:
        """Get - NOT IMPLEMENTED.

        :param context: Product context instance.
        :type context: EsxiContext
        :param template: Template of requested properties to populate
        :type template: dict
        :return: Tuple of the ESXi Cluster config and list of error messages.
        :rtype: tuple
        """

        return {}, [consts.SKIPPED]

    def set(self, context: EsxiContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """
        Set - NOT IMPLEMENTED.
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        status = RemediateStatus.SKIPPED
        return status, errors

    def check_compliance(self, context: EsxiContext, desired_values: str) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: EsxiContext
        :param desired_values: The cluster moid to target
        :type desired_values: str
        :return: Dict of status and result (for non_compliant) or errors (for failure).
        :rtype: dict
        """

        errors = []
        task_id = None
        task_response = None
        cluster_moid = desired_values

        try:
            # Invoke check compliance esx cluster config API
            try:
                logger.info(f"Initiating check_compliance on esx cluster: {cluster_moid}")
                task_id = context.vc_rest_client().post_helper(
                    url=context.vc_rest_client().get_base_url() + DESIRED_STATE_SCAN_URL.format(cluster_moid),
                )
            except Exception as e:
                logger.error(f"An error occurred in 'check_compliance' cluster_config: {e}")
                errors.append(
                    drift_utils.create_error(
                        BaseContext.ProductEnum.VCENTER,
                        str(e),
                        context.hostname,
                        context.vc_rest_client().get_base_url() + DESIRED_STATE_SCAN_URL.format(cluster_moid),
                    )
                )
            # Monitor task until completion.
            if task_id:
                try:
                    logger.info(f"check_compliance initiated on esx cluster: {cluster_moid}, task id: {task_id}")
                    task_response = context.vc_rest_client().wait_for_cis_task_completion(
                        task_id=task_id,
                        retry_wait_time=self.esx_cluster_config.getint("TaskPollIntervalSeconds"),
                        timeout=self.esx_cluster_config.getint("TaskTimeoutSeconds"),
                    )
                except Exception as e:
                    logger.error(f"An error occurred in polling cluster_config 'check_compliance' task: {e}")
                    errors.append(
                        drift_utils.create_error(
                            BaseContext.ProductEnum.VCENTER,
                            str(e),
                            context.hostname,
                            context.vc_rest_client().get_base_url() + vc_consts.CIS_TASKS_URL.format(task_id),
                        )
                    )
        except Exception as e:
            logger.error(f"An error occurred for 'check_compliance' cluster_config: {str(e)}")
            errors.append(
                drift_utils.create_error(
                    drift_utils.source_type_config_module,
                    str(e),
                )
            )

        # Transform API result into drift spec schema format.
        return cluster_config_utils.transform_to_drift_schema(context, cluster_moid, task_id, task_response, errors)

    def remediate(self, context: EsxiContext, desired_values: Dict) -> Dict:
        """
        Remediate - NOT IMPLEMENTED.
        """
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        logger.info(f"{consts.REMEDIATION_SKIPPED_MESSAGE}")
        result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}
        return result
