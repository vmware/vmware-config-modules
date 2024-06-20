### *class* SSOPasswordMinLowercaseCharacterPolicy

Bases: `BaseController`

Class for SSO Password min lowercase character Policy with get and set methods.

Config Id - 413
<br/>
Config Title - The vCenter Server passwords must must meet minimum lowercase character policy.
<br/>

Controller Metadata
```json
{
  "name": "sso_password_min_lowercase_characters",
  "configuration_id": "413",
  "path_in_schema": "compliance_config.vcenter.sso_password_min_lowercase_characters",
  "title": "The vCenter Server passwords must must meet minimum lowercase character policy.",
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

Get SSO password min lowercase character policy.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of an integer for the min number of lower case characters and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set SSO password min lowercase character policy.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for the min number of lower case characters.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
