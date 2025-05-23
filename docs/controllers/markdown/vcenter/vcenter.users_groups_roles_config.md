### *class* UsersGroupsRolesConfig

Bases: `BaseController`

Class for UsersGroupsRolesSettings config with get and set methods.
| ConfigId - 415
| ConfigTitle - The vCenter Server users must have the correct roles assigned.

Controller Metadata
```json
{
  "name": "users_groups_roles",
  "configuration_id": "415",
  "path_in_schema": "compliance_config.vcenter.users_groups_roles",
  "title": "The vCenter Server users must have the correct roles assigned.",
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

Get roles for users and groups.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of dictionary (with keys-‘role’, ‘name’, ‘type’, and ‘propagate’) objects and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set method to remediate drifts found in users, roles and permissions.

* **Parameters:**
  * **context** (*VcenterContext*) – 
  * **desired_values** (*Dict*) – 
* **Return type:**
  *Tuple*

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*list*) – Desired list of users,groups,roles on vCenter.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate configuration drifts by applying desired values.

Sample desired state
<br/>
```json
{
  "global": [
    {
      "name": "VSPHERE.LOCAL\SyncUsers",
      "type": "GROUP",
      "role": "SyncUsers",
      "propagate": True
    },
    {
      "name": "VSPHERE.LOCAL\Administrator",
      "type": "USER",
      "role": "Admin",
      "propagate": True
    }
  ],
  "vcenter": [
    {
      "name": "VSPHERE.LOCAL\Administrator",
      "type": "USER",
      "role": "Admin",
      "propagate": True
    },
    {
      "name": "VSPHERE.LOCAL\Administrators",
      "type": "USER",
      "role": "Admin",
      "propagate": False
    }
  ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for VM migrate encryption policy
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
