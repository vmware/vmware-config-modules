### *class* LogonBannerConfig

Bases: `BaseController`

Class for logon banner config with get and set methods.

Config Id - 1209
<br/>
Config Title - Configure a logon message
<br/>

Controller Metadata
```json
{
  "name": "logon_banner_config",
  "configuration_id": "1209",
  "path_in_schema": "compliance_config.vcenter.logon_banner_config",
  "title": "Configure a logon message",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vcenter"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": null,
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": [
    "vcenter"
  ]
}
```

#### get(context)

Function to get logon banner details of vcenter server for audit.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Details of the current logon banner
* **Return type:**
  tuple

#### set(context, desired_values)

Set to replace logon banner with desired config.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** – Desired values for the vcenter logon banner
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of logon banner in vCenter server. Customer desired logon message need to
be provided as shown in the below sample format.

Sample desired_values spec
<br/>
```json
{
    "logon_banner_title":
        "vCenter Server Managed by SDDC Manager",
    "logon_banner_content":
        "This vCenter Server is managed by SDDC Manager (sddc-manager.vrack.vsphere.local).
         Making modifications directly in vCenter Server may break SDDC Manager workflows.
         Please consult the product documentation before making changes through the vSphere Client.",
    "checkbox_enabled": True
}
```

* **Parameters:**
  * **context** – Product context instance.
  * **desired_values** – Desired value for the logon banner.
* **Returns:**
  Dict of status and current/desired value or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Replace logon banner with the one in desired value.

* **Parameters:**
  * **context** – Product context instance.
  * **desired_values** – Desired value for the logon banner.
* **Returns:**
  Dict of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  *Dict*
