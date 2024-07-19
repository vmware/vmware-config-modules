### *class* ManagedObjectBrowser

Bases: `BaseController`

Manage vCenter managed object browser config with get and set methods.
[Risk] Set/remediate method also restarts ‘vpxd’ service post settings change to reflect the changes.

Config Id - 0000
<br/>
Config Title - The vCenter Server must disable the managed object browser (MOB) at all times when not required for troubleshooting or maintenance of managed objects.
<br/>

Controller Metadata
```json
{
  "name": "managed_object_browser",
  "configuration_id": "0000",
  "path_in_schema": "compliance_config.vcenter.managed_object_browser",
  "title": "The vCenter Server must disable the managed object browser (MOB) at all times when not required for troubleshooting or maintenance of managed objects",
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
  "functional_test_targets": [
    "vcenter"
  ]
}
```

#### get(context)

Get managed object browser config on vCenter.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of bool and a list of error messages if any.
* **Return type:**
  tuple

#### set(context, desired_values)

Set managed object browser config on vCenter.
Restart ‘vpxd’ service post changing the MOB settings to reflect the changes.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*bool*) – Desired values for the managed object browser config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
