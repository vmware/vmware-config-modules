### *class* VpxUserPasswordExpirationPolicy

Bases: `BaseController`

Manage VPX User password expiration policy with get and set methods.

Config Id - 428
<br/>
Config Title - The vCenter Server must configure the vpxuser auto-password to be changed periodically.
<br/>

Controller Metadata
```json
{
  "name": "vpx_password_expiration_policy",
  "configuration_id": "428",
  "path_in_schema": "compliance_config.vcenter.vpx_password_expiration_policy",
  "title": "The vCenter Server must configure the vpxuser auto-password to be changed periodically.",
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

Get VPX user password expiration policy.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of VPX password expiration policy as int or None if not configured and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set VPX user password expiration policy.

Recommended value: 30 Days
<br/>
Note: By default, vCenter will change the “vpxuser” password automatically every 30 days.
<br/>
Ensure this setting meets site policies. If it does not, configure it to meet password aging policies.
<br/>
It is very important the password aging policy is not shorter than the default interval that is
set to automatically change the “vpxuser” password to preclude the possibility that vCenter might be
locked out of an ESXi host.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*int*) – Desired values for VPX user password expiration policy in days.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
