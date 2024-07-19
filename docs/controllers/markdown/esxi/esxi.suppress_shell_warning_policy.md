### *class* SuppressShellWarningPolicy

Bases: `BaseController`

ESXi controller to enable/disable suppressing of shell warning.

Config Id - 30
<br/>
Config Title - Show warnings in the vSphere Client if local or remote shell sessions are enabled on the ESXi hosts.
<br/>

Controller Metadata
```json
{
  "name": "suppress_shell_warning",
  "configuration_id": "30",
  "path_in_schema": "compliance_config.esxi.suppress_shell_warning",
  "title": "Show warnings in the vSphere Client if local or remote shell sessions are enabled on the ESXi hosts",
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

Get suppress shell warning settings for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of int (1 to enable suppress and 0 to disable suppress) and a list of error messages
* **Return type:**
  Tuple

#### set(context, desired_values)

Set suppress shell warning settings for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – 1 to enable suppress and 0 to disable suppress shell warning.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
