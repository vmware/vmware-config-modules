### *class* DVPortGroupVlanTrunkingConfig

Bases: `BaseController`

DV Port group Vlan trunking config get and set methods.

Config Id - 1227
<br/>
Config Title - The vCenter Server must not configure VLAN Trunking unless Virtual Guest
Tagging (VGT) is required and authorized.
<br/>

Controller Metadata
```json
{
  "name": "dvpg_vlan_trunking_authorized_check",
  "configuration_id": "1227",
  "path_in_schema": "compliance_config.vcenter.dvpg_vlan_trunking_authorized_check",
  "title": "The vCenter Server must not configure VLAN Trunking unless Virtual Guest Tagging (VGT) is required and authorized.",
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
    switch_name: "SDDC-Dswitch-Private",
    port_group_name: "SDDC-DPortGroup-VSAN",
    vlan_info: {
      vlan_type: "VLAN trunking",
      vlan_ranges:[
        { start: 0, end: 90},
        { start: 120, end: 200}
      ]
    }
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

Set vlan config for DV port groups to remediate trunking vlan in the configuration.

Sample desired state
<br/>
```json
[
  {
    switch_name: "SDDC-Dswitch-Private",
    port_group_name: "SDDC-DPortGroup-VSAN",
    vlan_info: {
      vlan_type: "VLAN trunking",
      vlan_ranges:[
        { start: 0, end: 90},
        { start: 120, end: 200}
      ]
    }
  }
]
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values containing vlan trunking configs.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance for all dv port groups if vlan trunking is in configuration.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Dict containing VLAN trunking configs  to be excluded checked.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
