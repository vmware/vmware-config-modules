### *class* PasswordQualityConfig

Bases: `BaseController`

ESXi password quality control configuration.

Config Id - 22
<br/>
Config Title - The ESXi host must enforce password complexity.
<br/>

Controller Metadata
```json
{
  "name": "password_quality_config",
  "configuration_id": "22",
  "path_in_schema": "compliance_config.esxi.password_quality_config",
  "title": "The ESXi host must enforce password complexity.",
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

#### get(context)

Get password quality control configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of dict for password quality control configs and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set password quality control configurations for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of desired configs to update ESXi password quality control configurations.
* **Returns:**
  Tuple of “status” and list of error messages.
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
