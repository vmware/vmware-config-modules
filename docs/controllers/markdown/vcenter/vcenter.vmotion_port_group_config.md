### *class* VMotionPortGroupConfig

Bases: `BaseController`

Class for vmotion port groups vlan isolation config with get and set methods.

Remediation is not supported as it involves addition/deletion of ports in the port group along with VLAN changes,
it could have unwanted impact. Any drifts should be analyzed based on compliance report and manually remediated.

Config Id - 0000
<br/>
Config Title - All vMotion traffic on distributed switches must be isolated from other traffic types.
<br/>

Controller Metadata
```json
{
  "name": "dvpg_vmotion_traffic_isolation",
  "configuration_id": "0000",
  "path_in_schema": "compliance_config.vcenter.dvpg_vmotion_traffic_isolation",
  "title": "All vMotion traffic on distributed switches must be isolated from other traffic types.",
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

Get vmotion distributed port groups vlan configurations for the vCenter.

Sample get output
<br/>
```json
[
  {
    "switch_name": "Switch1",
    "port_group_name": "PG1",
    "is_dedicated_vlan": true,
    "ports": [
      {
        "host_name": "esxi-3.vrack.vsphere.local",
        "device": "vmk5",
        "tcp_ip_stack": "vmotion"
      },
      {
        "host_name": "esxi-4.vrack.vsphere.local",
        "device": "vmk3",
        "tcp_ip_stack": "vmotion"
      }
    ],
      "vlan_info": {
        "vlan_type": "VLAN",
        "vlan_id": 130
      }
  },
  {
    "switch_name": "Switch1",
    "port_group_name": "PG2",
    "is_dedicated_vlan": false,
    "ports": [
      {
        "host_name": "esxi-3.vrack.vsphere.local",
         "device": "vmk1",
         "tcp_ip_stack": "defaultTcpipStack"
      }
    ],
      "vlan_info": {
        "vlan_type": "VLAN",
        "vlan_id": 170
      }
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  A tuple containing a dictionary to store vmotion port groups data and a list of error messages if any.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set method is not implemented as this control requires user intervention to remediate.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired value for vmotion port groups.
* **Returns:**
  Dict of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of all vmotion distributed port groups vlan isolation configuration.

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
            "vlan_info": {
                "vlan_id": 131,
                "vlan_type": "VLAN"
            }
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
            "vlan_info": {
                "vlan_type": "VLAN",
                "vlan_id": 130
            },
            "switch_name": "Switch1",
            "port_group_name": "PG2"
        },
        {
            "is_dedicated_vlan": false,
            "ports": [
                {
                    "host_name": "esxi-4.vrack.vsphere.local",
                    "device": "vmk4",
                    "tcp_ip_stack": "defaultTcpipStack"
                },
                {
                    "host_name": "esxi-5.vrack.vsphere.local",
                    "device": "vmk4",
                    "tcp_ip_stack": "defaultTcpipStack"
                },
                {
                    "host_name": "esxi-5.vrack.vsphere.local",
                    "device": "vmk5",
                    "tcp_ip_stack": "defaultTcpipStack"
                }
            ],
            "switch_name": "Switch1",
            "port_group_name": "PG1"
        }
    ],
    "desired": [
        {
            "is_dedicated_vlan": true,
            "vlan_info": {
                "vlan_id": 131,
                "vlan_type": "VLAN"
            },
            "switch_name": "Switch1",
            "port_group_name": "PG2"
        },
        {
            "is_dedicated_vlan": true,
            "ports": [
                {
                    "host_name": "esxi-4.vrack.vsphere.local",
                    "device": "vmk4",
                    "tcp_ip_stack": "vmotion"
                },
                {
                    "host_name": "esxi-5.vrack.vsphere.local",
                    "device": "vmk4",
                    "tcp_ip_stack": "vmotion"
                },
                {
                    "host_name": "esxi-5.vrack.vsphere.local",
                    "device": "vmk5",
                    "tcp_ip_stack": "vmotion"
                }
            ],
            "switch_name": "Switch1",
            "port_group_name": "PG1"
        }
    ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for vmotion port groups.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
