### *class* VpxSyslogEnablementPolicy

Bases: `BaseController`

Manage VPX syslog enablement config with get and set methods

Config Id - 1221
<br/>
Config Title - The vCenter Server must be configured to send events to a central log server.
<br/>

Controller Metadata
```json
{
  "name": "vpx_syslog_enablement_policy",
  "configuration_id": "1221",
  "path_in_schema": "compliance_config.vcenter.vpx_syslog_enablement_policy",
  "title": "The vCenter Server must be configured to send events to a central log server.",
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

Get VPX syslog enablement config.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of VPX syslog enablement config as bool and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set VPX syslog enablement config.

Recommended syslog configuration: true | enabled
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Bool*) – Desired values for VPX syslog enablement policy
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
