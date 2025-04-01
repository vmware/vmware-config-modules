### *class* ClusterConfig

Bases: `BaseController`

Class for managing desired config of an ESX cluster.

Controller Metadata
```json
{
  "name": "cluster_config",
  "configuration_id": "-1",
  "path_in_schema": "",
  "title": "ESX cluster configuration",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "esxi"
  ],
  "components": [],
  "status": "ENABLED",
  "impact": "REMEDIATION_SKIPPED",
  "scope": "",
  "type": "CONFIGURATION",
  "functional_test_targets": []
}
```

#### get(context, template=None)

Get - NOT IMPLEMENTED.

* **Parameters:**
  * **context** (*EsxiContext*) – Product context instance.
  * **template** (*dict*) – Template of requested properties to populate
* **Returns:**
  Tuple of the ESXi Cluster config and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set - NOT IMPLEMENTED.

* **Parameters:**
  **context** (*EsxiContext*) – 
* **Return type:**
  *Tuple*[*RemediateStatus*, *List*[str]]

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

* **Parameters:**
  * **context** (*EsxiContext*) – Product context instance.
  * **desired_values** (*str*) – The cluster moid to target
* **Returns:**
  Dict of status and result (for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediate - NOT IMPLEMENTED.

* **Parameters:**
  * **context** (*EsxiContext*) – 
  * **desired_values** (*Dict*) – 
* **Return type:**
  *Dict*
