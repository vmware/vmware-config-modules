### *class* H5ClientSessionTimeoutConfig

Bases: `BaseController`

Manage vCenter H5 client idle session timeout with get and set methods.

Config Id - 422
<br/>
Config Title - The vCenter Server must terminate management sessions after certain period of inactivity.
<br/>

Controller Metadata
```json
{
  "name": "h5_client_session_timeout",
  "configuration_id": "422",
  "path_in_schema": "compliance_config.vcenter.h5_client_session_timeout",
  "title": "The vCenter Server must terminate management sessions after certain period of inactivity.",
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
  "functional_test_targets": [
    "vcenter"
  ]
}
```

#### get(context)

Get H5 client session timeout from vCenter.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of session timeout value as int and a list of error messages if any.
* **Return type:**
  tuple

#### set(context, desired_values)

Sets H5 client session timeout on vCenter.

STIG Recommended value: 10 Minutes; default: 120 minutes.
<br/>
Note: For session timeout setting to take effect a restart of the vsphere-ui service is required.
Please note that service restart is not included as part of this remediation procedure.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired value in minutes for the H5 client session timeout.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
