### *class* HyperthreadWarningPolicy

Bases: `BaseController`

ESXi controller to enable/disable suppressing of hyperthread warning.

Config Id - 1110
<br/>
Config Title - The ESXi host must not suppress warning about unmitigated hyperthreading vulnerabilities.
<br/>

Controller Metadata
```json
{
  "name": "suppress_hyperthread_warning",
  "configuration_id": "1110",
  "path_in_schema": "compliance_config.esxi.suppress_hyperthread_warning",
  "title": "The ESXi host must not suppress warning about unmitigated hyperthreading vulnerabilities",
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

Get suppress hyperthread warning settings for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of int (1 to enable suppress and 0 to disable suppress) and a list of error messages
* **Return type:**
  Tuple

#### set(context, desired_values)

Set suppress hyperthread warning settings for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – 1 to enable suppress and 0 to disable suppress hyperthread warning.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
