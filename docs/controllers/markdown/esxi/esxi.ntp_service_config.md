### *class* NtpServiceConfig

Bases: `BaseController`

ESXi controller to start/stop ntp service..

Config Id - 149
<br/>
Config Title - Start NTP service on the ESXi host.
<br/>

Controller Metadata
```json
{
  "name": "ntp_service_config",
  "configuration_id": "149",
  "path_in_schema": "compliance_config.esxi.ntp_service_config",
  "title": "Start NTP service on the ESXi host.",
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

Get ntp service running status for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict ({“service_running”: True}) and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Start/stop ntp service for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of { “service_running”: True” } to start/stop service.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
