### *class* LockdownDcuiAccessUsers

Bases: `BaseController`

ESXi controller class to get/set/check compliance/remediate dcui access users(with unconditional access).

Config Id - 163
<br/>
Config Title - The ESXi host must verify the DCUI.Access list.
<br/>

Controller Metadata
```json
{
  "name": "lockdown_dcui_access_users",
  "configuration_id": "163",
  "path_in_schema": "compliance_config.esxi.lockdown_dcui_access_users",
  "title": "The ESXi host must verify the DCUI.Access list",
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

Get dcui access users (with unconditional access) configured for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of list of dcui access users and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set dcui access users (with unconditional access) configured for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*list*) – Desired value of dcui access users to be configured.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
