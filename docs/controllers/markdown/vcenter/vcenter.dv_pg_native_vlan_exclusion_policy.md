### *class* DVPortGroupNativeVlanExclusionConfig

Bases: `BaseController`

Manage DV Port group Native Vlan exclusion config with get and set methods.

Config Id - 1201
<br/>
Config Title - Configure all port groups to a value different from the value of the native VLAN.
<br/>

Controller Metadata
```json
{
  "name": "dvpg_excluded_native_vlan_policy",
  "configuration_id": "1201",
  "path_in_schema": "compliance_config.vcenter.dvpg_excluded_native_vlan_policy",
  "title": "Configure all port groups to a value different from the value of the native VLAN.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vcenter"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": "REMEDIATION_SKIPPED",
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### get(context)

Get DV Port group Native Vlan exclusion config for all applicable port groups.

Sample get call output
<br/>
```json
[
  {
    "switch_name": "DSwitch-test",
    "port_group_name": "DPortGroup-test",
    "vlan": 1
  },
  {
    "switch_name": "DSwitch-test",
    "port_group_name": "DPortGroup",
    "vlan": ["1-100", "105", "200-250"]
  },
  {
    "switch_name": "SDDC-Dswitch-Private",
    "port_group_name": "SDDC-DPortGroup-vMotion",
    "vlan": 1
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of port group and their vlan configs and a list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set vlan config for DV port groups excluding native vlan in the configuration.

Sample desired state
<br/>
```json
{
  "native_vlan_id_to_exclude": 1
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values containing native vlan id to be excluded from port group configurations.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of all dv port groups against native vlan id to be excluded from configuration.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Dict containing Native VLAN ID to be excluded from port group configurations.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
