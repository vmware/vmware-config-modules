### *class* AlarmRemoteSyslogFailureConfig

Bases: `BaseController`

Manage esxi remote syslog failure alarm config with get and set methods.

Config Id - 0000
<br/>
Config Title - Configure an alarm to alert on ESXi remote syslog connection.
<br/>

Remediation is supported only for creation of alarm. Any update/delete in an alarm is not supported.

Controller Metadata
```json
{
  "name": "alarm_esx_remote_syslog_failure",
  "configuration_id": "0000",
  "path_in_schema": "compliance_config.vcenter.alarm_esx_remote_syslog_failure",
  "title": "Configure an alert if an error occurs with the ESXi remote syslog connection.",
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

Get alarms for alarm_esx_remote_syslog_failure event type on vCenter.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of alarm info and a list of error messages if any.
* **Return type:**
  tuple

#### set(context, desired_values)

Set alarms for alarm_esx_remote_syslog_failure event type on vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*list**[**dict**]*) – List of dict objects with alarm info for the esx syslog failure alarm configuration.
* **Returns:**
  Tuple of remediation status and a list of error messages if any.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*VcenterContext*) – Vcenter context instance.
  * **desired_values** (*list**[**dict**]*) – List of dict objects with info for the esx remote syslog failure alarm configuration.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
