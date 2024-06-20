### *class* NtpConfig

Bases: `BaseController`

Manage Ntp config with get and set methods.

Config Id - 1246
<br/>
Config Title - The system must configure NTP time synchronization.
<br/>

Controller Metadata
```json
{
  "name": "ntp",
  "configuration_id": "1246",
  "path_in_schema": "compliance_config.vcenter.ntp",
  "title": "The system must configure NTP time synchronization.",
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

Get NTP config from vCenter.

Sample get output
<br/>
```json
{
  "mode": "NTP",
  "servers": ["time.vmware.com", "time.google.com"]
}
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of dict with key “servers”, “mode” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set NTP config in vCenter.

Sample desired state for NTP.
<br/>
```json
{
  "mode": "NTP",
  "servers": ["time.vmware.com", "time.google.com"]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired value for the NTP config. Dict with keys “servers” and “mode”.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current NTP configuration in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for NTP config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediate configuration drifts for NTP config in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for NTP config.
* **Returns:**
  Dict of status and old/new values(for success) or errors (for failure).
* **Return type:**
  dict
