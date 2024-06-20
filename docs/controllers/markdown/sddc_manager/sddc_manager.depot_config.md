### *class* DepotConfig

Bases: `BaseController`

Class for Depot config with get and set methods.
| ConfigID - 1607
| ConfigTitle - Dedicate an account for downloading updates and patches in SDDC Manager.

Controller Metadata
```json
{
  "name": "depot_config",
  "configuration_id": "1607",
  "path_in_schema": "compliance_config.sddc_manager.depot_config",
  "title": "Dedicate an account for downloading updates and patches in SDDC Manager.",
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

Get Depot Configuration from SDDC Manager.
Validation is not done to check if dedicated account is passed. Upto the customer to pass the dedicated account.

* **Parameters:**
  **context** (*SDDCManagerContext*) – Product context instance.
* **Returns:**
  Tuple of dict with key “vmware_account” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set Depot Configuration in SDDC Manager.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired value for the Depot config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple
