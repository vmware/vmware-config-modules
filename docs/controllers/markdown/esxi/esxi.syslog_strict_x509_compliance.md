### *class* SyslogStrictX509Compliance

Bases: `BaseController`

ESXi controller to get/set/check_compliance/remediate policy for strict x509 verification for SSL syslog endpoints.

Config Id - 1121
<br/>
Config Title - The ESXi host must enable strict x509 verification for SSL syslog endpoints.
<br/>

Controller Metadata
```json
{
  "name": "syslog_strict_x509_compliance",
  "configuration_id": "1121",
  "path_in_schema": "compliance_config.esxi.syslog_strict_x509_compliance",
  "title": "The ESXi host must enable strict x509 verification for SSL syslog endpoints",
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

Get SSL x509 verification policy for syslog for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of boolean value True/False and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set SSL x509 verification policy for syslog for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*bool*) – boolean value True/False to enable/disable SSL x509 verification.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
