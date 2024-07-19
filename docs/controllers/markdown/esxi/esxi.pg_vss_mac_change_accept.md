### *class* PgVssMacChangeAccept

Bases: `BaseController`

ESXi controller to get/set guest MAC address changes configuration on vSS portgroup.

Config Id - 161
<br/>
Config Title - All port groups on standard switches must be configured to reject guest MAC address changes.
<br/>

Controller Metadata
```json
{
  "name": "pg_vss_mac_change_accept",
  "configuration_id": "161",
  "path_in_schema": "compliance_config.esxi.pg_vss_mac_change_accept",
  "title": "All port groups on standard switches must be configured to reject guest MAC address changes.",
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

Get vSS portgroup MAC change configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of a list of all pg vss configs and a list of errors if any..
* **Return type:**
  Tuple

#### set(context, desired_values)

Set vSS portgroup MAC change configuration for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*boolean*) – boolean of True/False.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*HostContext*) – ESX context instance.
  * **desired_values** (*Any*) – Desired values for rulesets.
* **Returns:**
  Dict of status and list of current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
