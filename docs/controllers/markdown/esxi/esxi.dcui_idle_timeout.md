### *class* DcuiIdleTimeout

Bases: `BaseController`

ESXi controller class to get/set/check compliance/remediate dcui idle timeout(in seconds).

Config Id - 168
<br/>
Config Title - Set a timeout to automatically terminate idle DCUI sessions.
<br/>

Controller Metadata
```json
{
  "name": "dcui_idle_timeout",
  "configuration_id": "168",
  "path_in_schema": "compliance_config.esxi.dcui_idle_timeout",
  "title": "Set a timeout to automatically terminate idle DCUI sessions",
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

Get dcui idle timeout for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for dcui session idle timeout(in seconds) and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set dcui idle timeout for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of dcui session idle timeout(in seconds).
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
