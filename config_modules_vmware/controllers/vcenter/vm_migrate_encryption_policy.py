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

# Constants
DESIRED_KEY = "migrate_encryption_policy"
GLOBAL = "__GLOBAL__"
OVERRIDES = "__OVERRIDES__"
VM_NAME = "vm_name"
PATH = "path"


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
        vc_vmomi_client = context.vc_vmomi_client()
        errors = []
        status = RemediateStatus.SUCCESS
        try:
            errors = self.__set_vm_migrate_encryption_policy_for_all_non_compliant_vms(vc_vmomi_client, desired_values)
            if errors:
                status = RemediateStatus.FAILED

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

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
            vm_migrate_encryption_config = {
                "vm_name": vm_ref.name,
                "path": vc_vmomi_client.get_vm_path_in_datacenter(vm_ref),
                "migrate_encryption_policy": vm_ref.config.migrateEncryption,
            }
            all_vm_migrate_encryption_configs.append(vm_migrate_encryption_config)
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
        return parent, errors

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
        childs = datacenter.hostFolder.childEntity
        for child in childs:
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

    def __set_vm_migrate_encryption_policy_for_all_non_compliant_vms(
        self, vc_vmomi_client: VcVmomiClient, desired_values: Dict
    ) -> List:
        """
        Set VM migrate Encryption policies for all non-compliant VMs.

        :param vc_vmomi_client: VC vmomi client instance.
        :type vc_vmomi_client: VcVmomiClient
        :param desired_values: Dictionary containing VM migration Encryption policy.
        :type desired_values: Dict
        :return: list of errors if any
        :rtype: list
        """
        desired_global_vm_migrate_encryption_policy = desired_values.get(GLOBAL, {}).get(DESIRED_KEY)
        overrides = desired_values.get(OVERRIDES, [])
        all_vm_refs = vc_vmomi_client.get_objects_by_vimtype(vim.VirtualMachine)
        errors = []

        for vm_ref in all_vm_refs:
            vm_path = vc_vmomi_client.get_vm_path_in_datacenter(vm_ref)
            current_vm_migrate_encryption_policy = vm_ref.config.migrateEncryption
            override_vm_migrate_encryption_policy = next(
                (
                    override.get(DESIRED_KEY)
                    for override in overrides
                    if override[VM_NAME] == vm_ref.name and override[PATH] == vm_path
                ),
                None,
            )
            desired_vm_migrate_policy = (
                override_vm_migrate_encryption_policy
                if override_vm_migrate_encryption_policy is not None
                else desired_global_vm_migrate_encryption_policy
            )
            if current_vm_migrate_encryption_policy != desired_vm_migrate_policy:
                logger.info(f"Setting VM migrate policy {desired_vm_migrate_policy} on VM {vm_ref.name}")
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
                    vc_vmomi_client.wait_for_task(task=task)

                    if template:
                        # for VM template, convert it back to template after remediation
                        vm_ref.MarkAsTemplate()
                        logger.debug(f"Converted VM back to VM template, template flag: {vm_ref.config.template}")
                except Exception as e:
                    logger.exception(f"An error occurred: {e}")
                    errors.append(f"Failed to remediate VM: {vm_ref.name} - {str(e)}")
            else:
                logger.info(
                    f"VM {vm_ref.name} already has desired migrate policy {desired_vm_migrate_policy},"
                    f" no remediation required."
                )

        return errors

    def __get_non_compliant_configs(self, vm_configs: List, desired_values: Dict) -> List:
        """
        Get all non-compliant items for the given desired state spec.

        :return:
        :meta private:
        """
        non_compliant_configs = []

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

        # Check overrides for non-compliance
        for vm_overrides in overrides:
            vm_name = vm_overrides.get(VM_NAME)
            vm_path = vm_overrides.get(PATH)
            desired_value = vm_overrides.get(DESIRED_KEY)

            # Find the configuration for the current virtual machine
            config = next(
                (config for config in vm_configs if config.get(VM_NAME) == vm_name and config.get(PATH) == vm_path),
                None,
            )

            if config and config.get(DESIRED_KEY) != desired_value:
                non_compliant_configs.append(config)
        return non_compliant_configs

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

        non_compliant_configs = self.__get_non_compliant_configs(all_vm_migrate_encryption_configs, desired_values)

        if non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: non_compliant_configs,
                consts.DESIRED: desired_values,
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
        elif result[consts.STATUS] == ComplianceStatus.NON_COMPLIANT:
            non_compliant_configs = result[consts.CURRENT]
        else:
            errors = result[consts.ERRORS]
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}

        status, errors = self.set(context=context, desired_values=desired_values)

        if not errors:
            result = {consts.STATUS: status, consts.OLD: non_compliant_configs, consts.NEW: desired_values}
        else:
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result
