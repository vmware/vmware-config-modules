### *class* VpxSDDCDeployedComplianceKitConfig

Bases: `BaseController`

Manage Compliance kit configuration value for a recognized security control framework or standard
: (e.g., NIST-800-53) with get and set methods.

Config Id - 0000
<br/>
Config Title - Set Compliance kit configuration value for a recognized security control framework or standard.
<br/>

Controller Metadata
```json
{
  "name": "vpx_sddc_deployed_compliance_kit_config",
  "configuration_id": "0000",
  "path_in_schema": "compliance_config.vcenter.vpx_sddc_deployed_compliance_kit_config",
  "title": "Manage Compliance kit configuration value for a recognized security control framework or standard",
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
  "functional_test_targets": []
}
```

#### get(context)

Get Compliance kit configuration value for a recognized security control framework or standard
(e.g., NIST-800-53).

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of SDDC deployed compliance kit configuration value as string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set Compliance kit configuration value for a recognized security control framework or standard
(e.g., NIST-800-53).

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*String*) – Desired values for SDDC compliance kit configuration value.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
