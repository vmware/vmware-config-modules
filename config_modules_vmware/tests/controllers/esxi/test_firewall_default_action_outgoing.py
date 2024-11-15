# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.firewall_default_action_outgoing import FirewallDefaultActionOutgoing
from config_modules_vmware.tests.controllers.esxi.test_firewall_default_action_incoming import TestFirewallDefaultActionIncoming


class TestFirewallDefaultActionOutgoing(TestFirewallDefaultActionIncoming):
    # All test cases are same as for TestFirewallDefaultActionIncoming
    def setup_method(self):
        self.controller = FirewallDefaultActionOutgoing()
        self.compliant_value = 'DROP'
        self.non_compliant_value = 'PASS'
        self.cli_return_compliant_value = "   Default Action: DROP\n   Enabled: true\n   Loaded: true"
        self.cli_return_non_compliant_value = "   Default Action: PASS\n   Enabled: true\n   Loaded: true"
        mock_host_ref = MagicMock()
        mock_host_ref.name = 'host-1'
        self.firewallSystem = MagicMock()
        self.mock_host_context = MagicMock()
        self.firewallSystem.firewallInfo.defaultPolicy.incomingBlocked = False
        self.firewallSystem.firewallInfo.defaultPolicy.outgoingBlocked = False
        self.mock_host_context.host_ref.configManager.firewallSystem = self.firewallSystem
