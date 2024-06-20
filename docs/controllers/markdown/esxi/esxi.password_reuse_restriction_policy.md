### *class* PasswordReuseRestrictionPolicy

Bases: `BaseController`

ESXi Password history setting configuration for restricting password reuse.

Config Id - 109
<br/>
Config Title - Configure the password history setting to restrict the reuse of passwords.
<br/>

Controller Metadata
```json
{
  "name": "password_reuse_restriction",
  "configuration_id": "109",
  "path_in_schema": "compliance_config.esxi.password_reuse_restriction",
  "title": "Configure the password history setting to restrict the reuse of passwords",
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

Get password history setting for esxi host to restrict the reuse of passwords.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for the number of previous passwords restricted and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set password history setting for esxi host to restrict the reuse of passwords.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of number of previous passwords restricted.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
