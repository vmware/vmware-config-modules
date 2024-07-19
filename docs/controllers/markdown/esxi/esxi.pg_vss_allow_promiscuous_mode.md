### *class* PgVssAllowPromiscuousMode

Bases: `BaseController`

ESXi controller to get/set guest promiscuous mode configuration on vSS portgroup.

Config Id - 162
<br/>
Config Title - All port groups on standard switches must be configured to reject guest promiscuous mode requests.
<br/>

Controller Metadata
```json
{
  "name": "pg_vss_allow_promiscuous_mode",
  "configuration_id": "162",
  "path_in_schema": "compliance_config.esxi.pg_vss_allow_promiscuous_mode",
  "title": "All port groups on standard switches must be configured to reject guest promiscuous mode requests.",
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

Get vSS portgroup guest promiscuous mode configuration for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of a list of all pg vss configs and a list of errors if any.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set vSS portgroup guest promiscuous mode configuration for esxi host.

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
