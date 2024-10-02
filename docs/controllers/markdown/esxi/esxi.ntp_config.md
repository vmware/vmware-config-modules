### *class* NtpConfig

Bases: `BaseController`

ESXi controller to get/set ntp configurations for hosts.

Config Id - 147
<br/>
Config Title - ESXi host must configure NTP time synchronization.
<br/>

Controller Metadata
```json
{
  "name": "ntp_config",
  "configuration_id": "147",
  "path_in_schema": "compliance_config.esxi.ntp_config",
  "title": "ESXi host must configure NTP time synchronization.",
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

Get ntp configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict ({“protocol”: “ntp”, “server”: [“10.0.0.250”]}) and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ntp configurations for esxi host based on desired values.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of { “protocol”: “ntp”, “server”: [“10.0.0.250”] }.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
