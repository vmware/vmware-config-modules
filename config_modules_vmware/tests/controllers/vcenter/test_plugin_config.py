import yaml
from mock import MagicMock
from mock import patch

from config_modules_vmware.controllers.vcenter.plugin_config import PluginConfig
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

class TestPluginConfig:
    def setup_method(self):
        self.controller = PluginConfig()
        self.mock_member1 = { "id": "com.vmware.test1.client", "vendor": "VMware, Inc.", "type": "REMOTE", "versions": [ "8.0.3.100","8.0.3.24091160" ] }
        self.mock_member2 = { "id": "com.vmware.test2.client", "vendor": "VMware, Inc.", "type": "REMOTE", "versions": [ "8.0.3.100" ] }
        self.mock_member3 = { "id": "com.vmware.test3.client", "vendor": "VMware, Inc.", "type": "LOCAL", "versions": [ "8.0.3.100", "8.0.3.101" ] }
        self.mock_member4 = { "id": "com.vmware.test4.client", "vendor": "VMware, Inc.", "type": "REMOTE", "versions": [ "8.0.3.100", "8.0.3.24091160" ] }
        self.mock_member5 = { "id": "com.vmware.test5.client", "vendor": "VMware, Inc.", "type": "LOCAL", "versions": [ "8.0.3.100" ] }
        self.mock_member_exclude_1 = { "id": "com.vmware.exclude1.client", "vendor": "VMware, Inc.", "type": "LOCAL", "versions": [ "8.0.3.100" ] }
        self.mock_member_exclude_2 = { "id": "com.vmware.exclude2.client", "vendor": "VMware, Inc.", "type": "LOCAL", "versions": [ "8.0.3.100" ] }

        get_plugin_id_list = {
                                 "plugins": [
                                     {
                                         "id": "com.vmware.test1.client"
                                     },
                                     {
                                        "id":  "com.vmware.test2.client"
                                     },
                                     {
                                         "id": "com.vmware.test3.client"
                                     },
                                     {
                                         "id": "com.vmware.exclude1.client"
                                     },
                                     {
                                         "id": "com.vmware.exclude2.client"
                                     }
                                 ]
                             }
        plugin_id_list_str = yaml.dump(get_plugin_id_list)
        non_compliant_get_plugin_id_list = {
                                               "plugins": [
                                                   {
                                                       "id": "com.vmware.test1.client"
                                                   },
                                                   {
                                                      "id":  "com.vmware.test2.client"
                                                   },
                                                   {
                                                       "id": "com.vmware.test3.client"
                                                   },
                                                   {
                                                       "id": "com.vmware.test4.client"
                                                   },
                                                   {
                                                       "id": "com.vmware.exclude1.client"
                                                   },
                                                   {
                                                       "id": "com.vmware.exclude2.client"
                                                   }
                                               ]
                                           }
        non_compliant_plugin_id_list_str = yaml.dump(non_compliant_get_plugin_id_list)
        non_compliant_get_plugin_id_list2 = {
                                                "plugins": [
                                                    {
                                                        "id": "com.vmware.test1.client"
                                                    },
                                                    {
                                                       "id":  "com.vmware.test2.client"
                                                    },
                                                    {
                                                        "id": "com.vmware.test3.client"
                                                    },
                                                    {
                                                        "id": "com.vmware.test4.client"
                                                    },
                                                    {
                                                        "id": "com.vmware.test5.client"
                                                    }
                                                ]
                                            }
        non_compliant_plugin_id_list_str2 = yaml.dump(non_compliant_get_plugin_id_list2)

        self.mock_plugin_detail_1 = {
                                        "vendor": "VMware, Inc.",
                                        "name": "VMware Test1 Plugin",
                                        "description": "VMware Test1 Plugin",
                                        "id": "com.vmware.test1.client",
                                        "type": "REMOTE",
                                        "instance_registrations": [
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.100"
                                            },
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.24091160"
                                            }
                                        ]
                                    }
        self.mock_plugin_detail_2 = {
                                        "vendor": "VMware, Inc.",
                                        "name": "VMware Test2 Plugin",
                                        "description": "VMware Test2 Plugin",
                                        "id": "com.vmware.test2.client",
                                        "type": "REMOTE",
                                        "instance_registrations": [
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.100"
                                            }
                                        ]
                                    }
        self.mock_plugin_detail_3 = {
                                        "vendor": "VMware, Inc.",
                                        "name": "VMware Test3 Plugin",
                                        "description": "VMware Test3 Plugin",
                                        "id": "com.vmware.test3.client",
                                        "type": "LOCAL",
                                        "instance_registrations": [
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.100",
                                            },
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.101"
                                            }
                                        ]
                                    }
        self.mock_plugin_detail_4 = {
                                        "vendor": "VMware, Inc.",
                                        "name": "VMware Test4 Plugin",
                                        "description": "VMware Test4 Plugin",
                                        "id": "com.vmware.test4.client",
                                        "type": "REMOTE",
                                        "instance_registrations": [
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.100"
                                            },
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.24091160"
                                            }
                                        ]
                                    }
        self.mock_plugin_detail_5 = {
                                        "vendor": "VMware, Inc.",
                                        "name": "VMware Test2 Plugin",
                                        "description": "VMware Test2 Plugin",
                                        "id": "com.vmware.test5.client",
                                        "type": "LOCAL",
                                        "instance_registrations": [
                                            {
                                                "deployment_status": "DEPLOYED",
                                                "certification_status": "CERTIFIED",
                                                "version": "8.0.3.100"
                                            }
                                        ]
                                    }
        self.mock_plugin_exclude_1_detail = {
                                                "vendor": "VMware, Inc.",
                                                "name": "VMware Exclude 1 Plugin",
                                                "description": "VMware Exclude 1 Plugin",
                                                "id": "com.vmware.exclude1.client",
                                                "type": "LOCAL",
                                                "instance_registrations": [
                                                    {
                                                        "deployment_status": "DEPLOYED",
                                                        "certification_status": "CERTIFIED",
                                                        "version": "8.0.3.100"
                                                    }
                                                ]
                                            }
        self.mock_plugin_exclude_2_detail = {
                                                "vendor": "VMware, Inc.",
                                                "name": "VMware Exclude 2 Plugin",
                                                "description": "VMware Exclude 1 Plugin",
                                                "id": "com.vmware.exclude2.client",
                                                "type": "LOCAL",
                                                "instance_registrations": [
                                                    {
                                                        "deployment_status": "DEPLOYED",
                                                        "certification_status": "CERTIFIED",
                                                        "version": "8.0.3.100"
                                                    }
                                                ]
                                            }

        self.compliant_shell_cmd_side_effect = [
                                                   (plugin_id_list_str, "", 0),
                                                   (yaml.dump(self.mock_plugin_detail_1), "", 0),
                                                   (yaml.dump(self.mock_plugin_detail_2), "", 0),
                                                   (yaml.dump(self.mock_plugin_detail_3), "", 0),
                                                   (yaml.dump(self.mock_plugin_exclude_1_detail), "", 0),
                                                   (yaml.dump(self.mock_plugin_exclude_2_detail), "", 0)
                                               ]
        self.non_compliant_shell_cmd_side_effect = [
                                                       (non_compliant_plugin_id_list_str, "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_1), "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_2), "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_3), "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_4), "", 0),
                                                       (yaml.dump(self.mock_plugin_exclude_1_detail), "", 0),
                                                       (yaml.dump(self.mock_plugin_exclude_2_detail), "", 0)
                                                   ]
        self.non_compliant_shell_cmd_side_effect2 = [
                                                       (non_compliant_plugin_id_list_str2, "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_1), "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_2), "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_3), "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_4), "", 0),
                                                       (yaml.dump(self.mock_plugin_detail_5), "", 0)
                                                   ]

        self.desired_values = {
            "plugins": [
                self.mock_member1, self.mock_member2, self.mock_member3,
            ],
            "exclude_plugins": [
                self.mock_member_exclude_1.get("id", None),
                self.mock_member_exclude_2.get("id", None)
            ]
        }
        self.desired_values2 = {
            "plugins": [
                self.mock_member1, self.mock_member2, self.mock_member3,
                self.mock_member4, self.mock_member5
            ],
            "exclude_plugins": [
                self.mock_member_exclude_1.get("id", None),
                self.mock_member_exclude_2.get("id", None)
            ]
        }
        self.non_compliant_values = [
            self.mock_member1, self.mock_member2, self.mock_member3,
            self.mock_member4
        ]
        self.non_compliant_values2 = [
            self.mock_member1, self.mock_member2, self.mock_member3,
            self.mock_member4, self.mock_member5
        ]
        self.compliant_with_exclude_get = [
            self.mock_member1, self.mock_member2, self.mock_member3,
            self.mock_member_exclude_1, self.mock_member_exclude_2
        ]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_success(self, mock_run_shell_cmd, mock_vc_context):
        mock_run_shell_cmd.side_effect = self.compliant_shell_cmd_side_effect
        result, errors = self.controller.get(mock_vc_context)
        assert result == self.compliant_with_exclude_get
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_get_failed(self, mock_run_shell_cmd, mock_vc_context):
        mock_run_shell_cmd.side_effect = Exception(f"Test exception")
        result, errors = self.controller.get(mock_vc_context)
        assert result == []
        assert errors == ["Test exception"]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success(self, mock_run_shell_cmd, mock_vc_context):
        mock_run_shell_cmd.side_effect = self.non_compliant_shell_cmd_side_effect
        remediate_configs = self.controller._find_drifts(self.non_compliant_values, self.desired_values.get("plugins"))
        status, errors = self.controller.set(mock_vc_context, remediate_configs)

        # Assert expected results.
        assert status == RemediateStatus.SUCCESS
        assert errors == []

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    @patch("config_modules_vmware.controllers.vcenter.plugin_config.PluginConfig._apply_plugin_config")
    def test_set_failed(self, mock_apply_plugin_config, mock_run_shell_cmd, mock_vc_context):
        mock_run_shell_cmd.side_effect = self.non_compliant_shell_cmd_side_effect
        mock_apply_plugin_config.side_effect = Exception("set exception")
        remediate_configs = self.controller._find_drifts(self.non_compliant_values, self.desired_values.get("plugins"))
        status, errors = self.controller.set(mock_vc_context, remediate_configs)

        # Assert expected results.
        assert status == RemediateStatus.FAILED
        assert errors == ["set exception"]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_compliant(self, mock_run_shell_cmd, mock_vc_context):
        mock_run_shell_cmd.side_effect = self.compliant_shell_cmd_side_effect
        result = self.controller.check_compliance(mock_vc_context, self.desired_values)

        # Assert expected results.
        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT,
        }
        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_non_compliant(self, mock_run_shell_cmd, mock_vc_context):
        mock_run_shell_cmd.side_effect = self.non_compliant_shell_cmd_side_effect
        result = self.controller.check_compliance(mock_vc_context, self.desired_values)

        assert result[consts.STATUS] == ComplianceStatus.NON_COMPLIANT
        assert result[consts.DESIRED] == self.desired_values.get("plugins")
        assert result[consts.CURRENT] == self.non_compliant_values

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_compliance_get_failed(self, mock_run_shell_cmd, mock_vc_context):
        expected_error = "get failed"
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_run_shell_cmd.side_effect = Exception(expected_error)
        result = self.controller.check_compliance(mock_vc_context, self.desired_values)

        assert result == expected_result

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediation_success(self, mock_run_shell_cmd, mock_vc_context):
        mock_run_shell_cmd.side_effect = self.non_compliant_shell_cmd_side_effect
        result = self.controller.remediate(mock_vc_context, self.desired_values)

        # Assert expected results.
        assert result[consts.STATUS] == RemediateStatus.SUCCESS
        assert result[consts.NEW] == self.desired_values.get("plugins")
        assert result[consts.OLD] == self.non_compliant_values

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediation_get_failed(self, mock_run_shell_cmd, mock_vc_context):
        expected_error = "get failed"
        expected_result = {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: [str(expected_error)]}
        mock_run_shell_cmd.side_effect = Exception(expected_error)
        result = self.controller.remediate(mock_vc_context, self.desired_values)

        # Assert expected results.
        assert result[consts.STATUS] == RemediateStatus.FAILED
        assert result[consts.ERRORS] == [expected_error]

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediation_failed(self, mock_run_shell_cmd, mock_vc_context):

        mock_run_shell_cmd.side_effect = self.non_compliant_shell_cmd_side_effect2
        expected_error = [
                             "Can't unregister local  plugin {'id': 'com.vmware.test5.client', 'type': "
                             "'LOCAL', 'vendor': 'VMware, Inc.', 'versions': ['8.0.3.100']}."
                         ]
        result = self.controller.remediate(mock_vc_context, self.desired_values)

        # Assert expected results.
        assert result[consts.STATUS] == RemediateStatus.FAILED
        assert result[consts.ERRORS] == expected_error

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediation_failed_register(self, mock_run_shell_cmd, mock_vc_context):

        mock_run_shell_cmd.side_effect = self.non_compliant_shell_cmd_side_effect
        expected_error = [
                             "Register or Update for plugin com.vmware.test5.client is not supported at now."
                         ]

        result = self.controller.remediate(mock_vc_context, self.desired_values2)

        # Assert expected results.
        assert result[consts.STATUS] == RemediateStatus.FAILED
        assert result[consts.ERRORS] == expected_error

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_remediation_skipped(self, mock_run_shell_cmd, mock_vc_context):

        mock_run_shell_cmd.side_effect = self.compliant_shell_cmd_side_effect
        result = self.controller.remediate(mock_vc_context, self.desired_values)

        # Assert expected results.
        assert result[consts.STATUS] == RemediateStatus.SKIPPED
        assert result[consts.ERRORS] == [consts.CONTROL_ALREADY_COMPLIANT]
