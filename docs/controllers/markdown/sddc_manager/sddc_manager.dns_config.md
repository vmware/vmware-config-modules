### *class* DnsConfig

Bases: `BaseController`

Operations for Dns config in SDDC Manager.

Controller Metadata
```json
{
  "name": "dns",
  "configuration_id": "1612",
  "path_in_schema": "compliance_config.sddc_manager.dns",
  "title": "DNS should be configured to a global value that is enforced by SDDC Manager",
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

Get DNS config from SDDC Manager.

* **Parameters:**
  **context** (*SDDCManagerContext*) – Product context instance.
* **Returns:**
  Tuple of dict with key “servers” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set DNS config in SDDC Manager.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the DNS config.
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
