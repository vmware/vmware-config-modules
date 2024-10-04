### *class* SshPermitEmptyPasswordsPolicy

Bases: `BaseController`

ESXi ssh host permit empty passwords settings.
The control is automated only for vsphere 8.x and above. No remediation support as the property is no configurable.

Config Id - 6
<br/>
Config Title - ESXi host SSH daemon rejects authentication using an empty password.
<br/>

Controller Metadata
```json
{
  "name": "ssh_permit_empty_passwords",
  "configuration_id": "6",
  "path_in_schema": "compliance_config.esxi.ssh_permit_empty_passwords",
  "title": "ESXi host SSH daemon rejects authentication using an empty password",
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

Get ssh host permit empty passwords settings for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘permitemptypasswords’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh host permit empty passwords settings for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘permitemptypasswords’ config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the ssh host permit empty passwords settings.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
