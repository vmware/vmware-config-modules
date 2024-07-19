### *class* ImageProfileAcceptanceLevel

Bases: `BaseController`

ESXi controller to get/config host image profile acceptance level..

Config Id - 157
<br/>
Config Title - The ESXi Image Profile and vSphere Installation Bundle (VIB) Acceptance Levels must be verified.
<br/>

Controller Metadata
```json
{
  "name": "image_profile_acceptance_level",
  "configuration_id": "157",
  "path_in_schema": "compliance_config.esxi.image_profile_acceptance_level",
  "title": "The ESXi Image Profile and vSphere Installation Bundle (VIB) Acceptance Levels must be verified",
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

Get image profile acceptance level for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict such as {“acceptance_level”: “partner”} and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set image profile acceptance level for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of {“acceptance_level”: “partner”} to update acceptance level.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
