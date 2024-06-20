### *class* TlsVersion

Bases: `BaseController`

ESXi controller class to get/set/check compliance/remediate tls protocols on esxi hosts.

Config Id - 1107
<br/>
Config Title - The ESXi host must exclusively enable TLS 1.2 for all endpoints.
<br/>

Controller Metadata
```json
{
  "name": "tls_version",
  "configuration_id": "1107",
  "path_in_schema": "compliance_config.esxi.tls_version",
  "title": "The ESXi host must exclusively enable TLS 1.2 for all endpoints",
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

Get tls protocols enabled for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of list of enabled tls/ssl protocols and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set tls protocols enabled for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*list*) – Desired value of tls/ssl protocols to be enabled.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
