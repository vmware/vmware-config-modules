### *class* SSOBashShellAuthorizedMembersConfig

Bases: `BaseController`

Manage authorized members in the SystemConfiguration.BashShellAdministrators group with get and set methods.

Config Id - 1216
<br/>
Config Title - vCenter must limit membership to the SystemConfiguration.BashShellAdministrators SSO group.
<br/>

Controller Metadata
```json
{
  "name": "sso_bash_shell_authorized_members",
  "configuration_id": "1216",
  "path_in_schema": "compliance_config.vcenter.sso_bash_shell_authorized_members",
  "title": "vCenter must limit membership to the SystemConfiguration.BashShellAdministrators SSO group.",
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

Get authorized members in the SystemConfiguration.BashShellAdministrators group.

We limit our traversal to the first level of groups because a group can have subgroups, which in turn can
contain groups with users. This approach is consistent with the behavior of the dir-cli command:
<br/>
```shell
/usr/lib/vmware-vmafd/bin/dir-cli group list --name <group_name>
```

Sample get output
<br/>
```json
[
  {
    "name": "user-1",
    "domain": "vmware.com",
    "member_type": "USER"
  },
  {
    "name": "user-2",
    "domain": "vmware.com",
    "member_type": "USER"
  },
  {
    "name": "devops",
    "domain": "vsphere.local",
    "member_type": "GROUP"
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of List of dictionaries containing user and groups belonging to the BashShellAdministrators
  group and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Remediation has not been implemented for this control. It’s possible that a customer may legitimately add
: a new user and forget to update the control accordingly. Remediating the control could lead to the removal
  of these users, with potential unknown implications.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*List*) – List of objects containing users and groups details with name, domain and member_type.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of authorized members.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for authorized members.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
