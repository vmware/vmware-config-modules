### *class* NtpServiceStartupPolicy

Bases: `BaseController`

ESXi controller to get/update ntp startup policy.

Config Id - 148
<br/>
Config Title - The ESXi host must configure NTP Service startup policy.
<br/>

Controller Metadata
```json
{
  "name": "ntp_service_startup_policy",
  "configuration_id": "148",
  "path_in_schema": "compliance_config.esxi.ntp_service_startup_policy",
  "title": "The ESXi host must configure NTP Service startup policy.",
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

Get ntp service startup policy status for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of dict ({“startup_policy”: “on”}) and list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Update ntp startup policy for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – dict of { “service_policy”: “off”} to update policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
