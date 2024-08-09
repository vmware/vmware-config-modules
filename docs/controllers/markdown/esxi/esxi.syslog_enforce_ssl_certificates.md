### *class* SyslogEnforceSslCertificates

Bases: `BaseController`

ESXi controller to get/set/check_compliance/remediate policy for enforcing checking of SSL certificates for syslog.

Config Id - 1115
<br/>
Config Title - The ESXi host must verify certificates for SSL syslog endpoints.
<br/>

Controller Metadata
```json
{
  "name": "syslog_enforce_ssl_certificates",
  "configuration_id": "1115",
  "path_in_schema": "compliance_config.esxi.syslog_enforce_ssl_certificates",
  "title": "The ESXi host must verify certificates for SSL syslog endpoints",
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

Get SSL certificates enforcement policy for syslog for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of boolean value True/False and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set SSL certificates enforcement policy for syslog for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*bool*) – boolean value True/False to enable/disable SSL certs checking.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
