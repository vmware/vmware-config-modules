### *class* CertConfig

Bases: `BaseController`

Class for cert config with get and set methods.

Config Id - 1205
<br/>
Config Title - The vCenter Server Machine SSL certificate must be issued by an appropriate
<br/>
certificate authority.
<br/>

Controller Metadata
```json
{
  "name": "cert_config",
  "configuration_id": "1205",
  "path_in_schema": "compliance_config.vcenter.cert_config",
  "title": "The vCenter Server Machine SSL certificate must be issued by an appropriate certificate authority",
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

Get certificate details of vcenter server for audit.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Details of the certificate issuer
* **Return type:**
  tuple

#### set(context, desired_values)

Set is not implemented as this control requires manual intervention.

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*String* *or* *list* *of* *strings*) – Desired value for the certificate authority
* **Returns:**
  Tuple of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of configured certificate authority in vCenter server. Certificate issuer details needs
to be provided as shown in the below sample format (can provide multiple certs too).The method will check
if the current certificate details is available in the desired_values and return the compliance
status accordingly.

Sample desired_values spec
<br/>
```json
{
    "certificate_issuer":
        ["OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CB",
        "OU=VMware Engineering,O=vcenter-1.vrack.vsphere.local,ST=California,C=US,DC=local,DC=vsphere,CN=CA"]
}
```

* **Parameters:**
  * **context** – Product context instance.
  * **desired_values** – Desired value for the certificate authority.
* **Returns:**
  Dict of status and current/desired value or errors (for failure).
* **Return type:**
  dict
