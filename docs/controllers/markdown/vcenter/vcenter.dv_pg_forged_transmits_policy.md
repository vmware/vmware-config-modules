### *class* DVPortGroupForgedTransmitsPolicy

Bases: `BaseController`

Manage DV Port group Forged Transmits policy with get and set methods.

Config Id - 450
<br/>
Config Title - The vCenter Server must set the distributed port group Forged Transmits policy to reject.
<br/>

Controller Metadata
```json
{
  "name": "dvpg_forged_transmits_policy",
  "configuration_id": "450",
  "path_in_schema": "compliance_config.vcenter.dvpg_forged_transmits_policy",
  "title": "The vCenter Server must set the distributed port group Forged Transmits policy to reject.",
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

Get DV Port group Forged Transmits policy for all port groups.

Sample get call output
<br/>
```json
[
  {
    "switch_name": "SwitchB",
    "port_group_name": "dv_pg_PortGroup3",
    "allow_forged_transmits": false
  },
  {
    "switch_name": "SwitchC",
    "port_group_name": "dv_pg_PortGroup1",
    "allow_forged_transmits": true
  },
  {
    "switch_name": "SwitchA",
    "port_group_name": "dv_pg_PortGroup2",
    "allow_forged_transmits": false
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of port group and their Forged Transmits policy and a list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set DV Port group Forged Transmits policy for all port groups except uplink port groups.

Recommended DV port group Forged Transmits policy: false | reject.
<br/>
Sample desired state
<br/>
```json
{
  "__GLOBAL__": {
    "allow_forged_transmits": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "port_group_name": "dv_pg_PortGroup1",
      "allow_forged_transmits": true
    }
  ],
  "ignore_disconnected_hosts": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the enabling or disabling Forged Transmits policy on port groups.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of all non-uplink dv port groups Forged Transmits policy.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for Forged Transmits policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate configuration drifts on all non-uplink DV port groups.

Sample desired state for remediation.
<br/>
```json
{
  "__GLOBAL__": {
    "allow_forged_transmits": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "port_group_name": "dv_pg_PortGroup1",
      "allow_forged_transmits": true
    }
  ],
  "ignore_disconnected_hosts": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for Forged Transmits policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
