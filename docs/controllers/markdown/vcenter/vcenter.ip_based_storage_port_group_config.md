### *class* IPBasedStoragePortGroupConfig

Bases: `BaseController`

Class for ip based storage port groups vlan isolation config with get and set methods.

Remediation is not supported as it involves different configurations on vsan, iscsi and NFS. Any drifts should
be analyzed based on compliance report and manually remediated.

Config Id - 1225
<br/>
Config Title - Isolate all IP-based storage traffic on distributed switches from other traffic types.
<br/>

Controller Metadata
```json
{
  "name": "ip_based_storage_port_group_config",
  "configuration_id": "1225",
  "path_in_schema": "compliance_config.vcenter.ip_based_storage_port_group_config",
  "title": "Isolate all IP-based storage traffic on distributed switches from other traffic types",
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

Get ip based storage distributed port groups vlan configurations for the vCenter.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  A tuple containing a dictionary to store ip based storage port groups data and a list of error messages if any.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set method is not implemented as this control requires user intervention to remediate.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired value for ip based storage port groups.
* **Returns:**
  Dict of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of all ip based storage distributed port groups vlan isolation configuration.

Sample desired values
<br/>
```json
{
    "__GLOBAL__": {
        "is_dedicated_vlan": true
    },
    "__OVERRIDES__": [
        {
            "switch_name": "Switch1",
            "port_group_name": "PG2",
            "is_dedicated_vlan": true,
        }
    ]
}
```

Sample check compliance response
<br/>
```json
{
    "status": "NON_COMPLIANT",
    "current": [
        {
            "is_dedicated_vlan": false,
            "switch_name": "Switch1",
            "port_group_name": "PG2"
        },
        {
            "is_dedicated_vlan": false,
            "switch_name": "Switch1",
            "port_group_name": "PG1"
        }
    ],
    "desired": [
        {
            "is_dedicated_vlan": true,
            "switch_name": "Switch1",
            "port_group_name": "PG2"
        },
        {
            "is_dedicated_vlan": true,
            "switch_name": "Switch1",
            "port_group_name": "PG1"
        }
    ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for ip based stotage  port groups.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate is not implemented as this control requires manual intervention.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired value for the ip based storage port groups.
* **Returns:**
  Dict of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  *Dict*
