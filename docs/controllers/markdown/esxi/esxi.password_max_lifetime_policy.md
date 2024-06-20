### *class* PasswordMaxLifetimePolicy

Bases: `BaseController`

ESXi Password max lifetime configuration.

Config Id - 1123
<br/>
Config Title - The ESXi host must be configured with an appropriate maximum password age.
<br/>

Controller Metadata
```json
{
  "name": "password_max_lifetime",
  "configuration_id": "1123",
  "path_in_schema": "compliance_config.esxi.password_max_lifetime",
  "title": "The ESXi host must be configured with an appropriate maximum password age.",
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

Get max password lifetime policy for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for the max password lifetime in days and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set max password lifetime policy for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of max password lifetime in days.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
