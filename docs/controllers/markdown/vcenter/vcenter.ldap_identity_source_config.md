### *class* LdapIdentitySourceConfig

Bases: `BaseController`

Class for ldap identity source config with get and set methods.

Config Id - 1230
<br/>
Config Title - The vCenter Server must use a limited privilege account when adding an
LDAP identity source.
<br/>

Controller Metadata
```json
{
  "name": "ldap_identity_source_config",
  "configuration_id": "1230",
  "path_in_schema": "compliance_config.vcenter.ldap_identity_source_config",
  "title": "The vCenter Server must use a limited privilege account when adding an LDAP identity source.",
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
  "functional_test_targets": [
    "vcenter"
  ]
}
```

#### get(context)

Get details of ldap identity source of vcenter server for audit.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Details of the ldap account name
* **Return type:**
  tuple

#### set(context, desired_values)

Set is not implemented as this control since modifying config would impact existing auth.
Refer to Jira : VCFSC-147

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*String* *or* *list* *of* *strings*) – Desired value for the certificate authority
* **Returns:**
  Dict of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  tuple
