### *class* LockdownModeConfig

Bases: `BaseController`

ESXi controller to get/set lockdown mode.

Config Id - 31
<br/>
Config Title - Enable Normal lockdown mode on the host.
<br/>

Controller Metadata
```json
{
  "name": "lockdown_mode",
  "configuration_id": "31",
  "path_in_schema": "compliance_config.esxi.lockdown_mode",
  "title": "Enable Normal lockdown mode on the host",
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

Get lockdown mode for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of lockdown mode and a list of errors if any..
* **Return type:**
  Tuple

#### set(context, desired_values)

Set lockdown mode for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Lockdown mode - NORMAL or DISABLED or STRICT.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
