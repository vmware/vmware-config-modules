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
            }
        }
        self.compliant_value_overrides = {
            "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
            },
            "__OVERRIDES__": [
                {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"}
            ]
        }
        self.non_compliant_value_overrides = {
            "__GLOBAL__": {
                "migrate_encryption_policy": "opportunistic"
            },
            "__OVERRIDES__": [
                {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"}
            ]
        }
        self.non_compliant_vm_configs_overrides = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        self.compliant_vm_configs_overrides = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        self.compliant_vm_configs = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        self.non_compliant_vm_configs = [
            {"vm_name": "nsx-mgmt-1", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "sddc-manager", "migrate_encryption_policy": "opportunistic", "path": "SDDC-Datacenter/vm/Management VMs"},
            {"vm_name": "ms-sql-replica-1", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ms-sql-replica-2", "migrate_encryption_policy": "required", "path": "SDDC-Datacenter/vm/db_workloads/ms-sql"},
            {"vm_name": "ubuntu-dev-box", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/dev"},
            {"vm_name": "vcenter-1", "migrate_encryption_policy": "disabled", "path": "SDDC-Datacenter/vm/Management VMs"}
        ]
        # Pyvmomi type MagicMock objects
        self.mocked_vm_refs_compliant_overrides = self.create_all_vm_mock_refs(self.compliant_vm_configs_overrides)
        self.mocked_vm_refs_non_compliant_overrides = self.create_all_vm_mock_refs(self.compliant_vm_configs_overrides)
        self.mocked_vm_refs_compliant = self.create_all_vm_mock_refs(self.compliant_vm_configs)
        self.mocked_vm_refs_non_compliant = self.create_all_vm_mock_refs(self.non_compliant_vm_configs)

        # Bad mock to induce error
        self.mocked_vm_refs_missing_props = self.create_all_vm_mock_refs(self.non_compliant_vm_configs,
                                                                         create_bad_mock=True)

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
            if not create_bad_mock:
                vm_ref.name = vm_config.get("vm_name")
                vm_ref.config = vim.vm.ConfigSpec()
                vm_ref.config.migrateEncryption = vm_config.get("migrate_encryption_policy")
                setattr(vm_ref, "ReconfigVM_Task", MagicMock(return_value=True))
            all_vm_mock_refs.append(vm_ref)
        return all_vm_mock_refs

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_get_success(self, mock_vc_vmomi_client, mock_vc_context):
        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant

        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_vm_configs
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

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_set_failed(self, mock_vc_vmomi_client, mock_vc_context):
        expected_error = Exception("Failed to set VM migrate encryption policy")

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.wait_for_task.side_effect = expected_error
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result, errors = self.controller.set(mock_vc_context, self.compliant_value)
        assert result == RemediateStatus.FAILED
        assert errors == [str(expected_error)]

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
                           consts.DESIRED: self.non_compliant_value_overrides,
                           consts.STATUS: ComplianceStatus.NON_COMPLIANT}


        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant_overrides
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
                                                                      "SDDC-Datacenter/vm/Management VMs"]
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.check_compliance(mock_vc_context, self.non_compliant_value_overrides)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_check_compliance_non_compliant(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs = self.controller._VmMigrateEncryptionPolicy__get_non_compliant_configs(
            self.non_compliant_vm_configs,
            self.compliant_value)

        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: non_compliant_configs,
            consts.DESIRED: self.compliant_value,
        }

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_vmomi_client.get_vm_path_in_datacenter.side_effect = ["SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/Management VMs",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/db_workloads/ms-sql",
                                                                      "SDDC-Datacenter/vm/dev",
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
    def test_remediate_success_already_desired(self, mock_vc_vmomi_client, mock_vc_context):
        expected_result = {consts.STATUS: RemediateStatus.SUCCESS}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_compliant
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        result = self.controller.remediate(mock_vc_context, self.compliant_value)
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.clients.vcenter.vc_vmomi_client.VcVmomiClient")
    def test_remediate_success(self, mock_vc_vmomi_client, mock_vc_context):
        non_compliant_configs = self.controller._VmMigrateEncryptionPolicy__get_non_compliant_configs(
            self.non_compliant_vm_configs,
            self.compliant_value)

        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: non_compliant_configs,
            consts.NEW: self.compliant_value,
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
        expected_error = Exception("Pyvmomi exception while setting VM migrate encryption policy")
        expected_result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: [str(expected_error)]}

        mock_vc_vmomi_client.get_objects_by_vimtype.return_value = self.mocked_vm_refs_non_compliant
        mock_vc_context.vc_vmomi_client.return_value = mock_vc_vmomi_client

        # Mocking the set method to simulate failure and return the desired errors
        with patch.object(VmMigrateEncryptionPolicy, "set", return_value=(RemediateStatus.FAILED,
                                                                          [str(expected_error)])):
            result = self.controller.remediate(mock_vc_context, self.compliant_value)
            assert result == expected_result
