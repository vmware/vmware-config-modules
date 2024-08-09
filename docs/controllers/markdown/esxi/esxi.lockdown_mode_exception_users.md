### *class* LockdownModeExceptionUsers

Bases: `BaseController`

ESXi controller to get/set exception user list for lockdown mode.

Config Id - 125
<br/>
Config Title - The ESXi host must verify the exception users list for lockdown mode.
<br/>

Controller Metadata
```json
{
  "name": "lockdown_mode_exception_users",
  "configuration_id": "125",
  "path_in_schema": "compliance_config.esxi.lockdown_mode_exception_users",
  "title": "The ESXi host must verify the exception users list for lockdown mode",
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

Get lockdown mode exception users list for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of lockdown mode exception users list and a list of errors if any..
* **Return type:**
  Tuple

#### set(context, desired_values)

Set lockdown mode exception users list for esxi host. These users should be valid users which are
already configured on the host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*list*) – List of lockdown mode exception users.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.
USERS_TO_BE_IGNORED will be filtered out from current and desired values before running check compliance.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*list*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
