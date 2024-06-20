### *class* SSOActiveDirectoryAuthPolicy

Bases: `BaseController`

Manage active directory authentication for VC with get and set methods.

Config Id - 1228
<br/>
Config Title - The vCenter Server must implement Active Directory authentication.
<br/>

Controller Metadata
```json
{
  "name": "active_directory_authentication",
  "configuration_id": "1228",
  "path_in_schema": "compliance_config.vcenter.active_directory_authentication",
  "title": "The vCenter Server must implement Active Directory authentication.",
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

If there is at least one external domain of type = ‘ActiveDirectory’, then we consider the system compliant.
<br/>
* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  A tuple indicating whether one or more external domains of Active Directory (AD) are configured,
  along with a list of associated error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set requires manual intervention, as seamlessly integrating AD with vCenter is not possible and
: often requires a service or appliance restart.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*bool*) – Bool to enforce active directory based authentication in vCenter.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
