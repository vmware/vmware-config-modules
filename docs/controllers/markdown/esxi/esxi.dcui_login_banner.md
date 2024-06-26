### *class* DcuiLoginBanner

Bases: `BaseController`

ESXi controller for DCUI login banner.

Config Id - 122
<br/>
Config Title - Configure the login banner for the DCUI of the ESXi host.
<br/>

Controller Metadata
```json
{
  "name": "dcui_login_banner",
  "configuration_id": "122",
  "path_in_schema": "compliance_config.esxi.dcui_login_banner",
  "title": "Configure the login banner for the DCUI of the ESXi host",
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

Get dcui login banner for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of dcui login banner string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set dcui login banner for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value of dcui login banner.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
