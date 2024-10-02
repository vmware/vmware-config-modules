### *class* SshPortForwardingPolicy

Bases: `BaseController`

ESXi ssh port forwarding configuration. The control is automated only for vsphere 8.x and above.

Config Id - 1111
<br/>
Config Title - The ESXi host Secure Shell (SSH) daemon must disable port forwarding.
<br/>

Controller Metadata
```json
{
  "name": "ssh_port_forwarding",
  "configuration_id": "1111",
  "path_in_schema": "compliance_config.esxi.ssh_port_forwarding",
  "title": "The ESXi host Secure Shell (SSH) daemon must disable port forwarding.",
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

Get ssh port forwarding policy for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘AllowTcpForwarding’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh port forwarding policy for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘AllowTcpForwarding’ property.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the ‘AllowTcpForwarding’ config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
