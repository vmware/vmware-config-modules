### *class* SshLoginBanner

Bases: `BaseController`

ESXi controller for SSH login banner.

Config Id - 123
<br/>
Config Title - Configure the login banner for the SSH connections.
<br/>

Controller Metadata
```json
{
  "name": "ssh_login_banner",
  "configuration_id": "123",
  "path_in_schema": "compliance_config.esxi.ssh_login_banner",
  "title": "Configure the login banner for the SSH connections",
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

Get ssh login banner for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of ssh login banner string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh login banner for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value of ssh login banner.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
