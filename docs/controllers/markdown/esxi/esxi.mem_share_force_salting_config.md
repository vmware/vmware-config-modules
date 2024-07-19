### *class* MemShareForceSaltingConfig

Bases: `BaseController`

ESXi controller to get/update Mem.ShareForceSalting configuration.

Config Id - 138
<br/>
Config Title - The ESXi host must disable Inter-VM transparent page sharing.
<br/>

Controller Metadata
```json
{
  "name": "mem_share_force_salting_config",
  "configuration_id": "138",
  "path_in_schema": "compliance_config.esxi.mem_share_force_salting_config",
  "title": "The ESXi host must disable Inter-VM transparent page sharing.",
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

Get Mem.ShareForceSalting configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of int value (such as 2) for mem share forcing salt config and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set Mem.ShareForceSalting for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – value such as 2 to update Mem.ShareForceSalting.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
