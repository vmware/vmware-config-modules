### *class* AutoRotateScheduleConfig

Bases: `BaseController`

Class for AutoRotateSchedule config with get and set methods.
| ConfigID - 1609
| ConfigTitle - SDDC Manager must schedule automatic password rotation.

Controller Metadata
```json
{
  "name": "credential_auto_rotate_policy",
  "configuration_id": "1609",
  "path_in_schema": "compliance_config.sddc_manager.credential_auto_rotate_policy",
  "title": "SDDC Manager must schedule automatic password rotation.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "sddc_manager"
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

Get AutoRotateSchedule config of credentials.

* **Parameters:**
  **context** (*SddcManagerContext*) – SddcManagerContext.
* **Returns:**
  Tuple of dict with key “credentials” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set AutoRotateSchedule config for the audit control.

* **Parameters:**
  * **context** (*SddcManagerContext.*) – SddcManagerContext.
  * **desired_values** (*dict*) – Desired values for the AutoRotateSchedule config
* **Returns:**
  Tuple of “status” and list of error messages
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of auto rotate configuration.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and current/desired value( for non_compliant) or errors ( for failure).
* **Return type:**
  tuple

#### remediate(context, desired_values)

Remediate configuration drifts.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and old/new values(for success) or errors (for failure).
* **Return type:**
  dict
