### *class* SshServicePolicy

Bases: `BaseController`

ESXi controller to start/stop/update ssh service.

Config Id - 111
<br/>
Config Title - The ESXi host must be configured to disable non-essential capabilities by disabling SSH.
<br/>

Controller Metadata
```json
{
  "name": "ssh_service_policy",
  "configuration_id": "111",
  "path_in_schema": "compliance_config.esxi.ssh_service_policy",
  "title": "The ESXi host must be configured to disable non-essential capabilities by disabling SSH",
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

Get ssh service status for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict such as {“service_running”: True, “service_policy”: “off”} and list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Start/stop ssh service for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict with keys “service_running” and “service_policy” to start/stop service or update policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
