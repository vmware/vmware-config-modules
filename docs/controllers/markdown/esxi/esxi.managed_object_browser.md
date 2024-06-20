### *class* ManagedObjectBrowser

Bases: `BaseController`

ESXi controller class to configure managed object browser settings.

Config Id - 166
<br/>
Config Title - The ESXi host must disable the Managed Object Browser (MOB).
<br/>

Controller Metadata
```json
{
  "name": "managed_object_browser",
  "configuration_id": "166",
  "path_in_schema": "compliance_config.esxi.managed_object_browser",
  "title": "The ESXi host must disable the Managed Object Browser (MOB).",
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

Get managed object browser setting for ESXi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of boolean for the managed object browser flag and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set managed object browser setting for ESXi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*boolean*) – Desired value of managed object browser flag
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
