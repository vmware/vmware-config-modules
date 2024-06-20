# Copyright 2024 Broadcom. All Rights Reserved.
import copy

import pytest
from mock import MagicMock
from pyVmomi import vim

from config_modules_vmware.controllers.esxi.firewall_rulesets_config import FirewallRulesetsConfig
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext


class TestFirewallRulesetsConfig:

    def setup_method(self):
        self.context = MagicMock()

        mock_allowed_hosts = vim.host.Ruleset.IpList(allIp=False, ipAddress=["192.168.0.1"])
        mock_allowed_hosts.ipNetwork = [vim.host.Ruleset.IpNetwork(network="192.168.121.0", prefixLength=8)]
        mock_rule = vim.host.Ruleset.Rule(port=8080, endPort=9090, direction="inbound", protocol="tcp")
        self.mock_rulesets = [vim.host.Ruleset(key="test_ruleset",
                                               enabled=True,
                                               allowedHosts=mock_allowed_hosts,
                                               rule=[mock_rule])]
        self.mock_rulesets_disabled = [vim.host.Ruleset(key="test_ruleset",
                                                        enabled=False,
                                                        allowedHosts=mock_allowed_hosts,
                                                        rule=[mock_rule])]
        mock_host_ref = MagicMock()
        mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        self.context = HostContext(host_ref=mock_host_ref)

        self.mock_ruleset_1 = {
            "name": "test_ruleset",
            "allow_all_ip": False,
            "enabled": True,
            "allowed_ips": {
                "address": [
                    "192.168.0.1"
                ],
                "network": [
                    "192.168.121.0/8"
                ]
            },
            "rules": [
                {
                    "direction": "inbound",
                    "port": 8080,
                    "end_port": 9090,
                    "protocol": "tcp"
                }
            ]
        }

        # Remediation success mock data
        self.remediate_mock_1 = copy.deepcopy(self.mock_ruleset_1)
        self.remediate_mock_1["allow_all_ip"] = True
        self.remediate_mock_1_old = {"allow_all_ip": False, "name": "test_ruleset"}
        self.remediate_mock_1_new = {"allow_all_ip": True, "name": "test_ruleset"}

        self.remediate_mock_2 = copy.deepcopy(self.mock_ruleset_1)
        self.remediate_mock_2["enabled"] = False
        self.remediate_mock_2_old = {"enabled": True, "name": "test_ruleset"}
        self.remediate_mock_2_new = {"enabled": False, "name": "test_ruleset"}

        self.remediate_mock_3 = copy.deepcopy(self.mock_ruleset_1)
        self.remediate_mock_3["allowed_ips"]["address"] = ["192.168.0.2"]
        self.remediate_mock_3_old = {"allowed_ips": {"address": ["192.168.0.1"]}, "name": "test_ruleset"}
        self.remediate_mock_3_new = {"allowed_ips": {"address": ["192.168.0.2"]}, "name": "test_ruleset"}

        self.remediate_mock_4 = copy.deepcopy(self.mock_ruleset_1)
        self.remediate_mock_4["allowed_ips"]["network"] = ["192.168.121.0/8", "192.168.0.0/16"]
        self.remediate_mock_4_old = {"allowed_ips": {"network": ["192.168.121.0/8"]},
                                     "name": "test_ruleset"}
        self.remediate_mock_4_new = {"allowed_ips": {"network": ["192.168.121.0/8", "192.168.0.0/16"]},
                                     "name": "test_ruleset"}

        # Remediation failed mock data

        # Unsupported configuration
        self.remediate_mock_5 = copy.deepcopy(self.mock_ruleset_1)
        self.remediate_mock_5["rules"][0]["direction"] = "outbound"
        self.mock_5_expected_errors = [f"Manual intervention required for ruleset [test_ruleset]. Remediation not supported for configuration [rules].{self.remediate_mock_5['rules']}"]
        # Failed to Disable ruleset
        self.remediate_mock_6 = self.remediate_mock_2
        self.mock_6_expected_errors = ["Exception remediating ruleset [test_ruleset], Mock Exception"]
        # Failed to Enable ruleset
        self.remediate_mock_7 = self.mock_ruleset_1
        self.mock_7_expected_errors = ["Exception remediating ruleset [test_ruleset], Mock Exception"]
        # Failed to update ruleset for allow all ip
        self.remediate_mock_8 = self.remediate_mock_1
        self.mock_8_expected_errors = ["Exception remediating ruleset [test_ruleset], Mock Exception"]
        # Ruleset not found in host or desired spec
        self.remediate_mock_10 = copy.deepcopy(self.mock_ruleset_1)
        self.remediate_mock_10["name"] = "invalid"
        self.mock_10_expected_errors = [
            f"Manual intervention required. Ruleset [invalid] not found in host. spec={self.remediate_mock_10}",
            "Manual intervention required. Ruleset [test_ruleset] exists in host but not defined in desired input spec. "
            "spec={'allow_all_ip': False, 'name': 'test_ruleset', 'enabled': True, "
            "'allowed_ips': {'address': ['192.168.0.1'], 'network': ['192.168.121.0/8']}, "
            "'rules': [{'port': 8080, 'direction': 'inbound', 'protocol': 'tcp', 'end_port': 9090}]}"]

        # Partial remediation
        self.remediate_mock_9 = copy.deepcopy(self.mock_ruleset_1)
        self.remediate_mock_9["allow_all_ip"] = True
        self.remediate_mock_9["rules"][0]["direction"] = "outbound"
        self.remediate_mock_9_old = {"allow_all_ip": False, "name": "test_ruleset"}
        self.remediate_mock_9_new = {"allow_all_ip": True, "name": "test_ruleset"}
        self.mock_9_expected_errors = [f"Manual intervention required for ruleset [test_ruleset]. Remediation not supported for configuration [rules].{self.remediate_mock_9['rules']}"]

        self.controller = FirewallRulesetsConfig()

    def test_get_rulesets(self):
        expected_list = [self.mock_ruleset_1]
        rulesets, errors = self.controller.get(self.context)
        assert errors is None
        assert isinstance(rulesets, list)
        assert rulesets == expected_list

    def test_check_compliance_duplicate_rulesets(self):
        mock_input = [self.mock_ruleset_1, self.mock_ruleset_1]
        with pytest.raises(ValueError, match=f"Found duplicate entries for ruleset. name=test_ruleset"):
            self.controller.check_compliance(self.context, mock_input)

    def test_check_compliance_non_compliant(self):
        # mock_host_ref = MagicMock()
        # mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        # mock_get_host_ref_by_moid.return_value = mock_host_ref
        ruleset_1 = copy.deepcopy(self.mock_ruleset_1)
        ruleset_1["enabled"] = False
        ruleset_2 = copy.deepcopy(self.mock_ruleset_1)
        ruleset_2["name"] = "ruleset_unknown"

        expected_output = {"status": "NON_COMPLIANT", "current": [None, {"name": "test_ruleset", "enabled": True}],
                           "desired": [ruleset_2, {"name": "test_ruleset", "enabled": False}]}
        mock_input = [ruleset_1, ruleset_2]
        result = self.controller.check_compliance(self.context, mock_input)
        assert result["status"] == "NON_COMPLIANT"
        assert result["current"] == expected_output["current"]
        assert result["desired"] == expected_output["desired"]

    def test_check_compliance_compliant(self):
        # mock_host_ref = MagicMock()
        # mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        # mock_get_host_ref_by_moid.return_value = mock_host_ref
        mock_input = [self.mock_ruleset_1]
        result = self.controller.check_compliance(self.context, mock_input)
        assert result["status"] == "COMPLIANT"

    @pytest.mark.parametrize(
        "test_name, test_input, expected_new, expected_old",
        [
            ("update_allow_all_ip", "remediate_mock_1", "remediate_mock_1_new", "remediate_mock_1_old"),
            ("no_remediation_required", "mock_ruleset_1", None, None),
            ("update_enabled", "remediate_mock_2", "remediate_mock_2_new", "remediate_mock_2_old"),
            ("update_allowed_address", "remediate_mock_3", "remediate_mock_3_new", "remediate_mock_3_old"),
            ("update_allowed_hosts", "remediate_mock_4", "remediate_mock_4_new", "remediate_mock_4_old"),
        ],
    )
    def test_remediate_success(self, test_name, test_input, expected_old, expected_new):
        # mock_host_ref = MagicMock()
        # mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        # mock_get_host_ref_by_moid.return_value = mock_host_ref

        mock_input = [eval(f"self.{test_input}")]
        result = self.controller.remediate(self.context, mock_input)
        assert result["status"] == "SUCCESS"
        if expected_new is not None:
            assert result["new"] == [eval(f"self.{expected_new}")]
            assert result["old"] == [eval(f"self.{expected_old}")]
        else:
            assert "old" not in result
            assert "new" not in result

    def test_remediate_disable_ruleset_failed(self):
        mock_host_ref = MagicMock()
        mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        mock_host_ref.configManager.firewallSystem.DisableRuleset.side_effect = Exception("Mock Exception")
        mock_context = HostContext(host_ref=mock_host_ref)
        mock_input = [self.remediate_mock_6]
        result = self.controller.remediate(mock_context, mock_input)
        assert result["status"] == "FAILED"
        assert result["errors"] == self.mock_6_expected_errors

    def test_remediate_enable_ruleset_failed(self):
        mock_host_ref = MagicMock()
        mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets_disabled
        mock_host_ref.configManager.firewallSystem.EnableRuleset.side_effect = Exception("Mock Exception")
        mock_context = HostContext(host_ref=mock_host_ref)

        mock_input = [self.remediate_mock_7]
        result = self.controller.remediate(mock_context, mock_input)
        assert result["status"] == "FAILED"
        assert result["errors"] == self.mock_7_expected_errors

    def test_remediate_update_ruleset_failed(self):
        mock_host_ref = MagicMock()
        mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        mock_host_ref.configManager.firewallSystem.UpdateRuleset.side_effect = Exception("Mock Exception")
        mock_context = HostContext(host_ref=mock_host_ref)

        mock_input = [self.remediate_mock_8]
        result = self.controller.remediate(mock_context, mock_input)
        assert result["status"] == "FAILED"
        assert result["errors"] == self.mock_8_expected_errors

    def test_remediate_failed_unsupported_configuration(self):
        mock_input = [self.remediate_mock_5]
        result = self.controller.remediate(self.context, mock_input)
        assert result["status"] == "FAILED"
        assert result["errors"] == self.mock_5_expected_errors


    def test_remediate_failed_ruleset_not_found_in_host(self):
        # mock_host_ref = MagicMock()
        # mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        # mock_get_host_ref_by_moid.return_value = mock_host_ref

        mock_input = [self.remediate_mock_10]
        result = self.controller.remediate(self.context, mock_input)
        assert result["status"] == "FAILED"
        assert result["errors"] == self.mock_10_expected_errors

    def test_remediate_partial_status(self):
        # mock_host_ref = MagicMock()
        # mock_host_ref.configManager.firewallSystem.firewallInfo.ruleset = self.mock_rulesets
        # mock_host_context.host_ref.value = mock_host_ref

        mock_input = [self.remediate_mock_9]
        result = self.controller.remediate(self.context, mock_input)
        assert result["status"] == "PARTIAL"
        assert result["errors"] == self.mock_9_expected_errors
        assert result["old"] == [self.remediate_mock_9_old]
        assert result["new"] == [self.remediate_mock_9_new]
