### *class* TlsVersion

Bases: `BaseController`

Class to implement get and set methods for configuring and enabling specified TLS versions.
For vcenter versions 8.0.2 and above, control is not applicable.

Config Id - 1204
<br/>
Config Title - The vCenter Server must enable TLS 1.2 exclusively.
<br/>

Controller Metadata
```json
{
  "name": "tls_version",
  "configuration_id": "1204",
  "path_in_schema": "compliance_config.vcenter.tls_version",
  "title": "The vCenter Server must enable TLS 1.2 exclusively.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vcenter"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": "RESTART_REQUIRED",
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": [
    "vcenter"
  ]
}
```

#### get(context)

Get TLS versions for the services on vCenter.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  A tuple containing a dictionary where keys are service names and values are list of TLS versions and
  a list of error messages if any.
* **Return type:**
  Tuple

#### set(context, desired_values)

It is a high-risk remediation as it requires restart of services/vCenter.
Post updating the TLS versions, services are restarted as part of the implementation.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values with keys as services and values as TLS versions.
* **Returns:**
  Dict of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the TLS versions on vCenter(and services).
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
