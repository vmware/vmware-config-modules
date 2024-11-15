### *class* DVSNetworkIOControlPolicy

Bases: `BaseController`

Manage DV Switch Network I/O control policy with get and set methods.

Config Id - 409
<br/>
Config Title - The vCenter Server must manage excessive bandwidth and Denial of Service (DoS) attacks by enabling
Network I/O Control (NIOC).
<br/>

Controller Metadata
```json
{
  "name": "dvs_network_io_control",
  "configuration_id": "409",
  "path_in_schema": "compliance_config.vcenter.dvs_network_io_control",
  "title": "The vCenter Server must manage excessive bandwidth and Denial of Service (DoS) attacks by enabling Network I/O Control (NIOC).",
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

Get DVS Network I/O control policy for all DV switches.

Sample get output
<br/>
```json
[
  {
    "switch_name": "SwitchB",
    "network_io_control_status": false
  },
  {
    "switch_name": "SwitchC",
    "network_io_control_status": true
  },
  {
    "switch_name": "SwitchA",
    "network_io_control_status": false
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of list of DV switch network I/O control policy and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set Network I/O control policy for all DV switches.

Sample desired state
<br/>
```json
{
  "__GLOBAL__": {
    "network_io_control_status": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "network_io_control_status": true
    }
  ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for enabling/disabling Network I/O control policy.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of Network I/O control policy for all DV switches.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for network I/O control policy.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Remediate configuration drifts by applying desired values.

Sample desired state for remediation.
<br/>
```json
{
  "__GLOBAL__": {
    "network_io_control_status": false
  },
  "__OVERRIDES__": [
    {
      "switch_name": "Switch-A",
      "network_io_control_status": false
    }
  ]
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for Network I/O control for DV switches.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
