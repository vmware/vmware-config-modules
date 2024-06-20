### *class* SSOPasswordMinimumLengthPolicy

Bases: `BaseController`

Manage SSO Password min length  Policy with get and set methods.

Config Id - 410
<br/>
Config Title - The vCenter Server passwords must meet minimum password length policy.
<br/>

Controller Metadata
```json
{
  "name": "sso_password_minimum_length",
  "configuration_id": "410",
  "path_in_schema": "compliance_config.vcenter.sso_password_minimum_length",
  "title": "The vCenter Server passwords must meet minimum password length policy.",
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

Get SSO password min length policy.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of an integer for the min password length and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set SSO password min length policy.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for the min password length.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
