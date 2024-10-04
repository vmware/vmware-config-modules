### *class* SnmpConfig

Bases: `BaseController`

ESXi controller to get/set snmp configurations for ESXi host.

Config Id - 1114
<br/>
Config Title - SNMP must be configured properly on the ESXi host.
<br/>

Controller Metadata
```json
{
  "name": "snmp_config",
  "configuration_id": "1114",
  "path_in_schema": "compliance_config.esxi.snmp_config",
  "title": "SNMP must be configured properly on the ESXi host.",
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

Get snmp configs for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of boolean value True/False and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set snmp config for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – boolean value True/False to update config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
