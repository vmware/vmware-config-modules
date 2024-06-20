### *class* UsersGroupsRolesConfig

Bases: `BaseController`

Class for UsersGroupsRolesSettings config with get and set methods.
| ConfigId - 1605
| ConfigTitle - Assign least privileges to users and service accounts in SDDC Manager.

Controller Metadata
```json
{
  "name": "users_groups_roles",
  "configuration_id": "1605",
  "path_in_schema": "compliance_config.sddc_manager.users_groups_roles",
  "title": "Assign least privileges to users and service accounts in SDDC Manager.",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "sddc_manager"
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

Get UsersGroupsRolesSettings config for audit control.

* **Parameters:**
  **context** (*SDDCManagerContext*) – SDDCManagerContext.
* **Returns:**
  Tuple of dict with key “users_groups_roles_info” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set method is not implemented as this control requires user intervention to remediate.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – 
  * **desired_values** (*Dict*) – 
* **Return type:**
  *Tuple*
