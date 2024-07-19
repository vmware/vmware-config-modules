### *class* DvFilterBindIpConfig

Bases: `BaseController`

ESXi dvFilter configuration.

Config Id - 169
<br/>
Config Title - Use of the dvFilter network APIs must be restricted.
<br/>

Controller Metadata
```json
{
  "name": "dv_filter_bind_ip_config",
  "configuration_id": "169",
  "path_in_schema": "compliance_config.esxi.dv_filter_bind_ip_config",
  "title": "Use of the dvFilter network APIs must be restricted.",
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

Get dvFilter configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of dict for DVFilterBindIpAdress and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set DVFilterBindIpAdress for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict such as {“security_appliance_ip”: “10.0.0.250”} to update DVFilterBindIpAddress.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
