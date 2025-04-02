### *class* SNMPv3SecurityPolicy

Bases: `BaseController`

Manage vCenter SNMP v3 security config with get and set methods.

Config Id - 1222
<br/>
Config Title - The vCenter server must enforce SNMPv3 security features where SNMP is required.
<br/>

Controller Metadata
```json
{
  "name": "snmp_v3",
  "configuration_id": "1222",
  "path_in_schema": "compliance_config.vcenter.snmp_v3",
  "title": "The vCenter server must enforce SNMPv3 security features where SNMP is required.",
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
  "functional_test_targets": [
    "vcenter"
  ]
}
```

#### get(context)

Get SNMP v3 security config.

Sample get call output:
<br/>
```json
{
  "enable": true,
  "authentication": "SHA1",  # none, SHA1, SHA256, SHA384, SHA512
  "privacy": "AES128"  # none, AES128, AES192, AES256.
}
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of dict and a list of error messages if any.
* **Return type:**
  tuple

#### set(context, desired_values)

Sets SNMP v3 security config. Enables/disables configuration and sets privacy and authentication protocols.

If SNMP is enabled, recommendation is to configure Authentication as SHA1 and Privacy as AES128;
if SNMP is disabled, consider the system compliant.
<br/>
Sample desired state for SNMP security config
<br/>
```json
{
  "enable": true,
  "authentication": "SHA1",  # none, SHA1, SHA256, SHA384, SHA512
  "privacy": "AES128"  # none, AES128, AES192, AES256.
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the DNS config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of current SNMP_v3 configuration in vCenter.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the SNMP_v3 config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict
