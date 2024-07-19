### *class* HostdLogLevel

Bases: `BaseController`

ESXi controller class to get/set/check compliance/remediate hostd log level settings.

Config Id - 179
<br/>
Config Title - The ESXi host must produce audit records containing information to establish what type of events occurred.
<br/>

Controller Metadata
```json
{
  "name": "hostd_log_level",
  "configuration_id": "179",
  "path_in_schema": "compliance_config.esxi.hostd_log_level",
  "title": "The ESXi host must produce audit records containing information to establish what type of events occurred",
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

Get hostd log level settings for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of hostd log level string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set hostd log level settings for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value of hostd log level.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
