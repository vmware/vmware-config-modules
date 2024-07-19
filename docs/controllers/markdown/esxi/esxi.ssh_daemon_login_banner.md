### *class* SshDaemonLoginBanner

Bases: `BaseController`

ESXi controller for SSH daemon login (after) banner.

Config Id - 124
<br/>
Config Title - The ESXi host SSH daemon must be configured with an approved login banner.
<br/>

Controller Metadata
```json
{
  "name": "ssh_daemon_login_banner",
  "configuration_id": "124",
  "path_in_schema": "compliance_config.esxi.ssh_daemon_login_banner",
  "title": "The ESXi host SSH daemon must be configured with an approved login banner.",
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

Get ssh daemon login banner (display after logged in) for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of ssh daemon login banner string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ssh daemon login banner (display after logged in) for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value of ssh daemon login banner.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
