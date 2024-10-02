### *class* SshX11ForwardingPolicy

Bases: `BaseController`

ESXi ssh host x11 forwarding settings.
The control is automated only for vsphere 8.x and above. No remediation support as the property is no configurable.

Config Id - 14
<br/>
Config Title - ESXi host SSH daemon refuses X11 forwarding.
<br/>

Controller Metadata
```json
{
  "name": "ssh_x11_forwarding",
  "configuration_id": "14",
  "path_in_schema": "compliance_config.esxi.ssh_x11_forwarding",
  "title": "ESXi host SSH daemon refuses X11 forwarding",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "esxi"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": "REMEDIATION_SKIPPED",
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### get(context)

Get ssh host x11 forwarding settings for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘x11forwarding’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh host x11 forwarding settings for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘x11forwarding’ config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the ssh host x11 forwarding settings.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
