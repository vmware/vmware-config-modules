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
  Tuple of list of “users_groups_roles” and list of error messages.
* **Return type:**
  tuple [list, list]

#### set(context, desired_values)

Set UsersGroupsRolesSettings config for audit control.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – SDDCManagerContext.
  * **desired_values** (*list**[**dict**]*) – Desired values of the users, groups and roles
* **Returns:**
  Tuple of remediation status and list of error messages.
* **Return type:**
  tuple[str, list]

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*List*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediation with provided desired values.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*List*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
