### *class* CimServicePolicy

Bases: `BaseController`

ESXi controller to start/stop/update cim service.

Config Id - 1126
<br/>
Config Title - The ESXi CIM service must be disabled.
<br/>

Controller Metadata
```json
{
  "name": "cim_service_policy",
  "configuration_id": "1126",
  "path_in_schema": "compliance_config.esxi.cim_service_policy",
  "title": "The ESXi CIM service must be disabled.",
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

Get cim service status for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict such as {“service_running”: True, “service_policy”: “off”} and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Start/stop cim service for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of { “service_running”: True, “service_policy”: “off”} to start/stop service or update policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
