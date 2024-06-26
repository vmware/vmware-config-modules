### *class* AlarmSSOConfig

Bases: `BaseController`

Manage SSO account actions alarm config with get and set methods.

Config Id - 1219
<br/>
Config Title - Configure an alert to the appropriate personnel about SSO account actions.
<br/>

Remediation is supported only for creation of alarm. Any update/delete in an alarm is not supported.

Controller Metadata
```json
{
  "name": "alarm_sso_account_actions",
  "configuration_id": "1219",
  "path_in_schema": "compliance_config.vcenter.alarm_sso_account_actions",
  "title": "Configure an alert to the appropriate personnel about SSO account actions.",
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

Get alarms for SSO account actions on vCenter.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of alarm info and a list of error messages if any.
* **Return type:**
  tuple

#### set(context, desired_values)

Set alarms for SSO account actions on vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*list**[**dict**]*) – List of dict objects with alarm info for the sso account actions alarm configuration.
* **Returns:**
  Tuple of remediation status and a list of error messages if any.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*VcenterContext*) – Vcenter context instance.
  * **desired_values** (*list**[**dict**]*) – List of dict objects with alarm info for the sso account actions alarm configuration.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
