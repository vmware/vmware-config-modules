### *class* VmMigrateEncryptionPolicy

Bases: `BaseController`

Manage VM migrate Encryption policy with get and set methods.

Config Id - 1234
<br/>
Config Title - Encryption must be enabled for vMotion on the virtual machine.
<br/>

Controller Metadata
```json
{
  "name": "vm_migrate_encryption",
  "configuration_id": "1234",
  "path_in_schema": "compliance_config.vcenter.vm_migrate_encryption",
  "title": "Encryption must be enabled for vMotion on the virtual machine.",
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

Get VM migrate Encryption policy for all Virtual Machines.

Sample Get call output
<br/>
```json
[
  {
    "vm_name": "nsx-mgmt-1",
    "path": "SDDC-Datacenter/vm",
    "migrate_encryption_policy": "opportunistic"
  },
  {
    "vm_name": "sddc-manager",
    "path": "SDDC-Datacenter/vm/Management VMs",
    "migrate_encryption_policy": "opportunistic"
  },
  {
    "vm_name": "ms-sql-replica-1",
    "path": "SDDC-Datacenter/vm/database_workloads/ms-sql",
    "migrate_encryption_policy": "disabled"
  },
  {
    "vm_name": "ms-sql-replica-2",
    "path": "SDDC-Datacenter/vm/database_workloads/ms-sql",
    "migrate_encryption_policy": "required"
  },
  {
    "vm_name": "ubuntu-dev-box",
    "path": "SDDC-Datacenter/vm/dev",
    "migrate_encryption_policy": "opportunistic"
  },
  {
    "vm_name": "vcenter-1",
    "path": "SDDC-Datacenter/vm/Management VMs",
    "migrate_encryption_policy": "opportunistic"
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of dicts with migrate encryption policies for VMs and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set VM migrate Encryption policies for all Virtual machines.

Recommended value for migrate encryption: “opportunistic” | “required”
<br/>
Supported values: [“disabled”, “opportunistic”, “required”].
<br/>
Disabled: Do not use encrypted vMotion, even if available.
<br/>
Opportunistic: Use encrypted vMotion if source and destination hosts support it,
fall back to unencrypted vMotion otherwise. This is the default option.
<br/>
Required: Allow only encrypted vMotion. If the source or destination host does not support vMotion encryption,
do not allow the vMotion to occur.
<br/>
Sample desired state
<br/>
```json
{
  "__GLOBAL__": {
    "migrate_encryption_policy": "opportunistic"
  },
  "__OVERRIDES__": [
    {
      "vm_name": "sddc-manager",
      "path": "SDDC-Datacenter/vm/Management VMs",
      "migrate_encryption_policy": "required"
    },
    {
      "vm_name": "nsx-mgmt-1",
      "path": "SDDC-Datacenter/vm/Networking VMs",
      "migrate_encryption_policy": "required"
    }
  ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for VM migration Encryption policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of VM migrate Encryption policies for all Virtual Machines.

Support Values: [“disabled”, “opportunistic”, “required”]
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for VM migrate Encryption policy.
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
  "__GLOBAL__": {
    "migrate_encryption_policy": "opportunistic"
  },
  "__OVERRIDES__": [
    {
      "vm_name": "sddc-manager",
      "path": "SDDC-Datacenter/vm/Management VMs",
      "migrate_encryption_policy": "required"
    },
    {
      "vm_name": "nsx-mgmt-1",
      "path": "SDDC-Datacenter/vm/Networking VMs",
      "migrate_encryption_policy": "required"
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
