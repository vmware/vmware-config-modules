### *class* SshHostBasedAuthPolicy

Bases: `BaseController`

ESXi ssh host based authentication configuration. The control is automated only for vsphere 8.x and above.

Config Id - 4
<br/>
Config Title - ESXi host SSH daemon does not allow host-based authentication.
<br/>

Controller Metadata
```json
{
  "name": "ssh_host_based_authentication",
  "configuration_id": "4",
  "path_in_schema": "compliance_config.esxi.ssh_host_based_authentication",
  "title": "ESXi host SSH daemon does not allow host-based authentication.",
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

Get ssh host based auth policy for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of str for ‘hostbasedauthentication’ value and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh host based auth policy for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value for ‘hostbasedauthentication’ config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – Product context instance.
  * **desired_values** (*str*) – Desired value for the ssh host based authentication config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
