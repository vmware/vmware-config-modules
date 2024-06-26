### *class* DnsConfig

Bases: `BaseController`

Manage DNS config with get and set methods.

Config Id - 0000
<br/>
Config Title - Placeholder title for vRealize Suite LCM DNS control
<br/>

Controller Metadata
```json
{
  "name": "dns",
  "configuration_id": "0",
  "path_in_schema": "compliance_config.vrslcm.dns",
  "title": "Placeholder title for vRealize Suite LCM DNS control",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vrslcm"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": null,
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### http_headers *= None*

#### get(context)

Get DNS config from VrsLcm.

Sample get output
<br/>
```json
{
  "servers": ["8.8.8.8", "4.4.4.4"]
}
```

* **Parameters:**
  **context** (*VrslcmContext*) – vRealize suite LCM context
* **Returns:**
  Tuple of Dict containing dns servers and a list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*VrslcmContext*) – vRealize suite LCM product context instance.
  * **desired_values** (*Any*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### set(context, desired_values)

Set DNS config in vRealize suite LCM.
This will delete any existing DNS entries and create the new desired ones as each DNS entry requires a unique name associated with it.

Sample desired state for DNS.
<br/>
```json
{
  "servers": ["8.8.8.8", "4.4.4.4"]
}
```

* **Parameters:**
  * **context** (*VrslcmContext*) – vRealize suite LCM context instance.
  * **desired_values** (*dict*) – Desired value for the DNS config. Dict with keys “servers”.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### remediate(context, desired_values)

Remediate current DNS configuration drifts.

* **Parameters:**
  * **context** (*VrslcmContext*) – vRealize suite LCM context instance.
  * **desired_values** (*Any*) – Desired values for DNS control.
* **Returns:**
  Dict of status and old/new values(for success) or errors (for failure).
* **Return type:**
  dict
