### *class* AccountUnlockTimeInterval

Bases: `BaseController`

For ESXi, a user’s account to be locked for time interval before account can be unlocked.

Config Id - 165
<br/>
Config Title - The ESXi host must enforce an unlock timeout of certain defined minutes after a user account is locked out.
<br/>

Controller Metadata
```json
{
  "name": "account_unlock_time_interval",
  "configuration_id": "165",
  "path_in_schema": "compliance_config.esxi.account_unlock_time_interval",
  "title": "The ESXi host must enforce an unlock timeout of certain defined minutes after a user account is locked out",
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

Get unlock time interval for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for the account unlock time interval and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set unlock time interval for esxi host

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of account unlock time interval.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
