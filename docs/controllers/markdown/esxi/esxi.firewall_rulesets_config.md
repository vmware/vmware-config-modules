### *class* FirewallRulesetsConfig

Bases: `BaseController`

ESXi Firewall Rulesets configuration.

Config Id - 28
<br/>
Config Title - Configure the ESXi hosts firewall to only allow traffic from the authorized networks.
<br/>

Controller Metadata
```json
{
  "name": "firewall_rulesets",
  "configuration_id": "28",
  "path_in_schema": "compliance_config.esxi.firewall_rulesets",
  "title": "Configure the ESXi hosts firewall to only allow traffic from the authorized networks.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "esxi"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": null,
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### set(context, desired_values)

Set firewall ruleset configs in ESXi.

* **Parameters:**
  * **context** (*HostContext*) – ESXHostContext product instance.
  * **desired_values** (*list*) – Desired values for rulesets. List of Dict.
* **Returns:**
  Tuple of a status (from the RemediateStatus enum) and a list of errors encountered if any.
* **Return type:**
  tuple

#### remediate(context, desired_values)

Remediate current rulesets configuration drifts.

Sample output
<br/>
```json
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
```

* **Parameters:**
  * **context** (*EsxContext*) – ESXContext product instance.
  * **desired_values** (*list*) – Desired values for rulesets. List of Dict.
* **Returns:**
  Dict of status and list of old/new values(for success) and/or errors (for failure and partial).
* **Return type:**
  dict

#### get(context)

Get Firewall rulesets configured in ESXi.

Sample output
<br/>
```json
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
```

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of list of Dict containing rulesets and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – ESX context instance.
  * **desired_values** (*Any*) – Desired values for rulesets.
* **Returns:**
  Dict of status and list of current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
