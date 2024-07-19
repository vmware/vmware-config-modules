### *class* UserworldMemoryZeroingConfig

Bases: `BaseController`

ESXi controller to get/update Mem.MemEagerZero configuration.

Config Id - 1122
<br/>
Config Title - The ESXi host must enable volatile key destruction.
<br/>

Controller Metadata
```json
{
  "name": "userworld_memory_zeroing_config",
  "configuration_id": "1122",
  "path_in_schema": "compliance_config.esxi.userworld_memory_zeroing_config",
  "title": "The ESXi host must enable volatile key destruction",
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

Get Mem.MemEagerZero configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of integer and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set Mem.MemEagerZero for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – 1 to enable or 0 to disable userworld memory zeroing.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
