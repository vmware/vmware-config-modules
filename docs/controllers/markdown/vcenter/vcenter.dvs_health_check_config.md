### *class* DVSHealthCheckConfig

Bases: `BaseController`

Manage DVS health check config with get and set methods.

Config Id - 1200
<br/>
Config Title - The vCenter Server must disable the distributed virtual switch health check.
<br/>

Controller Metadata
```json
{
  "name": "dvs_health_check",
  "configuration_id": "1200",
  "path_in_schema": "compliance_config.vcenter.dvs_health_check",
  "title": "The vCenter Server must disable the distributed virtual switch health check.",
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

Get DVS health check status for all virtual switches.

Sample get call output
<br/>
```json
[
  {
    "switch_name": "SwitchB",
    "health_check_enabled": false
  },
  {
    "switch_name": "SwitchC",
    "health_check_enabled": true
  },
  {
    "switch_name": "SwitchA",
    "health_check_enabled": false
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of DV switch health check status  and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Enable/Disable health check for DV switches.

Recommended value for DV switch health check: false | disabled
<br/>
Sample desired state
<br/>
```json
{
  "__GLOBAL__": {
    "health_check_enabled": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "health_check_enabled": true
    }
  ],
  "ignore_disconnected_hosts": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the enabling or disabling DVS health check config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of health check configs for all DV switches.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for DV switch health check config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate configuration drifts by applying desired values.

Sample desired state for remediation
<br/>
```json
{
  "__GLOBAL__": {
    "health_check_enabled": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "health_check_enabled": true
    }
  ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for DV switch health check config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
