### *class* BackupConfig

Bases: `BaseController`

Class for backupSettings config with get and set methods.
| ConfigID - 1600
| ConfigTitle - Verify SDDC Manager backup.

Controller Metadata
```json
{
  "name": "backup",
  "configuration_id": "1600",
  "path_in_schema": "compliance_config.sddc_manager.backup",
  "title": "Verify SDDC Manager backup.",
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

Get Backup config for audit control.

* **Parameters:**
  **context** (*SDDCManagerContext*) – SDDCManagerContext.
* **Returns:**
  Tuple of dict and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set Backup config for the audit control.

* **Parameters:**
  * **context** (*SDDCManagerContext.*) – SDDCManagerContext.
  * **desired_values** (*dict*) – Desired values for the DepotSettings config
* **Returns:**
  Tuple of “status” and list of error messages
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of current backup configuration in SDDC Manager.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for backup config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
