# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from itertools import dropwhile
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import HostContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList

ALLOW_ALL_IP_KEY = "allow_all_ip"
NAME_KEY = "name"
ENABLED_KEY = "enabled"
ALLOWED_IPS_KEY = "allowed_ips"
RULES_KEY = "rules"
PORT_KEY = "port"
DIRECTION_KEY = "direction"
PROTOCOL_KEY = "protocol"
END_PORT_KEY = "end_port"
ADDRESS_KEY = "address"
NETWORK_KEY = "network"
NETWORK_CIDR_FORMAT = "{}/{}"

logger = LoggerAdapter(logging.getLogger(__name__))


class FirewallRulesetsConfig(BaseController):
    """ESXi Firewall Rulesets configuration.

    | Config Id - 28
    | Config Title - Configure the ESXi hosts firewall to only allow traffic from the authorized networks.
    """

    metadata = ControllerMetadata(
        name="firewall_rulesets",  # controller name
        path_in_schema="compliance_config.esxi.firewall_rulesets",
        # path in the schema to this controller's definition.
        configuration_id="28",  # configuration id as defined in compliance kit.
        title="Configure the ESXi hosts firewall to only allow traffic from the authorized networks.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.ESXI],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    def __init__(self):
        super().__init__()
        self.comparator_option = ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON
        self.instance_key = NAME_KEY

    def set(self, context: HostContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        """Set firewall ruleset configs in ESXi.

        :param context: ESXHostContext product instance.
        :type context: HostContext
        :param desired_values: Desired values for rulesets. List of Dict.
        :type desired_values: list
        :return: Tuple of a status (from the RemediateStatus enum) and a list of errors encountered if any.
        :rtype: tuple
        """
        pass  # pylint: disable=unnecessary-pass

    def remediate(self, context: HostContext, desired_values: Any) -> Dict:
        """Remediate current rulesets configuration drifts.

        | Sample output

        .. code-block:: json

                {
                  "status": "SUCCESS",
                  "old": [
                    {
                      "enabled": true,
                      "allow_all_ip": false,
                      "allowed_ips": {
                        "address": [
                          "192.168.0.1"
                        ],
                        "network": [
                          "192.168.121.0/8"
                        ]
                      },
                      "name": "ruleset_name"
                    }
                  ],
                  "new": [
                    {
                      "enabled": false,
                      "allow_all_ip": true,
                      "allowed_ips": {
                        "address": [
                          "192.168.0.2"
                        ],
                        "network": [
                          "192.168.121.0/8",
                          "192.168.0.0/16"
                        ]
                      },
                      "name": "ruleset_name"
                    }
                  ]
                }

        :param context: ESXContext product instance.
        :type context: EsxContext
        :param desired_values: Desired values for rulesets. List of Dict.
        :type desired_values: list
        :return: Dict of status and list of old/new values(for success) and/or errors (for failure and partial).
        :rtype: dict
        """
        logger.debug("Running remediation.")

        # validate for duplicate keys
        self._validate_input(desired_values)

        compliance_response = self.check_compliance(context, desired_values)
        if compliance_response.get(consts.STATUS) == ComplianceStatus.FAILED:
            # For compliance_status as "FAILED", return FAILED with errors.
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: compliance_response.get(consts.ERRORS, [])}

        elif compliance_response.get(consts.STATUS) == ComplianceStatus.COMPLIANT:
            # For compliant case, return SKIPPED.
            return {consts.STATUS: RemediateStatus.SKIPPED, consts.ERRORS: ["Control already compliant"]}
        else:
            # Check for non-compliant items and iterate through each of drifts and invoke remediation.
            # Scenario 1. Handle addition/removal of ruleset in desired config
            # Scenario 2: Handle drifts in ruleset.
            desired_non_compliant_configs = compliance_response.get(consts.DESIRED)
            current_non_compliant_configs = compliance_response.get(consts.CURRENT)
            logger.debug(
                f"check compliance response. "
                f"non_compliant_configs_desired = {desired_non_compliant_configs}"
                f"non_compliant_configs_current = {current_non_compliant_configs}"
            )
            old_values = []
            new_values = []
            errors = []
            desired_iter, current_iter = iter(desired_non_compliant_configs), iter(current_non_compliant_configs)
            for non_compliant_desired_config in desired_iter:
                non_compliant_current_config = next(current_iter)

                # Scenario 1. Handle addition/removal of ruleset in desired config
                if non_compliant_desired_config is None or non_compliant_current_config is None:
                    # Ruleset is added/removed in desired config.
                    # ESXi don't support creation or deletion of rulesets.
                    ruleset_name = (
                        non_compliant_desired_config.get(NAME_KEY)
                        if non_compliant_desired_config is not None
                        else non_compliant_current_config.get(NAME_KEY)
                    )
                    if non_compliant_current_config is not None:
                        errors.append(
                            f"Manual intervention required. Ruleset [{ruleset_name}] exists in host "
                            f"but not defined in desired input spec. spec={non_compliant_current_config}"
                        )
                    else:
                        errors.append(
                            f"Manual intervention required. Ruleset [{ruleset_name}] not found in host. "
                            f"spec={non_compliant_desired_config}"
                        )
                else:
                    # Scenario 2: Handle drifts in ruleset.
                    # Exclude name(unique identifier) as it is identical in current and desired.
                    # ruleset_name = current_config.pop(NAME_KEY)
                    # desired_config.pop(NAME_KEY)

                    self._set_ruleset_config(
                        context,
                        non_compliant_desired_config,
                        non_compliant_current_config,
                        desired_values,
                        new_values,
                        old_values,
                        errors,
                    )

            # create remediation output.
            # set status to success if all remediation passed for all rulesets.
            # set status to failed if all remediation failed for all rulesets.
            # set status to partial if remediation succeeded for few rulesets and failed for few.
            remediation_result = {}
            if len(new_values) > 0:
                remediation_result[consts.NEW] = new_values
                remediation_result[consts.OLD] = old_values
                remediation_result[consts.STATUS] = RemediateStatus.SUCCESS
            if len(errors) > 0:
                remediation_result[consts.ERRORS] = errors
                remediation_result[consts.STATUS] = RemediateStatus.FAILED
                if len(new_values) > 0:
                    remediation_result[consts.STATUS] = RemediateStatus.PARTIAL
            return remediation_result

    def _set_ruleset_config(
        self,
        context,
        non_compliant_desired_config,
        non_compliant_current_config,
        desired_values,
        new_values,
        old_values,
        errors,
    ):
        new = {}
        old = {}
        firewall_config = context.host_ref.configManager.firewallSystem
        ruleset_name = non_compliant_desired_config.get(NAME_KEY)
        allow_all_ip, allowed_ips = None, None
        # desired_config dict contains only non-compliant config. This operation requires other keys that are
        # compliant as well. So get full desired config from input desired_values.
        desired_config_full = next(filter(lambda config: config[NAME_KEY] == ruleset_name, desired_values))

        # ESXi vapi allow changes to
        #   1. Enable/Disable ruleset
        #   2. Enable/Disable allow_all_ip flag
        #   3. Make changes to list of IP and Networks allowed
        # Check for allowed keys present in desired_config and invoke vim API to remediate drift.
        # For set not allowed keys in desired_config, add them to error.

        for config_key in non_compliant_desired_config.keys():
            if config_key == NAME_KEY:
                continue
            if config_key == ENABLED_KEY:
                # Handle Enable/Disable Ruleset configuration.
                config = non_compliant_desired_config.get(ENABLED_KEY)
                self._toggle_ruleset(
                    firewall_config, ruleset_name, config, new, old, errors, non_compliant_current_config
                )
            elif config_key == ALLOW_ALL_IP_KEY or config_key == ALLOWED_IPS_KEY:
                # create tuples with drift and full desired configs.
                allow_all_ip = (
                    desired_config_full.get(ALLOW_ALL_IP_KEY),
                    non_compliant_desired_config.get(ALLOW_ALL_IP_KEY),
                )
                allowed_ips = (
                    desired_config_full.get(ALLOWED_IPS_KEY),
                    non_compliant_desired_config.get(ALLOWED_IPS_KEY),
                )
            else:
                # Add unsupported config keys to errors.
                errors.append(
                    f"Manual intervention required for ruleset [{ruleset_name}]. "
                    f"Remediation not supported for configuration [{config_key}]."
                    f"{non_compliant_desired_config.get(config_key)}"
                )
        # Handle allow_all_ip flag and allowed_ips configurations.
        if allow_all_ip or allowed_ips:
            self._set_allowed_ips(
                allow_all_ip,
                allowed_ips,
                firewall_config,
                ruleset_name,
                old,
                new,
                errors,
                non_compliant_current_config,
            )
        # Set ruleset name to dict to uniquely identify result.
        if len(new) > 0:
            new[NAME_KEY] = ruleset_name
            old[NAME_KEY] = ruleset_name
            new_values.append(new)
            old_values.append(old)

    def _toggle_ruleset(self, firewall_config, name, config, new, old, errors, current_config):
        try:
            if config:
                firewall_config.EnableRuleset(id=name)
            else:
                firewall_config.DisableRuleset(id=name)
            new[ENABLED_KEY] = config
            old[ENABLED_KEY] = current_config.get(ENABLED_KEY)
        except Exception as e:
            logger.error(f"Ruleset {name}.Exception in remediating {ENABLED_KEY}={config}.{e}")
            errors.append(f"Exception remediating ruleset [{name}], {str(e)}")

    def _set_allowed_ips(
        self, allow_all_ip, allowed_ips, firewall_config, ruleset_name, old, new, errors, current_config
    ):
        # firewall_config.UpdateRuleset() API overwrites entire object whenever update is made to allowedHosts.
        # So any update to firewall_rulespec.allowedHosts requires all 3 attributes
        # (allIp, ipNetwork, ipAddress) to be set even when drift is found in one of them.
        try:
            firewall_rulespec = vim.host.Ruleset.RulesetSpec()
            firewall_rulespec.allowedHosts = vim.host.Ruleset.IpList()

            firewall_rulespec.allowedHosts.allIp = allow_all_ip[0]
            firewall_rulespec.allowedHosts.ipAddress = allowed_ips[0].get(ADDRESS_KEY, [])

            ip_networks = [
                self._create_ip_network_spec(ip_network) for ip_network in allowed_ips[0].get(NETWORK_KEY, [])
            ]
            firewall_rulespec.allowedHosts.ipNetwork = ip_networks
            logger.info(
                f"Remediate ruleset {ruleset_name}. {ALLOW_ALL_IP_KEY}={allow_all_ip[0]}. {ALLOWED_IPS_KEY}={allowed_ips[0]}"
            )
            firewall_config.UpdateRuleset(id=ruleset_name, spec=firewall_rulespec)
            # Check if allow_all_ip is changed
            if allow_all_ip[1] is not None:
                new[ALLOW_ALL_IP_KEY] = allow_all_ip[1]
                old[ALLOW_ALL_IP_KEY] = current_config.get(ALLOW_ALL_IP_KEY)
            # Check if allowed_ips is changed
            if allowed_ips[1] is not None:
                new[ALLOWED_IPS_KEY] = {}
                old[ALLOWED_IPS_KEY] = {}
                # set to new values if key is found to be non-compliant.
                # desired_config dict contains non-compliant keys only.
                if ADDRESS_KEY in allowed_ips[1]:
                    new[ALLOWED_IPS_KEY][ADDRESS_KEY] = allowed_ips[1][ADDRESS_KEY]
                    old[ALLOWED_IPS_KEY][ADDRESS_KEY] = current_config.get(ALLOWED_IPS_KEY)[ADDRESS_KEY]
                if NETWORK_KEY in allowed_ips[1]:
                    new[ALLOWED_IPS_KEY][NETWORK_KEY] = allowed_ips[1][NETWORK_KEY]
                    old[ALLOWED_IPS_KEY][NETWORK_KEY] = current_config.get(ALLOWED_IPS_KEY)[NETWORK_KEY]
        except Exception as e:
            logger.error(f"Ruleset {ruleset_name}.Exception in remediation {e}")
            errors.append(f"Exception remediating ruleset [{ruleset_name}], {str(e)}")

    def get(self, context: HostContext) -> Tuple[List[dict], List[str]]:
        """Get Firewall rulesets configured in ESXi.

        | Sample output

        .. code-block:: json

            [
              {
                "allow_all_ip": false,
                "name": "test_ruleset",
                "enabled": true,
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
                    "port": 8080,
                    "direction": "inbound",
                    "protocol": "tcp",
                    "end_port": 9090
                  }
                ]
              }
            ]

        :param context: ESX context instance.
        :type context: HostContext
        :return: Tuple of list of Dict containing rulesets and list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting firewall rulesets for audit.")
        errors = None
        try:
            # Fetch all firewall rulesets. Any failure will throw an exception.
            rulesets_configured = context.host_ref.configManager.firewallSystem.firewallInfo.ruleset

            # Process each ruleset config and create ruleset json.
            rulesets = [self._to_ruleset_dict(ruleset_config) for ruleset_config in rulesets_configured]
        except Exception as e:
            logger.exception(f"Exception retrieving firewall ruleset configuration - {e}")
            errors = [str(e)]
            rulesets = []
        return rulesets, errors

    def check_compliance(self, context: HostContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: ESX context instance.
        :type context: HostContext
        :param desired_values: Desired values for rulesets.
        :type desired_values: Any
        :return: Dict of status and list of current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        # Add custom validation on input config.
        FirewallRulesetsConfig._validate_input(self, desired_values)
        return super().check_compliance(context, desired_values)

    def _find_first_non_unique_value(self, values):
        # Predicate function to validate for non-unique values
        unique_values = set()
        predicate = lambda value: value[NAME_KEY] not in unique_values and unique_values.add(value[NAME_KEY]) is None
        # Iterator to check and return first non-unique value in list
        return next(dropwhile(predicate, values), None)

    def _validate_input(self, desired_values):
        # Validate if any rule sets are using same name.
        # Raise an exception when first such occurrence is found.
        non_unique_value = self._find_first_non_unique_value(desired_values)
        if non_unique_value:
            raise ValueError(f"Found duplicate entries for ruleset. {NAME_KEY}={non_unique_value[NAME_KEY]}")

    def _to_ruleset_dict(self, ruleset_config):
        # Create rule set
        ruleset = {
            ALLOW_ALL_IP_KEY: ruleset_config.allowedHosts.allIp,
            NAME_KEY: ruleset_config.key,
            ENABLED_KEY: ruleset_config.enabled,
        }

        # Get allowed ip addresses and networks
        allowed_ips = self._to_allowed_ips_dict(ruleset_config.allowedHosts)
        ruleset[ALLOWED_IPS_KEY] = allowed_ips

        # Get all firewall rules
        ruleset[RULES_KEY] = [self._to_rule_dict(rule_config) for rule_config in ruleset_config.rule]

        return ruleset

    def _to_rule_dict(self, rule_config):
        rule = {
            PORT_KEY: rule_config.port,
            DIRECTION_KEY: rule_config.direction,
            PROTOCOL_KEY: rule_config.protocol,
        }
        if rule_config.endPort is not None:
            rule[END_PORT_KEY] = rule_config.endPort
        return rule

    def _to_allowed_ips_dict(self, allowed_hosts_config):
        allowed_ips = {
            ADDRESS_KEY: list(allowed_hosts_config.ipAddress),
            # Network format should follow standard networking CIDR.
            NETWORK_KEY: [
                self._to_network_cidr_format(network_config) for network_config in list(allowed_hosts_config.ipNetwork)
            ],
        }
        return allowed_ips

    def _to_network_cidr_format(self, network_config):
        return NETWORK_CIDR_FORMAT.format(network_config.network, network_config.prefixLength)

    def _create_ip_network_spec(self, ip_network):
        ip, prefix = ip_network.split("/", 1)
        ip_network_spec = vim.host.Ruleset.IpNetwork()
        ip_network_spec.network = ip
        ip_network_spec.prefixLength = int(prefix)
        return ip_network_spec
