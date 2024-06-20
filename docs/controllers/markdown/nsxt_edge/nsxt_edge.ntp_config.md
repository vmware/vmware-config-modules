### *class* NtpConfig

Bases: `BaseController`

Manage Ntp config with get and set methods..

Config Id - 1401
<br/>
Config Title - Synchronize system clocks to an authoritative time source.
<br/>

Controller Metadata
```json
{
  "name": "ntp",
  "configuration_id": "1401",
  "path_in_schema": "compliance_config.nsxt_edge.ntp",
  "title": "Configure NTP servers for the NSX-T edge.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "nsxt_edge"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": null,
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": [
    "nsxt_edge"
  ]
}
```

#### get(context)

Get NTP config from NSXT edge.

Sample get output
<br/>
```json
{
  "servers": ["time.vmware.com", "time.google.com"]
}
```

* **Parameters:**
  **context** (*BaseContext*) – BaseContext, since this controller doesn’t require product specific context.
* **Returns:**
  Tuple of Dict containing ntp servers and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set NTP config in NSXT edge.
Also post set, check_compliance is run again to validate that the values are set.

Sample desired state for NTP.
<br/>
```json
{
  "servers": ["time.vmware.com", "time.google.com"]
}
```

* **Parameters:**
  * **context** (*BaseContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired value for the NTP config. Dict with keys “servers”.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
