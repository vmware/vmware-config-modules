from mock import MagicMock
from mock import patch
from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.vcenter.vm_migrate_encryption_policy import DESIRED_KEY
from config_modules_vmware.controllers.vcenter.vm_migrate_encryption_policy import VmMigrateEncryptionPolicy
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


class TestVmMigrateEncryptionPolicy:
    def setup_method(self):
        self.controller = VmMigrateEncryptionPolicy()
        self.compliant_value = {
            "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
            },
            "exclude_vms": {
                "vm_type": {
                    "vm_disconnected": True,
                    "vm_fully_encrypted": True,
                },
                "vm_name_match": {
                    "vCLS-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                    "Test-VM-01"
                }
            }
        }
        self.compliant_value_overrides = {
            "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
            },
            "__OVERRIDES__": [
                {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
                {"vm_name": "ubuntu-dev-box2", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev2", "exclude": True}
            ],
            "exclude_vms": {
                "vm_type": {
                    "vm_disconnected": True,
                    "vm_fully_encrypted": True,
                },
                "vm_name_match": {
                    "vCLS-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                    "Test-VM-01"
                }
            }
        }
        self.non_compliant_value_overrides = {
            "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
            },
            "__OVERRIDES__": [
                {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
                {"vm_name": "ubuntu-dev-box2", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev2", "exclude": True}
            ],
            "exclude_vms": {
                "vm_type": {
                    "vm_disconnected": True,
                    "vm_fully_encrypted": True,
                },
                "vm_name_match": {
                    "vCLS-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                    "Test-VM-01"
                }
            }
        }
        self.non_compliant_vm_configs_overrides = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "ubuntu-dev-box2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/dev2"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "Test-VM-01", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        self.compliant_vm_configs_overrides = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "ubuntu-dev-box2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/dev2"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "Test-VM-01", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        self.compliant_vm_configs = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "Test-VM-01", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        self.get_compliant_vm_configs = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs", "vm_encrypted": False, "vm_state": "connected"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs", "vm_encrypted": False, "vm_state": "connected"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql", "vm_encrypted": False, "vm_state": "connected"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql", "vm_encrypted": False, "vm_state": "connected"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev", "vm_encrypted": False, "vm_state": "connected"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs", "vm_encrypted": False, "vm_state": "connected"},
            {"vm_name": "Test-VM-01", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs", "vm_encrypted": False, "vm_state": "connected"},
        ]
        self.non_compliant_vm_configs = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "Test-VM-01", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        self.remediate_failure_messages = [
            "Failed to remediate VM: nsx-mgmt-1 - ",
            "Failed to remediate VM: ms-sql-replica-1 - ",
            "Failed to remediate VM: ms-sql-replica-2 - ",
            "Failed to remediate VM: ubuntu-dev-box - ",
            "Failed to remediate VM: vcenter-1 - "
        ]
        # Pyvmomi type MagicMock objects
        self.mocked_vm_refs_compliant_overrides = self.create_all_vm_mock_refs(self.compliant_vm_configs_overrides)
        self.mocked_vm_refs_non_compliant_overrides = self.create_all_vm_mock_refs(self.non_compliant_vm_configs_overrides)
        self.mocked_vm_refs_compliant = self.create_all_vm_mock_refs(self.compliant_vm_configs)
        self.mocked_vm_refs_non_compliant = self.create_all_vm_mock_refs(self.non_compliant_vm_configs)

    def create_all_vm_mock_refs(self, vm_configs, create_bad_mock=False):
        """
        Create mock pyvmomi like objects for all Virtual Machine
        :param vm_configs:
        :param create_bad_mock:
        :return:
        """
        all_vm_mock_refs = []
        for vm_config in vm_configs:
            vm_ref = MagicMock()
            vm_ref.name = vm_config.get("vm_name")
            vm_ref.config = vim.vm.ConfigInfo()
            if not create_bad_mock:
                vm_ref.config.migrateEncryption = vm_config.get("migrate_encryption_policy")
                setattr(vm_ref, "ReconfigVM_Task", MagicMock(return_value=True))
                vm_ref.runtime.connectionState = "connected"
                vm_ref.runtime.powerState = "poweredOn"
                vm_ref.config.keyId = None
            else:
                vm_ref.runtime.connectionState = "orphaned"
                vm_ref.runtime.powerState = "poweredOff"
                vm_ref.config.keyId = vim.encryption.CryptoKeyId()
                vm_ref.config.keyId.keyId = "encryption key"
            all_vm_mock_refs.append(vm_ref)
        return all_vm_mock_refs

    def set_vm_ref_property(self, vm_name, vm_refs, vm_bad_state=False, vm_encrypted=False):
        for vm_ref in vm_refs:
            if vm_ref.name == vm_name:
                if vm_bad_state:
                    vm_ref.runtime.connectionState = "orphaned"
                    vm_ref.runtime.powerState = "poweredOff"
                if vm_encrypted:
                    vm_ref.config.keyId = vim.encryption.CryptoKeyId()
                    vm_ref.config.keyId.keyId = "encryption key"

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant

        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.get_compliant_vm_configs
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to get VM migrate encryption policy")

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == [str(expected_error)]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        non_compliant_configs = result.get(consts.CURRENT, [])
        vc_vmomi_client = mock_vc_context.vc_vmomi_client()
        _, _, errors = self.controller._VmMigrateEncryptionPolicy__set_vm_migrate_encryption_policy_for_all_non_compliant_vms(vc_vmomi_client, self.compliant_value, non_compliant_configs)
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("")

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.wait_for_task.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        non_compliant_configs = result.get(consts.CURRENT, [])
        vc_vmomi_client = mock_vc_context.vc_vmomi_client()
        _, _, errors = self.controller._VmMigrateEncryptionPolicy__set_vm_migrate_encryption_policy_for_all_non_compliant_vms(vc_vmomi_client, self.compliant_value, non_compliant_configs)
        assert errors == self.remediate_failure_messages

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant_vm_disconnected(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        self.set_vm_ref_property("Test-VM-01", self.mocked_vm_refs_compliant, vm_bad_state=True)
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant_vm_encrypted(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        self.set_vm_ref_property("Test-VM-01", self.mocked_vm_refs_compliant, vm_encrypted=True)
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_compliant_overrides(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: ComplianceStatus.COMPLIANT}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant_overrides
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/dev2",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value_overrides)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant_overrides(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.CURRENT: [{'migrate_encryption_policy': 'required',
                                             'path': 'SDDC-Datacenter/vm/db_workloads/ms-sql',
                                             'vm_name': 'ms-sql-replica-2'}],
                           consts.DESIRED: [{'migrate_encryption_policy': 'disabled',
                                             'path': 'SDDC-Datacenter/vm/db_workloads/ms-sql',
                                             'vm_name': 'ms-sql-replica-2'}],
                           consts.STATUS: ComplianceStatus.NON_COMPLIANT}


        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant_overrides
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/dev2",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.non_compliant_value_overrides)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = self.controller._VmMigrateEncryptionPolicy__get_non_compliant_configs(
            self.non_compliant_vm_configs,
            self.compliant_value)

        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: desired_configs,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Check compliance Exception")
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_skipped_already_desired(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: [consts.CONTROL_ALREADY_COMPLIANT]}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = self.controller._VmMigrateEncryptionPolicy__get_non_compliant_configs(
            self.non_compliant_vm_configs,
            self.compliant_value)

        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: desired_configs,
        }
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    @patch("config_modules_vmware.controllers.vcenter.vm_migrate_encryption_policy.VmMigrateEncryptionPolicy._get_resource_pool")
    def test_remediate_template_success(self, mock_get_resource_pool, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = self.controller._VmMigrateEncryptionPolicy__get_non_compliant_configs(
            self.non_compliant_vm_configs,
            self.compliant_value)

        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: desired_configs,
        }
        # Mark VM as template
        for vm_ref in self.mocked_vm_refs_non_compliant:
            vm_ref.config.template = True
        mock_get_resource_pool.return_value = MagicMock(), []
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_template_success_resource_pool(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs, desired_configs = self.controller._VmMigrateEncryptionPolicy__get_non_compliant_configs(
            self.non_compliant_vm_configs,
            self.compliant_value)

        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: desired_configs,
        }
        # Mark VM as template
        #datacenter = vim.Datacenter("group-d1")
        datacenter = MagicMock(spec=vim.Datacenter)
        datacenter.name = "group-d1"
        datacenter.parent = None
        child = MagicMock(spec=vim.ClusterComputeResource)
        datacenter.hostFolder.childEntity = [child]
        for vm_ref in self.mocked_vm_refs_non_compliant:
            vm_ref.config.template = True
            vm_ref.parent = datacenter
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    @patch("config_modules_vmware.controllers.vcenter.vm_migrate_encryption_policy.VmMigrateEncryptionPolicy._get_resource_pool")
    def test_remediate_template_failed(self, mock_get_resource_pool, mock_vc_vmomi_client, mock_vc_context):
        expected_error = [["Resource pool not found"], ["Resource pool not found"], ["Resource pool not found"], ["Resource pool not found"], ["Resource pool not found"]]
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: expected_error}
        # Mark VM as template
        for vm_ref in self.mocked_vm_refs_non_compliant:
            vm_ref.config.template = True
        mock_get_resource_pool.return_value = None, ["Resource pool not found"]
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_get_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Get exception while remediation")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        pyvmomi_error = Exception("Pyvmomi exception while setting VM migrate encryption policy")
        expected_error = [
                             'Failed to remediate VM: nsx-mgmt-1 - Pyvmomi exception while setting '
                             'VM migrate encryption policy',
                             'Failed to remediate VM: ms-sql-replica-1 - Pyvmomi exception while '
                             'setting VM migrate encryption policy',
                             'Failed to remediate VM: ms-sql-replica-2 - Pyvmomi exception while '
                             'setting VM migrate encryption policy',
                             'Failed to remediate VM: ubuntu-dev-box - Pyvmomi exception while '
                             'setting VM migrate encryption policy',
                             'Failed to remediate VM: vcenter-1 - Pyvmomi exception while setting '
                             'VM migrate encryption policy',
                          ]
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: expected_error}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client
        mock_vc_vmomi_client.wait_for_task.side_effect = pyvmomi_error

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result
