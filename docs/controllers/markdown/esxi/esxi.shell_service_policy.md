### *class* ShellServicePolicy

Bases: `BaseController`

ESXi controller to start/stop/update shell service.

Config Id - 112
<br/>
Config Title - Stop the ESXi shell service and set the startup policy.
<br/>

Controller Metadata
```json
{
  "name": "shell_service_policy",
  "configuration_id": "112",
  "path_in_schema": "compliance_config.esxi.shell_service_policy",
  "title": "Stop the ESXi shell service and set the startup policy.",
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

Get shell service status for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict such as {“service_running”: True, “service_policy”: “off”} and list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Start/stop shell service for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of { “service_running”: True, “service_policy”: “off”} to start/stop service or update policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
