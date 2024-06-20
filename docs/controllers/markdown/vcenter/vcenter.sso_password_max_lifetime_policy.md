### *class* SSOPasswordMaxLifetimePolicy

Bases: `BaseController`

Manage SSO Password Max Lifetime Policy with get and set methods.

Config Id - 421
<br/>
Config Title - The vCenter server passwords should meet max password lifetime policy.
<br/>

Controller Metadata
```json
{
  "name": "sso_password_max_lifetime",
  "configuration_id": "421",
  "path_in_schema": "compliance_config.vcenter.sso_password_max_lifetime",
  "title": "The vCenter server passwords should meet max password lifetime policy.",
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

Get SSO max password lifetime policy.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of an integer for the max password lifetime in days and a list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set SSO max password lifetime policy.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for the SSO max password lifetime in days.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
