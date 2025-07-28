# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401
from pyVmomi import vmodl  # pylint: disable=E0401

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

# Constants
DESIRED_KEY = "migrate_encryption_policy"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"
VM_NAME = "vm_name"
PATH = "path"
EXCLUDE_THIS_VM = "exclude"


class VmMigrateEncryptionPolicy(BaseController):
    """Manage VM migrate Encryption policy with get and set methods.

    | Config Id - 1234
    | Config Title - Encryption must be enabled for vMotion on the virtual machine.

    """

    metadata = ControllerMetadata(
        name="vm_migrate_encryption",  # controller name
        path_in_schema="compliance_config.vcenter.vm_migrate_encryption",  # path in the schema to this controller's definition.
        configuration_id="1234",  # configuration id as defined in compliance kit.
        title="Encryption must be enabled for vMotion on the virtual machine.",  # controller title as defined in compliance kit.
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
        Get VM migrate Encryption policy for all Virtual Machines.

        | Sample Get call output

        .. code-block:: json

            [
              {
                "vm_name": "nsx-mgmt-1",
                "path": "SDDC-Datacenter/vm",
                "migrate_encryption_policy": "opportunistic"
              },
              {
                "vm_name": "sddc-manager",
                "path": "SDDC-Datacenter/vm/Management VMs",
                "migrate_encryption_policy": "opportunistic"
              },
              {
                "vm_name": "ms-sql-replica-1",
                "path": "SDDC-Datacenter/vm/database_workloads/ms-sql",
                "migrate_encryption_policy": "disabled"
              },
              {
                "vm_name": "ms-sql-replica-2",
                "path": "SDDC-Datacenter/vm/database_workloads/ms-sql",
                "migrate_encryption_policy": "required"
              },
              {
                "vm_name": "ubuntu-dev-box",
                "path": "SDDC-Datacenter/vm/dev",
                "migrate_encryption_policy": "opportunistic"
              },
              {
                "vm_name": "vcenter-1",
                "path": "SDDC-Datacenter/vm/Management VMs",
                "migrate_encryption_policy": "opportunistic"
              }
            ]

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of list of dicts with migrate encryption policies for VMs and a list of error messages.
        :rtype: Tuple
        """
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        try:
            result = self.__get_all_vm_migrate_encryption_policy(vc_vmomi_client)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            result = []
        return result, errors

    def set(self, context: VcenterContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set VM migrate Encryption policies for all Virtual machines.
        If a VM is "template", mark it as "VM" before remediation, and mark it
        back to "template" after remediation.

        | Recommended value for migrate encryption: "opportunistic" | "required"
        | Supported values: ["disabled", "opportunistic", "required"].

        | Disabled: Do not use encrypted vMotion, even if available.

        | Opportunistic: Use encrypted vMotion if source and destination hosts support it,
            fall back to unencrypted vMotion otherwise. This is the default option.

        | Required: Allow only encrypted vMotion. If the source or destination host does not support vMotion encryption,
            do not allow the vMotion to occur.

        | Sample desired state

        .. code-block:: json

            {
              "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
              },
              "__OVERRIDES__": [
                {
                  "vm_name": "sddc-manager",
                  "path": "SDDC-Datacenter/vm/Management VMs",
                  "migrate_encryption_policy": "required"
                },
                {
                  "vm_name": "nsx-mgmt-1",
                  "path": "SDDC-Datacenter/vm/Networking VMs",
                  "migrate_encryption_policy": "required"
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VM migration Encryption policy.
        :type desired_values: Dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        pass  # pylint: disable=unnecessary-pass

    def _vm_name_check(self, vm_name: str, exclude_vm_names: List) -> bool:
        """
        Check if a given vm name matches any name/pattern in exclude list.

        :param vm_name: vm name.
        :type vm_name: str
        :param exclude_vm_names: a list of vm names/patterns to compare.
        :type exclude_vm_names: List
        :return: True if vm_name matches any name or pattern in exclude list
        :rtype: bool
        """
        for exclude_vm_name in exclude_vm_names:
            if re.match(exclude_vm_name, vm_name, re.IGNORECASE):
                logger.debug(f"VM name: {vm_name} -match-: {exclude_vm_name}")
                return True
        return False

    def _filter_vm_configs(self, all_vm_migrate_encryption_configs: List, exclude_vms: Dict) -> List:
        """
        Remove vm configs in vm exclude list.

        :param all_vm_migrate_encryption_configs: all vm configs.
        :type all_vm_migrate_encryption_configs: List
        :param exclude_vms: user input VM exclude patterns.
        :type exclude_vms: Dict
        :return: a list of configs to compare with desired input.
        :rtype: List
        """
        all_vm_configs = []
        excluded_vms = {}
        vm_type = exclude_vms.get("vm_type", {})
        exclude_vm_in_bad_state = vm_type.get("vm_disconnected", False)
        exclude_vm_fully_encrypted = vm_type.get("vm_fully_encrypted", False)
        exclude_vm_names = exclude_vms.get("vm_name_match", [])
        for vm_migrate_encryption_config in all_vm_migrate_encryption_configs:
            vm_name = vm_migrate_encryption_config["vm_name"]
            vm_state = vm_migrate_encryption_config["vm_state"]
            migrate_policy = vm_migrate_encryption_config["migrate_encryption_policy"]
            # check if vm in bad state
            if vm_migrate_encryption_config["vm_state"] != "connected" and exclude_vm_in_bad_state:
                logger.debug(
                    f"Exclude this VM -  name: {vm_name}, state: {vm_state}, policy: {migrate_policy} - bad state"
                )
                excluded_vms.setdefault("disconnected", []).append(vm_name)
                continue
            # check if vm is fully encrypted
            if vm_migrate_encryption_config["vm_encrypted"] and exclude_vm_fully_encrypted:
                logger.debug(
                    f"Exclude this VM -  name: {vm_name}, state: {vm_state}, policy: {migrate_policy} - encrypted"
                )
                excluded_vms.setdefault("encrypted", []).append(vm_name)
                continue
            # check if vm name matches the name in exclude list
            if self._vm_name_check(vm_name, exclude_vm_names):
                logger.debug(
                    f"Exclude this VM -  name: {vm_name}, state: {vm_state}, policy: {migrate_policy} - name match"
                )
                excluded_vms.setdefault("name_match", []).append(vm_name)
                continue
            vm_config = {
                "vm_name": vm_name,
                "path": vm_migrate_encryption_config["path"],
                "migrate_encryption_policy": migrate_policy,
            }
            all_vm_configs.append(vm_config)

        logger.info(f"Excluded disconnected VMs: {','.join(excluded_vms.get('disconnected', []))}")
        logger.info(f"Excluded fully encrypted VMs: {','.join(excluded_vms.get('encrypted', []))}")
        logger.info(f"Excluded name match VMs: {','.join(excluded_vms.get('name_match', []))}")
        logger.debug(f"All VM configs: {all_vm_configs}")
        return all_vm_configs

    def _is_vm_deleted_exception(self, cause) -> bool:
        """
        Check if exception received when get config is because VM been deleted.

        :param cause: exception cause.
        :type cause: Exception
        :return: True if exception case is "vmodl.fault.ManagedObjectNotFound" otherwise False
        :rtype: bool
        """

        while cause:
            if isinstance(cause, vmodl.fault.ManagedObjectNotFound):
                return True
            cause = getattr(cause, "__cause__", None)
        return False

    def __get_all_vm_migrate_encryption_policy(self, vc_vmomi_client: VcVmomiClient) -> List[Dict]:
        """
        Get all VM migrate Encryption policies.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :return: List containing VM migration Encryption policy for all Virtual Machines
        :rtype: Dict
        """
        all_vm_migrate_encryption_configs = []
        all_vm_refs = vc_vmomi_client.get_objects_by_vimtype(vim.VirtualMachine)

        for vm_ref in all_vm_refs:
            try:
                logger.debug(
                    f"VM name: {vm_ref.name}, conn state: {vm_ref.runtime.connectionState}, power state: {vm_ref.runtime.powerState}"
                )
                vm_migrate_encryption_config = {
                    "vm_name": vm_ref.name,
                    "path": vc_vmomi_client.get_vm_path_in_datacenter(vm_ref),
                    "migrate_encryption_policy": vm_ref.config.migrateEncryption
                    if vm_ref.config and hasattr(vm_ref.config, "migrateEncryption")
                    else "None",
                    "vm_state": vm_ref.runtime.connectionState,
                    "vm_encrypted": True
                    if vm_ref.config and hasattr(vm_ref.config, "keyId") and vm_ref.config.keyId is not None
                    else False,
                }
                all_vm_migrate_encryption_configs.append(vm_migrate_encryption_config)
            except Exception as e:
                logger.exception(f"Exception when get configs: {e}")
                if not self._is_vm_deleted_exception(e):
                    raise
        return all_vm_migrate_encryption_configs

    def _get_data_center(self, vm_ref):
        """
        Get datacenter where this VM/VM template located.

        :param vm_ref: vm reference object.
        :type vm_ref: vim.VirtualMachine
        :return: datacenter and a list of errors if any
        :rtype: Tuple
        """
        errors = []
        parent = vm_ref.parent
        while parent:
            if isinstance(parent, vim.Datacenter):
                return parent, errors
            parent = parent.parent
        errors.append(f"Datacenter not found for the VM: {vm_ref.name}")
        return None, errors

    def _get_resource_pool(self, vm_ref):
        """
        Get resource pool for converting a VM template to VM for remediation.

        :param vm_ref: vm reference object.
        :type vm_ref: vim.VirtualMachine
        :return: resource pool and a list of errors if any
        :rtype: Tuple
        """
        resource_pool = None
        datacenter, errors = self._get_data_center(vm_ref)
        if errors:
            return resource_pool, errors
        logger.debug(f"Datacenter : {datacenter.name} found for VM: {vm_ref.name}")
        cluster_resource_pool = None
        host_resource_pool = None
        children = datacenter.hostFolder.childEntity
        for child in children:
            if isinstance(child, vim.ClusterComputeResource):
                cluster_resource_pool = child.resourcePool
                break
            elif isinstance(child, vim.ComputerResource):
                host_resource_pool = child.resourcePool
        if cluster_resource_pool:
            resource_pool = cluster_resource_pool
        elif host_resource_pool:
            resource_pool = host_resource_pool
        else:
            errors.append(f"Resource pool for VM: {vm_ref.name} not found")
        return resource_pool, errors

    def _is_in_non_compiliant_list(self, vm_name: str, non_compliant_configs: List) -> bool:
        """
        Check if a given vm name is in non compliant vm list.

        :param vm_name: vm name.
        :type vm_name: str
        :param non_compliant_configs: non compliant vm config list.
        :type non_compliant_configs: List
        :return: True if vm_name matches any item in non compliant config list
        :rtype: bool
        """
        return any(item.get("vm_name") == vm_name for item in non_compliant_configs)

    def __set_vm_migrate_encryption_policy_for_all_non_compliant_vms(
        self, vc_vmomi_client: VcVmomiClient, desired_values: Dict, non_compliant_configs: List
    ) -> Tuple[List[dict], List[dict], List[str]]:
        """
        Set VM migrate Encryption policies for all non-compliant VMs.

        | Sample desired state

        .. code-block:: json

            {
              "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
              },
              "__OVERRIDES__": [
                {
                  "vm_name": "sddc-manager",
                  "path": "SDDC-Datacenter/vm/Management VMs",
                  "migrate_encryption_policy": "required"
                },
                {
                  "vm_name": "nsx-mgmt-1",
                  "path": "SDDC-Datacenter/vm/Networking VMs",
                  "migrate_encryption_policy": "required",
                  "exclude": True
                }
              ]
            }

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :param desired_values: Dictionary containing VM migration Encryption policy.
        :type desired_values: Dict
        :return: list of current non compliant and desired configs and list of errors if any
        :rtype: Tuple
        """
        desired_global_vm_migrate_encryption_policy = desired_values.get(GLOBAL, {}).get(DESIRED_KEY)
        overrides = desired_values.get(OVERRIDES, [])
        all_vm_refs = vc_vmomi_client.get_objects_by_vimtype(vim.VirtualMachine)
        errors = []
        remediated = []
        remediated_desired = []

        for vm_ref in all_vm_refs:
            try:
                vm_name = vm_ref.name
                if not self._is_in_non_compiliant_list(vm_name, non_compliant_configs):
                    continue
                vm_path = vc_vmomi_client.get_vm_path_in_datacenter(vm_ref)
                current_vm_migrate_encryption_policy = (
                    vm_ref.config.migrateEncryption
                    if vm_ref.config and hasattr(vm_ref.config, "migrateEncryption")
                    else "None"
                )
                override_vm_migrate_encryption_policy, exclude_flag = next(
                    (
                        (override.get(DESIRED_KEY), override.get(EXCLUDE_THIS_VM))
                        for override in overrides
                        if override[VM_NAME] == vm_name and override[PATH] == vm_path
                    ),
                    (None, None),
                )
                desired_vm_migrate_policy = (
                    override_vm_migrate_encryption_policy
                    if override_vm_migrate_encryption_policy is not None
                    else desired_global_vm_migrate_encryption_policy
                )
                if current_vm_migrate_encryption_policy != desired_vm_migrate_policy and not exclude_flag:
                    logger.info(f"Setting VM migrate policy {desired_vm_migrate_policy} on VM {vm_name}")
                    # continue to remediate next vm if hitting any errors
                    try:
                        template = vm_ref.config.template
                        if template:
                            # for VM template, convert to VM during remediation
                            resource_pool, errs = self._get_resource_pool(vm_ref)
                            if errs:
                                errors.append(errs)
                                continue
                            logger.debug(f"Resource pool for convert template to VM: {resource_pool}")
                            vm_ref.MarkAsVirtualMachine(pool=resource_pool)
                            logger.debug(f"Converted VM template to VM, template flag: {vm_ref.config.template}")

                        config_spec = vim.vm.ConfigSpec()
                        config_spec.migrateEncryption = desired_vm_migrate_policy
                        task = vm_ref.ReconfigVM_Task(config_spec)
                        vc_vmomi_client.wait_for_task(task=task, timeout=120)

                        if template:
                            # for VM template, convert it back to template after remediation
                            vm_ref.MarkAsTemplate()
                            logger.debug(f"Converted VM back to VM template, template flag: {vm_ref.config.template}")

                        remediated.append(
                            {VM_NAME: vm_name, PATH: vm_path, DESIRED_KEY: current_vm_migrate_encryption_policy}
                        )
                        remediated_desired.append(
                            {VM_NAME: vm_name, PATH: vm_path, DESIRED_KEY: desired_vm_migrate_policy}
                        )
                    except Exception as e:
                        logger.exception(f"An error occurred: {e}")
                        if not self._is_vm_deleted_exception(e):
                            errors.append(f"Failed to remediate VM: {vm_name} - {str(e)}")
                else:
                    if exclude_flag:
                        logger.info(
                            f"VM {vm_name} is excluded from remediation,  exclude flag present - {exclude_flag}"
                        )
                    else:
                        logger.info(
                            f"VM {vm_name} already has desired migrate policy {desired_vm_migrate_policy}, no remediation required."
                        )
            except Exception as e:
                logger.exception(f"An error occurred: {e}")
                if not self._is_vm_deleted_exception(e):
                    errors.append(f"Failed to remediate VM: {vm_name} - {str(e)}")

        return remediated, remediated_desired, errors

    def __get_non_compliant_configs(self, vm_configs: List, desired_values: Dict) -> Tuple[List, List]:
        """
        Get all non-compliant items for the given desired state spec.

        :return:
        :meta private:
        """
        non_compliant_configs = []
        desired_configs = []

        global_desired_value = desired_values.get(GLOBAL, {}).get(DESIRED_KEY)
        overrides = desired_values.get(OVERRIDES, [])

        # Check global non-compliance
        non_compliant_global = [config for config in vm_configs if config.get(DESIRED_KEY) != global_desired_value]
        if non_compliant_global:
            non_compliant_configs.extend(non_compliant_global)

        # Remove non-compliant override config if exists from global
        for override in overrides:
            override_vm_name = override.get(VM_NAME)
            override_path = override.get(PATH)
            for config in non_compliant_global:
                if config.get(VM_NAME) == override_vm_name and config.get(PATH) == override_path:
                    non_compliant_configs.remove(config)
        desired_configs = [{**config, DESIRED_KEY: global_desired_value} for config in non_compliant_configs]

        # Check overrides for non-compliance
        for vm_overrides in overrides:
            vm_name = vm_overrides.get(VM_NAME)
            vm_path = vm_overrides.get(PATH)
            exclude_flag = vm_overrides.get(EXCLUDE_THIS_VM)
            desired_value = vm_overrides.get(DESIRED_KEY)

            # Find the configuration for the current virtual machine
            config = next(
                (
                    config
                    for config in vm_configs
                    if config.get(VM_NAME) == vm_name and config.get(PATH) == vm_path and not exclude_flag
                ),
                None,
            )

            if config and config.get(DESIRED_KEY) != desired_value:
                non_compliant_configs.append(config)
                desired_configs.append({VM_NAME: vm_name, PATH: vm_path, DESIRED_KEY: desired_value})
        return non_compliant_configs, desired_configs

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        Check compliance of VM migrate Encryption policies for all Virtual Machines.

        | Support Values: ["disabled", "opportunistic", "required"]

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VM migrate Encryption policy.
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Checking compliance")
        all_vm_migrate_encryption_configs, errors = self.get(context=context)

        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # check if need to exclude any VMs.
        exclude_vms = desired_values.get("exclude_vms", {})
        logger.debug(f"User input VM patterns to be excluded from compliance check: {exclude_vms}")
        all_vm_migrate_encryption_configs = self._filter_vm_configs(all_vm_migrate_encryption_configs, exclude_vms)

        non_compliant_configs, desired_configs = self.__get_non_compliant_configs(
            all_vm_migrate_encryption_configs, desired_values
        )

        if non_compliant_configs:
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

        | Sample desired state

        .. code-block:: json

            {
              "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
              },
              "__OVERRIDES__": [
                {
                  "vm_name": "sddc-manager",
                  "path": "SDDC-Datacenter/vm/Management VMs",
                  "migrate_encryption_policy": "required"
                },
                {
                  "vm_name": "nsx-mgmt-1",
                  "path": "SDDC-Datacenter/vm/Networking VMs",
                  "migrate_encryption_policy": "required"
                }
              ]
            }

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for VM migrate encryption policy
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running remediation")
        result = self.check_compliance(context, desired_values)

        if result[consts.STATUS] == ComplianceStatus.COMPLIANT:
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}
        elif result[consts.STATUS] == ComplianceStatus.FAILED:
            errors = result[consts.ERRORS]
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        non_compliant_configs = result.get(consts.CURRENT, [])
        vc_vmomi_client = context.vc_vmomi_client()
        remediated, remediated_desired, errors = self.__set_vm_migrate_encryption_policy_for_all_non_compliant_vms(
            vc_vmomi_client, desired_values, non_compliant_configs
        )

        if not errors:
            status = RemediateStatus.SUCCESS
            result = {consts.STATUS: status, consts.OLD: remediated, consts.NEW: remediated_desired}
        else:
            if remediated:
                status = RemediateStatus.PARTIAL
                result = {
                    consts.STATUS: status,
                    consts.OLD: remediated,
                    consts.NEW: remediated_desired,
                    consts.ERRORS: errors,
                }
            else:
                result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result
