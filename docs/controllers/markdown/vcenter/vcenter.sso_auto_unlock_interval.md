### *class* SSOAutoUnlockInterval

Bases: `BaseController`

Manage SSO Auto Unlock Interval Policy with get and set methods.

Config Id - 435
<br/>
Config Title - The vCenter server passwords should meet max auto unlock interval policy.
<br/>

Controller Metadata
```json
{
  "name": "sso_auto_unlock_interval",
  "configuration_id": "435",
  "path_in_schema": "compliance_config.vcenter.sso_auto_unlock_interval",
  "title": "The vCenter server passwords should meet max auto unlock interval policy.",
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

Get SSO auto unlock interval.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of an integer for the auto unlock interval in seconds and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set SSO auto unlock interval.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for the SSO auto unlock interval in seconds.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple
