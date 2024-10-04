### *class* LogLocationConfig

Bases: `BaseController`

ESXi controller to get/set/check_compliance/remediate persistent log location config.

Config Id - 136
<br/>
Config Title - Configure a persistent log location for all locally stored logs.
<br/>

Controller Metadata
```json
{
  "name": "log_location_config",
  "configuration_id": "136",
  "path_in_schema": "compliance_config.esxi.log_location_config",
  "title": "Configure a persistent log location for all locally stored logs",
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

Get persistent log location config for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dictionary with keys “log_location” and “is_persistent” and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set persistent log location config for esxi host.
It sets the log location and verifies if the log location persistent criteria matches with desired or not.
If it does not, then reverts to the original log location and report error

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dictionary with keys “log_location” and “is_persistent”
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
