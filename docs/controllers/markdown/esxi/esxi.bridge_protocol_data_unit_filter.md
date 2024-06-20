### *class* BridgeProtocolDataUnitFilter

Bases: `BaseController`

ESXi controller to get and set bridge protocol data unit filter.

Config Id - 43
<br/>
Config Title - Enable the Bridge Protocol Data Unit (BPDU) filter.
<br/>

Controller Metadata
```json
{
  "name": "bridge_protocol_data_unit_filter",
  "configuration_id": "43",
  "path_in_schema": "compliance_config.esxi.bridge_protocol_data_unit_filter",
  "title": "Enable the Bridge Protocol Data Unit (BPDU) filter",
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

Get bridge protocol data unit filter.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of int (1 to enable, 0 to disable) and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set bridge protocol data unit filter

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – 1 to enable and 0 to disable BPDU filter.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
