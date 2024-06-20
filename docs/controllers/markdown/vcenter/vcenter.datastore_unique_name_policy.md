### *class* DatastoreUniqueNamePolicy

Bases: `BaseController`

Manage vSAN datastore name uniqueness with get and set methods.

Config Id - 420
<br/>
Config Title - The vCenter Server must configure the vSAN Datastore name to a unique name.
<br/>

Controller Metadata
```json
{
  "name": "vsan_datastore_naming_policy",
  "configuration_id": "420",
  "path_in_schema": "compliance_config.vcenter.vsan_datastore_naming_policy",
  "title": "The vCenter Server must configure the vSAN Datastore name to a unique name.",
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

Get all vSAN datastore info.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of List of dicts with vSAN datastore info and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set will not be implemented until we have a proper remediation workflow is in place with fail safes
and rollback mechanism.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*bool*) – When set to true (the only allowed value), the audit process flags a datastore
    as non-compliant only if its name is ‘vsanDatastore.’ No other names are checked for compliance.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of datastore names among all vSAN-based datastores.

The audit process flags a datastore as non-compliant only if its name is ‘vsanDatastore.’
No other names are checked for compliance.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*bool*) – When set to true (the only allowed value), the audit process flags a datastore as
    non-compliant only if its name is ‘vsanDatastore.’ No other names are checked for compliance.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
