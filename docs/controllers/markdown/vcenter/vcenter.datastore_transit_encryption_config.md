### *class* DatastoreTransitEncryptionPolicy

Bases: `BaseController`

Manage data in transit encryption policy for vSAN clusters with get and set method.

Config Id - 0000
<br/>
Config Title - Configure Data in Transit Encryption Keys to be re-issued at regular intervals
for the vSAN Data in Transit encryption enabled clusters.
<br/>

Controller Metadata
```json
{
  "name": "vsan_datastore_transit_encryption_config",
  "configuration_id": "0000",
  "path_in_schema": "compliance_config.vcenter.vsan_datastore_transit_encryption_config",
  "title": "Configure Data in Transit Encryption Keys to be re-issued at regular intervals for the vSAN Data in Transit encryption enabled clusters.",
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

Get transit encryption policy for all encrypted vSAN based clusters.

Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
Support for version 5xxx will be added soon.
<br/>
* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of List of dicts with transit encryption policy and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set transit encryption policy for encryption enabled vSAN clusters.

Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
Support for version 5xxx will be added soon.
<br/>
Sample desired state for transit encryption policy. Rekey interval range lies
between 30 minutes - 10080 (7 days).
<br/>
```json
{
    "rekey_interval": 30,
    "transit_encryption_enabled": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for transit encryption policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check transit encryption policy compliance for encrypted vSAN enabled clusters.

Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
Support for version 5xxx will be added soon.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for transit encryption policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate transit encryption policy drifts on encryption enabled vSAN based clusters.

Note: This control currently operates only on VCF 4411 due to vModl changes between versions 4411 and 5000.
Support for version 5xxx will be added soon.
<br/>
Sample desired state for transit encryption policy. Rekey interval range
lies between 30 minutes - 10080 (7 days).
<br/>
```json
{
    "rekey_interval": 30,
    "transit_encryption_enabled": true
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for transit encryption policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
