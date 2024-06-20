### *class* DnsConfig

Bases: `BaseController`

Manage DNS config with get and set methods.

Config Id - 1271
<br/>
Config Title - DNS should be configured to a global value that is enforced by vCenter.
<br/>

Controller Metadata
```json
{
  "name": "dns",
  "configuration_id": "1271",
  "path_in_schema": "compliance_config.vcenter.dns",
  "title": "DNS should be configured to a global value that is enforced by vCenter.",
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

Get DNS config from vCenter.

Sample get call output
<br/>
```json
{
  "mode": "is_static",
  "servers": ["8.8.8.8", "1.1.1.1"]
}
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of dict with keys “servers” and “mode” and a list of error messages if any.
* **Return type:**
  tuple

#### set(context, desired_values)

Sets list of servers and DNS mode.

Sample desired state for DNS
<br/>
```json
{
  "mode": "is_static",
  "servers": ["8.8.8.8", "1.1.1.1"]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the DNS config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current DNS configuration in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the DNS config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediate DNS configuration drifts in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Any*) – Desired values for the DNS config.
* **Returns:**
  Dict of status and old/new values(for success) or errors (for failure).
* **Return type:**
  dict
