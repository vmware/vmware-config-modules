### *class* SshCompressionPolicy

Bases: `BaseController`

ESXi ssh host compression settings.
The control is automated only for vsphere 8.x and above. No remediation support as the property is no configurable.

Config Id - 12
<br/>
Config Title - Disallow compression for the ESXi host SSH daemon.
<br/>

Controller Metadata
```json
{
  "name": "ssh_compression",
  "configuration_id": "12",
  "path_in_schema": "compliance_config.esxi.ssh_compression",
  "title": "Disallow compression for the ESXi host SSH daemon",
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

Get ssh host compression settings for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘compression’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh host compression settings for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘compression’ config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the ssh host compression settings.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
