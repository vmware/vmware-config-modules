### *class* DVPortGroupMacAddressChangePolicy

Bases: `BaseController`

Manage DV Port group MAC address change policy with get and set methods.

Config Id - 407
<br/>
Config Title - The vCenter Server must set the distributed port group MAC Address Change policy to reject.
<br/>

Controller Metadata
```json
{
  "name": "dvpg_mac_address_change_policy",
  "configuration_id": "407",
  "path_in_schema": "compliance_config.vcenter.dvpg_mac_address_change_policy",
  "title": "The vCenter Server must set the distributed port group MAC Address Change policy to reject.",
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

Get DV Port group MAC address change policy for all port groups.

Sample get call output
<br/>
```json
[
  {
    "switch_name": "SwitchB",
    "port_group_name": "dv_pg_PortGroup3",
    "allow_mac_address_change": false
  },
  {
    "switch_name": "SwitchC",
    "port_group_name": "dv_pg_PortGroup1",
    "allow_mac_address_change": true
  },
  {
    "switch_name": "SwitchA",
    "port_group_name": "dv_pg_PortGroup2",
    "allow_mac_address_change": false
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of port group and their MAC address change policy and a list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set DV Port group MAC address change policy for all port groups.

Recommended DV port group MAC address change policy: false | reject.
<br/>
Sample desired state
<br/>
```json
{
  "__GLOBAL__": {
    "allow_mac_address_change": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "port_group_name": "dv_pg_PortGroup1",
      "allow_mac_address_change": true
    }
  ],
  "ignore_disconnected_hosts": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the enabling or disabling MAC address change policy on port groups.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of all dv port group’s MAC address change policy.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for MAC address change policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate configuration drifts.

Sample desired state for remediation.
<br/>
```json
{
  "__GLOBAL__": {
    "allow_mac_address_change": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "port_group_name": "dv_pg_PortGroup1",
      "allow_mac_address_change": true
    }
  ],
  "ignore_disconnected_hosts": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for MAC address change policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
