### *class* AdEsxAdminGroupConfig

Bases: `BaseController`

ESXi controller to get/set Active Directory ESX Admin group membership configuration.

Config Id - 137
<br/>
Config Title - Active Directory ESX Admin group membership must not be used when adding ESXi hosts to Active Directory.
<br/>

Controller Metadata
```json
{
  "name": "ad_esx_admin_group_config",
  "configuration_id": "137",
  "path_in_schema": "compliance_config.esxi.ad_esx_admin_group_config",
  "title": "Active Directory ESX Admin group membership must not be used when adding ESXi hosts to Active Directory.",
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

Get ESX Admin group configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of config string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set ESX Admin group configuration for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*str*) – Desired value of ESX Admin group configuration.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
