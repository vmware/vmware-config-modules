### *class* PluginConfig

Bases: `BaseController`

Manage vCenter Server plugin configs.

Config Id - 406
<br/>
Config Title - vCenter Server plugins must be verified.
<br/>

Controller Metadata
```json
{
  "name": "plugin_config",
  "configuration_id": "406",
  "path_in_schema": "compliance_config.vcenter.plugin_config",
  "title": "vCenter Server plugins must be verified.",
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
  "functional_test_targets": [
    "vcenter"
  ]
}
```

#### get(context)

Get vCenter server plugin config.

Sample get call output:
<br/>
```json
[
  {
    "id": "com.vmware.lcm.client",
    "vendor": ""VMware, Inc.",
    "type": "REMOTE",
  },
  {
    "id": "com.vmware.vlcm.client",
    "vendor": ""VMware, Inc.",
    "type": "REMOTE",
  },
  {
    "id": "com.vmware.vum.client",
    "vendor": ""VMware, Inc.",
    "type": "LOCAL",
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of dict and a list of error messages if any.
* **Return type:**
  tuple

#### set(context, desired_values)

Sets vCenter plugin config.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the DNS config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current plugin configuration in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the vCenter plugin config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediate configuration drifts by applying desired values.

Sample desired state
<br/>
```json
{
  "id": "com.vmware.vum.client",
  "vendor": "VMware, Inc.",
  "type": "LOCAL",
  "versions": [
    "8.0.3.24091160"
  ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for VM migrate encryption policy
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
