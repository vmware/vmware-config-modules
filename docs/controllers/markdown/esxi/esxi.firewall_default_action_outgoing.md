### *class* FirewallDefaultActionOutgoing

Bases: `BaseController`

ESXi controller to get/set firewall default action for outgoing traffic.

Config Id - 106
<br/>
Config Title - The ESXi host must configure the firewall to block outgoing network traffic by default.
<br/>

Controller Metadata
```json
{
  "name": "firewall_default_action_outgoing",
  "configuration_id": "106",
  "path_in_schema": "compliance_config.esxi.firewall_default_action_outgoing",
  "title": "The ESXi host must configure the firewall to block outgoing network traffic by default",
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

Get firewall default action for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of str value DROP/PASS and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set firewall default action for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – DROP/PASS to block/allow the network traffic.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
