### *class* SshPermitTunnelPolicy

Bases: `BaseController`

ESXi ssh permit tunnel configuration. The control is automated only for vsphere 8.x and above.

Config Id - 16
<br/>
Config Title - ESXi host SSH daemon refuses tunnels.
<br/>

Controller Metadata
```json
{
  "name": "ssh_permit_tunnel",
  "configuration_id": "16",
  "path_in_schema": "compliance_config.esxi.ssh_permit_tunnel",
  "title": "ESXi host SSH daemon refuses tunnels.",
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

Get ssh host permit tunnel policy for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘permittunnel’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh host permit tunnel policy for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘permittunnel’ config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the host permit tunnel config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
