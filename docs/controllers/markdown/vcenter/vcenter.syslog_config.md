### *class* SyslogConfig

Bases: `BaseController`

Manage Syslog config with get and set methods.

Config Id - 1218
<br/>
Config Title - The vCenter Server must be configured to send logs to a central log server.
<br/>

Controller Metadata
```json
{
  "name": "syslog",
  "configuration_id": "1218",
  "path_in_schema": "compliance_config.vcenter.syslog",
  "title": "The vCenter Server must be configured to send logs to a central log server.",
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

Get Syslog config from vCenter.

sample get call output
<br/>
```json
{
  "servers": [
    {
      "hostname": "8.8.4.4",
      "port": 90,
      "protocol": "TLS"
    },
    {
      "hostname": "8.8.1.8",
      "port": 90,
      "protocol": "TLS"
    }
  ]
}
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of dict with key “servers” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set Syslog config for the audit control.

Sample desired state for syslog config
<br/>
```json
{
  "servers": [
    {
      "hostname": "10.0.0.250",
      "port": 514,
      "protocol": "TLS"
    },
    {
      "hostname": "10.0.0.251",
      "port": 514,
      "protocol": "TLS"
    }
  ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the Syslog config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of current syslog configuration in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the syslog config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediate syslog configuration drifts in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Any*) – Desired values for the syslog config.
* **Returns:**
  Dict of status and old/new values(for success) or errors (for failure).
* **Return type:**
  dict
