### *class* DvsPortGroupNetflowConfig

Bases: `BaseController`

Class for dvs and portgroup netflow config with get and set methods.

Config Id - 417
<br/>
Config Title -The vCenter Server must only send NetFlow traffic to authorized collectors.
<br/>

Controller Metadata
```json
{
  "name": "dvs_pg_netflow_config",
  "configuration_id": "417",
  "path_in_schema": "compliance_config.vcenter.dvs_pg_netflow_config",
  "title": "The vCenter Server must only send NetFlow traffic to authorized collectors.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vcenter"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": null,
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### get(context)

Get all distributed switches for the vCenter.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  A tuple containing dict of all netflow related switch/portgroup configs and a list of error messages if any.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set method to configure ipfix configurations for all dvs and pgs..

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired value for switches and port groups.
* **Returns:**
  Tuple of status and errors if any
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of all distributed switches and port groups for netflow configuration.

Sample desired values
<br/>
```json
{
  "__GLOBAL__": {
    "ipfix_collector_ip": ""
    "ipfix_enabled": false
  },
  "__OVERRIDES__": {
    "switch_override_config": [
      {
        "switch_name": "SW1",
        "ipfix_collector_ip": "10.0.0.250"
      }
    ],
    "portgroup_override_config": [
      {
        "switch_name": "SW1",
        "port_group_name": "PG1",
        "ipfix_enabled": false
      }
    ]
  }
}
```

Sample check compliance response
<br/>
```json
{
  "status": "NON_COMPLIANT",
  "current": [
    {
      "switch_name": "Switch1",
      "ipfix_collector_ip": "10.0.0.1"
    },
    {
      "switch_name": "Switch1",
      "port_group_name": "PG1"
      "ipfix_enabled": true
    }
  ],
  "desired": {
    "__GLOBAL__": {
      "ipfix_collector_ip": ""
      "ipfix_enabled": false
    },
    "__OVERRIDES__": {
      "switch_override_config": [
        {
          "switch_name": "SW1",
          "ipfix_collector_ip": "10.0.0.250"
        }
      ],
      "portgroup_override_config": [
        {
          "switch_name": "SW1",
          "port_group_name": "PG1",
          "ipfix_enabled": false
        }
      ]
    }
  }
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for netflow config for switches and  port groups.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
