### *class* SSOPasswordReusePolicy

Bases: `BaseController`

Manage SSO Password reuse restriction Policy with get and set methods.

Config Id - 403
<br/>
Config Title - The vCenter Server must prohibit password reuse.
<br/>

Controller Metadata
```json
{
  "name": "sso_password_reuse_restriction",
  "configuration_id": "403",
  "path_in_schema": "compliance_config.vcenter.sso_password_reuse_restriction",
  "title": "The vCenter Server must prohibit password reuse.",
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

Get SSO password reuse restriction policy.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of an integer for the number of previous passwords restricted and a list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set SSO password reuse restriction  policy.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for the number of previous passwords restricted.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
