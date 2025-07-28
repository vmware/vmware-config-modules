### *class* DVPortGroupPromiscuousModePolicy

Bases: `BaseController`

Class for managing DV Port group promiscuous mode policy with get and set methods.

Config Id - 405
<br/>
Config Title - The vCenter Server must set the distributed port group Promiscuous Mode policy to reject.
<br/>

Controller Metadata
```json
{
  "name": "dvpg_promiscuous_mode_policy",
  "configuration_id": "405",
  "path_in_schema": "compliance_config.vcenter.dvpg_promiscuous_mode_policy",
  "title": "The vCenter Server must set the distributed port group Promiscuous Mode policy to reject.",
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

Get DV Port group promiscuous mode policy for all port groups.

Sample get call output for remediation.
<br/>
```json
[
  {
    "switch_name": "SwitchB",
    "port_group_name": "dv_pg_PortGroup3",
    "promiscuous_mode": false
  },
  {
    "switch_name": "SwitchC",
    "port_group_name": "dv_pg_PortGroup1",
    "promiscuous_mode": true
  },
  {
    "switch_name": "SwitchA",
    "port_group_name": "dv_pg_PortGroup2",
    "promiscuous_mode": false
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of port group and their promiscuous mode policy and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set DV Port group promiscuous mode policy for all port groups.

Sample desired state
<br/>
```json
{
  "__GLOBAL__": {
    "promiscuous_mode": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "port_group_name": "dv_pg_PortGroup1",
      "promiscuous_mode": true
    }
  ],
  "ignore_disconnected_hosts": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the enabling or disabling promiscuous mode on port groups.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of all dv port group’s promiscuous mode policy.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for promiscuous mode policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate configuration drifts by applying desired values.

Recommended promiscuous mode policy: false | reject
<br/>
Sample desired state for remdiation.
<br/>
```json
{
  "__GLOBAL__": {
    "promiscuous_mode": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "port_group_name": "dv_pg_PortGroup1",
      "promiscuous_mode": true
    }
  ],
  "ignore_disconnected_hosts": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for promiscuous mode policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
