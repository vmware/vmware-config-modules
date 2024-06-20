### *class* SSOMaxFailedLoginAttempts

Bases: `BaseController`

Manage SSO Max Failed Login Attempts Policy with get and set methods.

Config Id - 436
<br/>
Config Title - The vCenter server should meet max failed login attempts.
<br/>

Controller Metadata
```json
{
  "name": "sso_max_failed_login_attempts",
  "configuration_id": "436",
  "path_in_schema": "compliance_config.vcenter.sso_max_failed_login_attempts",
  "title": "The vCenter server should meet max failed login attempts.",
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

Get SSO max failed login attempts.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of an integer for the max failed login attempts and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set SSO max failed login attempts.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for the SSO max failed login attempts.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
