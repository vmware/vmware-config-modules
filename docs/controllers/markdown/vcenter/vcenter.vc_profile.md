### *class* VcProfile

Bases: `BaseController`

Class for managing VC profiles.

Controller Metadata
```json
{
  "name": "vc_profile",
  "configuration_id": "-1",
  "path_in_schema": "",
  "title": "vCenter Profile Configuration",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vcenter"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": "REMEDIATION_SKIPPED",
  "scope": "",
  "type": "CONFIGURATION",
  "functional_test_targets": []
}
```

#### get(context, template=None)

Get the current VC profile configuration.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **template** (*dict*) – Template of requested properties to populate
* **Returns:**
  Tuple of the VC profile config and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set - NOT IMPLEMENTED.

* **Parameters:**
  **context** (*VcenterContext*) – 
* **Return type:**
  *Tuple*[*RemediateStatus*, *List*[str]]

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Any*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and result (for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediate - NOT IMPLEMENTED.

* **Parameters:**
  * **context** (*VcenterContext*) – 
  * **desired_values** (*Dict*) – 
* **Return type:**
  *Dict*
