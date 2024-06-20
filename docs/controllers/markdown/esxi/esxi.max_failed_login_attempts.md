### *class* MaxFailedLoginAttempts

Bases: `BaseController`

For ESXi, max failed login attempts before account is locked.

Config Id - 34
<br/>
Config Title - Set the maximum number of failed login attempts before an account is locked.
<br/>

Controller Metadata
```json
{
  "name": "max_failed_login_attempts",
  "configuration_id": "34",
  "path_in_schema": "compliance_config.esxi.max_failed_login_attempts",
  "title": "Set the maximum number of failed login attempts before an account is locked",
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

Get max failed login attempts for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for the max failed login attempts and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set max failed login attempts for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of max failed login attempts.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
