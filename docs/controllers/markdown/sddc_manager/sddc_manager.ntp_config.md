### *class* NtpConfig

Bases: `BaseController`

Operations for Ntp config in SDDC Manager.

Controller Metadata
```json
{
  "name": "ntp",
  "configuration_id": "1601",
  "path_in_schema": "compliance_config.sddc_manager.ntp",
  "title": "SDDC Manager components must use an authoritative time source [NTP]",
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

Get list of NTP Servers from SDDC Manager.

* **Parameters:**
  **context** (*SDDCManagerContext*) – Product context instance.
* **Returns:**
  Tuple of dict with key “servers” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set NTP config in SDDC Manager.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired value for the NTP config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*Any*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
