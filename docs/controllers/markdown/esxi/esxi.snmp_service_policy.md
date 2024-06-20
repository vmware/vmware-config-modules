### *class* SnmpServicePolicy

Bases: `BaseController`

ESXi controller to start/stop snmp service..

Config Id - 1128
<br/>
Config Title - Configure or disable SNMP.
<br/>

Controller Metadata
```json
{
  "name": "snmp_service_policy",
  "configuration_id": "1128",
  "path_in_schema": "compliance_config.esxi.snmp_service_policy",
  "title": "Configure or disable SNMP",
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

Get snmp service status for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict such as {“service_running”: True, “service_policy”: “off”} and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Start/stop snmp service for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of { “service_running”: True, “service_policy”: “off”} to start/stop service or update policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
