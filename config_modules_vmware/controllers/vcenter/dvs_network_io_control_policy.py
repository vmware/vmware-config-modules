# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.controllers.vcenter.utils.vc_dvs_utils import is_host_disconnect_exception
from config_modules_vmware.controllers.vcenter.utils.vc_dvs_utils import is_host_exception
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient
from config_modules_vmware.framework.clients.vcenter.vc_rest_client import VcRestClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

logger = LoggerAdapter(logging.getLogger(__name__))

# Constants
DESIRED_KEY = "network_io_control_status"
SWITCH_NAME = "switch_name"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"
OFFLOAD_NONE = "None"
IGNORE_DISCONNECTED_HOSTS = "ignore_disconnected_hosts"
IGNORE_HOST_EXCEPTION = "ignore_host_exception"


class DVSNetworkIOControlPolicy(BaseController):
    """Manage DV Switch Network I/O control policy with get and set methods.

    | Config Id - 409
    | Config Title - The vCenter Server must manage excessive bandwidth and Denial of Service (DoS) attacks by enabling
        Network I/O Control (NIOC).

    """

    metadata = ControllerMetadata(
        name="dvs_network_io_control",  # controller name
        path_in_schema="compliance_config.vcenter.dvs_network_io_control",  # path in the schema to this controller's definition.
        configuration_id="409",  # configuration id as defined in compliance kit.
        title="The vCenter Server must manage excessive bandwidth and Denial of Service (DoS) attacks by enabling Network I/O Control (NIOC).",
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

    def get(self, context: VcenterContext) -> Tuple[List[Dict], List[Any]]:
        """
        Get DVS Network I/O control policy for all DV switches.

        | Sample get output

        .. code-block:: json

            [
              {
                "switch_name": "SwitchB",
                "network_io_control_status": false
              },
              {
                "switch_name": "SwitchC",
                "network_io_control_status": true
              },
              {
                "switch_name": "SwitchA",
                "network_io_control_status": false
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of DV switch network I/O control policy and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        vc_rest_client = context.vc_rest_client()
        errors = []
        try:
            result = self.__get_all_dv_switches_by_tag(vc_vmomi_client, vc_rest_client)
        
        
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set Network I/O control policy for all DV switches.

        | Sample desired state

        .. code-block:: json

            {
              "__GLOBAL__": {
                "network_io_control_status": false
              },
              "__OVERRIDES__": [
                {
                  "switch_name": "Switch-A",
                  "network_io_control_status": true
                }
              ],
              "ignore_disconnected_hosts": true
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for enabling/disabling Network I/O control policy.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        pass  # pylint: disable=unnecessary-pass

    def __get_all_dvswitches(self, vc_vmomi_client: VcVmomiClient):
            """Retrieve all distributed virtual switches."""
            logger.info("\nEnumerating dvSwitches...")
            all_dv_switches = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualSwitch)

            logger.info(f"Found {len(all_dv_switches)} dvSwitch(es)")
            return all_dv_switches

    def __get_all_dvswitches_by_tag(self, vc_vmomi_client: VcVmomiClient, vc_rest_client: VcRestClient):
        """Retrieve all distributed virtual switches."""

        result_list = []

        logger.info("\nEnumerating dvSwitches...")
        result = self.__get_dvswitch_tag_mappings(vc_vmomi_client, vc_rest_client)
        logger.info(f"Found: {result}")

        for mapping in result:
            dvSwitch = mapping.get("switch_name", "")
            nioc_status = mapping.get("nioc_status", "")
            clusters = mapping.get("clusters", "")
            result_list.append({"switch_name": dvSwitch, "nioc_status": nioc_status, "clusters": clusters})

        logger.info(f"result_list: {result_list}")
        return result_list

    def __get_clusters_for_dvswitch(self, dvswitch):
        """Get all clusters associated with a dvSwitch."""
        clusters = {}

        if not hasattr(dvswitch.config, 'host') or not dvswitch.config.host:
            return clusters

        for host_member in dvswitch.config.host:
            try:
                host = host_member.config.host

                if host and host.parent:
                    parent = host.parent

                    # Check if parent is a cluster
                    if isinstance(parent, vim.ClusterComputeResource):
                        cluster_name = parent.name
                        cluster_moid = parent._moId

                        if cluster_name not in clusters:
                            clusters[cluster_name] = {
                                'object': parent,
                                'moid': cluster_moid,
                                'hosts': []
                            }

                        clusters[cluster_name]['hosts'].append(host.name)

            except Exception as e:
                logger.info(f"Warning: Error processing host: {e}")
                continue

        return clusters


    def __get_dvswitch_tag_mappings(self, vc_vmomi_client: VcVmomiClient, vc_rest_client: VcRestClient) -> List[Dict]:
        """Main method to map all dvSwitches to cluster tags."""
        mapping = []

        # Get all dvSwitches
        dvswitches = self.__get_all_dvswitches(vc_vmomi_client)

        for dvs in dvswitches:
            dvs_name = dvs.name
            dvs_uuid = dvs.uuid
            network_io_control_status = dvs.config.networkResourceManagementEnabled

            logger.info(f"\nProcessing dvSwitch: {dvs_name}")

            # Get clusters for this dvSwitch
            clusters = self.__get_clusters_for_dvswitch(dvs)

            if not clusters:
                logger.info(f"No clusters found for {dvs_name}")
                switch_obj = {
                    'switch_name': dvs_name,
                    'uuid': dvs_uuid,
                    'nioc_status': network_io_control_status,
                    'clusters': [],
                    'all_tags': []
                }
                mapping.append(switch_obj)
                continue

            logger.info(f"Found {len(clusters)} cluster(s): {', '.join(clusters.keys())}")

            # Get tags for each cluster
            cluster_info = []
            all_tags = {}

            for cluster_name, cluster_data in clusters.ietms():
                logger.info(f"retrieving tags for cluster: {cluster_name}")

                tags = self..__get_tags_for_cluster(cluster_data['moid'], vc_rest_client)

                cluster_info.append({
                    'cluster_name': cluster_name,
                    'cluster_moid': cluster_data['moid'],
                    'host_count': len(cluster_data['hosts']),
                    'hosts': cluster_data['hosts'],
                    'tags': tags
                })

                #Aggregate unique tags
                for tag in tags:
                    tag_key = f"{tag['category_name']}:{tag['tag_name']}"
                    if tag_key not in all tags:
                        all_tags[tag_key] = {
                            'tag_name': tag['tag_name'],
                            'category_name': tag['category_name'],
                            'description': tag['description'],
                            'clusters': []
                        }
                    all_tags[tag_key]['clusters'].append(cluster_name)
                
                logger.debug(f"Found {len(tags)} tag(s)")

                switch_obj - {
                    'switch_name': dvs_name,
                    'uuid': dvs_uuid,
                    'nioc_status': network_io_control_status,
                    'clusters': cluster_info,
                    'all_tags': list(all_tags.values())
                }
                mapping.append(switch_obj)
            logger.info(f"Mapping: {mapping}")
            return mapping

    def __get_tag_info(self, tag_id, vc_rest_client: VcRestClient) -> List[Dict]:
        tag_url = vc_rest_client.get_base_url() + f"api/cis/tagging/tag/{tag_id}"

        try:
            tag_data = vc_rest_client.get_helper(tag_url, raise_for_status=True)
            logger.info(f"tag_info: {tag_data}")
            cat_url = vc_rest_client.get_base_url() + f"api/cis/tagging/category/{tag_data['category_id']}"
            cat_data = vc_rest_client.get_helper(cat_url, raise_for_status=True)
            logger.info(f"tag_category: {cat_data}")
            cat_name = cat_data["name"]
        except:
            logger.info(f"Warning: could not retrieve tag details{tag_id}: {e}")

            return {
                "tag_id": tag_id,
                "tag_name": tag_data["name"],
                "category_name": cat_name,
                "description": tag_data.get("description:", "").strip() or "-"
            }


    def __get_tags_for_cluster(self, cluster_moid, vc_rest_client: VcRestClient) -> List[Dict]
        """Retrieve all tags attached to a cluster. """
        tags = []


        try:
            #get tag-associations from vCenter
            url = vc_rest_client.get_base_url() + 'api/cis/tagging/tag-association?action=list-attached-tags'
            payload = {"object_id":{"id": cluster_moid, "type":"ClusterComputeResource"}}
            tag_ids_resp = vc_rest_client.post_helper(url, body=payload, raise_for_status=True)

            #Get all tags attached to this cluster
            for tag_id in tag_ids_resp:
                try:
                    logger.debug(f"Getting tag info for: {tatg_id}")
                    tag_info = self.__get_tag_info(tag_id, vc_rest_client)
                    logger.debug(f"Tag Details: {tag_info}")
                    tags.append(tag_info)

                except Exception as e:
                    logger.info(f"Warning: Could not retrieve tag  {tag_id}: {e}")
                    continue

        except:
            logger.info(f"Warning: Could not retrieve tags for cluster {cluster_moid}: {e}")

        logger.info(f"Tags: {tags}")
        return tags

    def __get_all_dv_switch_network_io_control_policy(self, vc_vmomi_client: VcVmomiClient) -> List[Dict]:
        """
        Get Network I/O control policy for all DV Switches.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List of Network I/O control policy for all DV switches.
        :rtype: List
        :return:
        """
        dv_switch_network_io_control_configs = []
        all_dv_switches = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualSwitch)

        for dvs in all_dv_switches:
            network_io_control_status = {
                SWITCH_NAME: dvs.name,
                DESIRED_KEY: dvs.config.networkResourceManagementEnabled,
            }
            dv_switch_network_io_control_configs.append(network_io_control_status)
        return dv_switch_network_io_control_configs

    def __set_network_io_control_policy_for_all_dv_switches(
        self, vc_vmomi_client: VcVmomiClient, desired_values: Dict
    ) -> Tuple[List[dict], List[dict], List[str]]:
        """
        Enable or disable Network I/O control policy for all dv switches.

        | Recommended value for network I/O control: true | enabled
        | Sample desired state

        .. code-block:: json

            {
              "network_io_control_status": [              
                {
                "cluster_tag": "cluster_type",
                "tag_value": "edge",
                "network_io_control_status": false
                },
                {
                "cluster_tag": "cluster_type",
                "tag_value": "management",
                "network_io_control_status": true
                },
                {
                "cluster_tag": "cluster_type",
                "tag_value": "tenant",
                "network_io_control_status": true
                },
                {
                "cluster_tag": "cluster_type",
                "tag_value": "micro",
                "network_io_control_status": true
                }
                ],
              "ignore_disconnected_hosts": true
            }

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :param desired_values: Desired values for Network I/O control policy.
        :type desired_values: Dict
        :return: list of previous and current configs and list of errors if any
        :rtype: Tuple
        """
        errors = []
        previous = []
        current = []

        desired_global_network_io_control_value = desired_values.get(DESIRED_KEY,{})
        overrides = desired_global_network_io_control_value

        ignore_disconnected_hosts = desired_values.get(IGNORE_DISCONNECTED_HOSTS, False)
        ignore_host_exception = desired_values.get(IGNORE_HOST_EXCEPTION, False)
        # desired_network_io_control_value = desired_values.get(DESIRED_KEY)
        try:
            all_switch_refs = vc_vmomi_client.get_objects_by_vimtype(vim.DistributedVirtualSwitch)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            return [], [], errors

        for dvs_ref in all_switch_refs:
            # Check if there are overrides for the current DVS
            override_health_check_value = next(
                (switch.get(DESIRED_KEY) for switch in overrides if switch[SWITCH_NAME] == dvs_ref.name),
                None,
            )
            current_network_io_control_value = dvs_ref.config.networkResourceManagementEnabled
            desired_network_io_control_value = (
                override_health_check_value
                if override_health_check_value is not None
                else desired_global_network_io_control_value
            )

            if current_network_io_control_value == desired_network_io_control_value:
                logger.info(
                    f"DV switch {dvs_ref.name} already has desired network I/O control config," f" skipping remediation"
                )
            else:
                # Check if network offload is enabled, if yes, skip remediation
                if (
                    hasattr(dvs_ref.config, "networkOffloadSpecId")
                    and dvs_ref.config.networkOffloadSpecId is not None
                    and dvs_ref.config.networkOffloadSpecId != OFFLOAD_NONE
                ):
                    offload = dvs_ref.config.networkOffloadSpecId
                    err_msg = f"Network offload - {offload} enabled for: {dvs_ref.name}, skip remediation"
                    logger.warning(err_msg)
                    errors.append(err_msg)
                else:
                    logger.info(
                        f"Setting network I/O control config {desired_network_io_control_value} on DV "
                        f"switch {dvs_ref.name}"
                    )
                    try:
                        dvs_ref.EnableNetworkResourceManagement(desired_network_io_control_value)
                        previous.append({SWITCH_NAME: dvs_ref.name, DESIRED_KEY: current_network_io_control_value})
                        current.append({SWITCH_NAME: dvs_ref.name, DESIRED_KEY: desired_network_io_control_value})
                    except vim.fault.DvsOperationBulkFault as e:
                        if is_host_disconnect_exception(e) and ignore_disconnected_hosts:
                            previous.append({SWITCH_NAME: dvs_ref.name, DESIRED_KEY: current_network_io_control_value})
                            current.append({SWITCH_NAME: dvs_ref.name, DESIRED_KEY: desired_network_io_control_value})
                            logger.info(f"Ignore disconnected hosts caused exception - {e}")
                        elif is_host_exception(e) and ignore_host_exception:
                            logger.info(f"Ignore all host caused exception - {e}")
                            previous.append({SWITCH_NAME: dvs_ref.name, DESIRED_KEY: current_network_io_control_value})
                            current.append({SWITCH_NAME: dvs_ref.name, DESIRED_KEY: desired_network_io_control_value})
                        else:
                            logger.exception(f"An error occurred: {e}")
                            errors.append(str(e))
                    except Exception as e:
                        logger.exception(f"An error occurred: {e}")
                        errors.append(str(e))
        return previous, current, errors

    def __get_non_compliant_configs(self, switch_configs: List, desired_values: Dict) -> Tuple[List, List]:
        """
        Get all non-compliant items for the given desired state spec.

        :return:
        :meta private:
        """

        logger.debug(f"desired_values: {desired_values}")
        logger.debug(f"switch_configs: {switch_configs}")
        non_compliant_items = []
        invalid_items -[]
        desired_configs = []

        # convert to dictionary for easy access
        configs_by_switch_name = {config.get(SWITCH_NAME): config for config in switch_configs}
        logger.debug(f"Checking: {configs_by_switch_name}")

        #global_desired_value = desired_values.get(GLOBAL, {}).get(DESIRED_KEY)
        global_desired_value = desired_values.get(DESIRED_KEY,{})
        logger.info(f"global_desired_value {global_desired_value}"),
        overrides = global_desired_value
        logger.debug(f"Overrides {overrides}")

        #Build tag mapping from overrides
        tag_mapping = {}
        for override in overrides:
            tag_name = override.get("tag_value", None)
            nioc_status = override.get("network_io_control_status", None)
            if tag_name is not None and nioc_status is not None:
                tag_mapping[tag_name] - nioc_status

        logger.debug(f"tag_mapping" {tag_mapping})



        for config in switch_configs:
            found_tag = False
            logger.debug(f"config: {config}")
            if not config.get("clusters"):
                logger.info(f"Skipping switch {config.get('switch_name')} as no clusters are associated")
                continue
            for tag in config["clusters"][0]["tags"]:
                logger.debug(f"tag: {tag}")
                tag_name = tag.get("tag_name", None)
                if tag_name in tag_mapping:
                    logger.debug(f"Found tag {tag_name}")
                    found_tag = true
                    desired_nioc = tag_mapping[tag_name]
                    if desired_nioc != config["nioc_status"]:
                        non_compliant_items.append({SWITCH_NAME: config["switch_name"], DESIRED_KEY: config["nioc_status"]})
                        desired_configs.append({SWITCH_NAME: config["switch_name"], DESIRED_KEY: desired_nioc})
            logger.debug(f"non_compliant_items: {non_compliant_items}")
            if not found_tag:
                invalid_items.append({SWITCH_NAME: config["switch_name"], DESIRED_KEY: config["nioc_status"]})

        logger.debug(f"non_compliant_items: {non_compliant_items}")
        
        return non_compliant_items, invalid_items, desired_configs

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Check compliance of Network I/O control policy for all DV switches.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for network I/O control policy.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        dv_switch_network_io_control_configs, errors = self.get(context=context)
        invalid_items = []

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs, invalid_items, desired_configs = self.__get_non_compliant_configs(
            dv_switch_network_io_control_configs, desired_values
        )


        if len(invalid_items) > 0:
            result = {
                consts.STATUS: ComplianceStatus.FAILED,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: desired_configs,
                const.ERRORS: f"Failed to validate NIOC settings. No matching tags found for: {invalid_items}"
            }
        elif non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: desired_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Remediate configuration drifts by applying desired values.

        | Sample desired state for remediation.

        .. code-block:: json

            {
              "__GLOBAL__": {
                "network_io_control_status": false
              },
              "__OVERRIDES__": [
                {
                  "switch_name": "Switch-A",
                  "network_io_control_status": false
                }
              ],
              "ignore_disconnected_hosts": true
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for Network I/O control for DV switches.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Remediation is not implemented. Manual intervention is required")
        errors = [consts.REMEDIATION_SKIPPED_MESSAGE]
        return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: errors}