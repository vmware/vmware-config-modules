### *class* VpxUserPasswordLengthPolicy

Bases: `BaseController`

Manage VPX User host password length policy with get and set methods.

Config Id - 427
<br/>
Config Title - The vCenter Server must configure the vpxuser host password meets length policy.
<br/>

Controller Metadata
```json
{
  "name": "vpx_host_password_length_policy",
  "configuration_id": "427",
  "path_in_schema": "compliance_config.vcenter.vpx_host_password_length_policy",
  "title": "The vCenter Server must configure the vpxuser host password meets length policy.",
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

Get VPX user host password length policy.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of VPX password length policy as int or None if not configured and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set VPX user host password length policy.

Recommended vpx user password length: >=32 characters or Null
<br/>
Note: The vpxuser password default length is 32 characters.
<br/>
Ensure this setting meets site policies; if not, configure to meet password length policies.
<br/>
Longer passwords make brute-force password attacks more difficult.
<br/>
The vpxuser password is added by vCenter, meaning no manual intervention is normally required.
<br/>
The vpxuser password length must never be modified to less than the default length of 32 characters.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for VPX user host password length policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
