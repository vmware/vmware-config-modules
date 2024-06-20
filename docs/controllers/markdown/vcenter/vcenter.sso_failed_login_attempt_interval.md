### *class* SSOFailedLoginAttemptInterval

Bases: `BaseController`

Manage SSO Failed Login Attempt Interval Policy with get and set methods.

Config Id - 434
<br/>
Config Title - The vCenter server should meet failed login attempts interval.
<br/>

Controller Metadata
```json
{
  "name": "sso_failed_login_attempts_interval",
  "configuration_id": "434",
  "path_in_schema": "compliance_config.vcenter.sso_failed_login_attempts_interval",
  "title": "The vCenter server should meet failed login attempts interval.",
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

Get SSO failed login attempt interval.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of an integer for the failed login attempt interval in seconds and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set SSO failed login attempt interval.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for the SSO failed login attempt interval in seconds.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple
