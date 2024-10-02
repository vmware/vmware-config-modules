### *class* SshGatewayPortsPolicy

Bases: `BaseController`

ESXi ssh gateway ports configuration. The control is automated only for vsphere 8.x and above.

Config Id - 13
<br/>
Config Title - ESXi host SSH daemon does not contain gateway ports.
<br/>

Controller Metadata
```json
{
  "name": "ssh_gateway_ports",
  "configuration_id": "13",
  "path_in_schema": "compliance_config.esxi.ssh_gateway_ports",
  "title": "ESXi host SSH daemon does not contain gateway ports.",
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

Get ssh host gateway ports policy for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘gatewayports’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh host gateway ports policy for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘gatewayports’ config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the host gateway ports config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
