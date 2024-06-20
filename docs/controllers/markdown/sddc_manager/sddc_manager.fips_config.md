### *class* FipsConfig

Bases: `BaseController`

Class for Fips config with get method.

Controller Metadata
```json
{
  "name": "fips_mode_enabled",
  "configuration_id": "1608",
  "path_in_schema": "compliance_config.sddc_manager.fips_mode_enabled",
  "title": "SDDC Manager must be deployed with FIPS mode enabled",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "sddc_manager"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": "REMEDIATION_SKIPPED",
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### get(context)

Get FIPS mode status.

* **Parameters:**
  **context** (*SDDCManagerContext*) – SDDCManagerContext.
* **Returns:**
  Tuple of fips mode status (as a boolean data type) and list of error messages
* **Return type:**
  tuple

#### set(context, desired_values)

Set will not be implemented as in current VCF versions we can’t change FIPS mode post bringup.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – SDDCManagerContext.
  * **desired_values** (*boolean*) – True
* **Returns:**
  Tuple of status and list of error messages
* **Return type:**
  tuple
