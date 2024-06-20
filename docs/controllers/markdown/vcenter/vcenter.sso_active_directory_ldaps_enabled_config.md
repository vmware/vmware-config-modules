### *class* SSOActiveDirectoryLdapsEnabledPolicy

Bases: `BaseController`

Manage active directory LDAPS enabled config for VC with get and set methods.

Config Id - 1229
<br/>
Config Title - The vCenter Server must use LDAPS when adding an SSO identity source.
<br/>

Controller Metadata
```json
{
  "name": "active_directory_ldaps_enabled",
  "configuration_id": "1229",
  "path_in_schema": "compliance_config.vcenter.active_directory_ldaps_enabled",
  "title": "The vCenter Server must use LDAPS when adding an SSO identity source.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vcenter"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": "REMEDIATION_SKIPPED",
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### get(context)

Get active directory authentication config for VC.

If any external domain is of type ‘ActiveDirectory’ and doesn’t use LDAPS, then the system is deemed
non-compliant.
<br/>
* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  A tuple indicating that at least one Active Directory (AD) external domain is configured without LDAPS,
  along with a list of associated error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set requires manual intervention, as seamlessly integrating AD with vCenter is not possible and
: often requires a service or appliance restart.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Dict containing use_ldaps bool to enforce active directory based authentication in
    vCenter.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of Active directories configurations in VC, if AD is configured but it does not use LDAPS
: protocol then flag it as non-compliant.

The audit process flags an Active Directory source as non-compliant if it does not use LDAPS protocol.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Dict containing use_ldaps bool to enforce active directory based authentication in
    vCenter. When set to true (the only allowed value), the audit process flags an Active directory as
    non-compliant if it does not use LDAPS protocol.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
