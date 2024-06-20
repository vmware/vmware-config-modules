### *class* VpxLogLevelConfig

Bases: `BaseController`

Manage VPX Logging level with get and set methods.

Config Id - 404
<br/>
Config Title - The vCenter Server must produce audit records containing information to establish what type of
events occurred.
<br/>

Controller Metadata
```json
{
  "name": "vpx_log_level_config",
  "configuration_id": "404",
  "path_in_schema": "compliance_config.vcenter.vpx_log_level_config",
  "title": "The vCenter Server must produce audit records containing information to establish what type of events occurred.",
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
  "functional_test_targets": []
}
```

#### get(context)

Get VPX log level config.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of VPX logging level as string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set VPX logging level.

Recommended log level: info
<br/>
Supported log levels : [“none”, “error”, “warning”, “info”, “verbose”, “trivia”]
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*String*) – Desired values for VPX logging level config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
