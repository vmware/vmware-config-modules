### *class* SshPermitUserEnvironmentPolicy

Bases: `BaseController`

ESXi ssh host permit user environment configuration. The control is automated only for vsphere 8.x and above.

Config Id - 7
<br/>
Config Title - ESXi host SSH daemon does not permit user environment settings.
<br/>

Controller Metadata
```json
{
  "name": "ssh_permit_user_environment",
  "configuration_id": "7",
  "path_in_schema": "compliance_config.esxi.ssh_permit_user_environment",
  "title": "ESXi host SSH daemon does not permit user environment settings.",
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

Get ssh host permit user environment policy for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘permituserenvironment’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh host permit user environment policy for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘permituserenvironment’ config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the ssh host permit user environment config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
