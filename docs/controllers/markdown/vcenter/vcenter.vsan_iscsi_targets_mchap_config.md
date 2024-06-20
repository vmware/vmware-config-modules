### *class* VsanIscsiTargetsMchapConfig

Bases: `BaseController`

Manage vsan iscsi targets mutual chap authentication configuration for vsan enabled clusters.

Config Id - 1212
<br/>
Config Title - Configure Mutual CHAP for vSAN iSCSI targets.
<br/>

Controller Metadata
```json
{
  "name": "vsan_iscsi_targets_mutual_chap_config",
  "configuration_id": "1212",
  "path_in_schema": "compliance_config.vcenter.vsan_iscsi_targets_mutual_chap_config",
  "title": "Configure Mutual CHAP for vSAN iSCSI targets",
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

Get vSAN iSCSI configurations for all clusters.

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Returns tuple with dict of vSAN iSCSI configurations for each cluster and list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set is not implemented for this control since modifying config would impact existing auth.
Refer to Jira : VCFSC-202 and VCFSC-274

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*String* *or* *list* *of* *strings*) – Desired value for the certificate authority
* **Returns:**
  Dict of status (RemediateStatus.SKIPPED) and errors if any
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of vsan iscsi targets config in vCenter server. If no clusters are enabled for vSAN or
if vSAN is enabled but iSCSI is not enabled, this is not applicable (compliant). If iscsi targets is
enabled, mutual chap should be configured as authentication type.
The desired value is for remediation.

Sample desired_values spec
<br/>
```json
{
    'global': 'CHAP_Mutual',
    'SDDC-Datacenter/SDDC-Cluster1': 'CHAP_Mutual',
    'SDDC-Datacenter/SDDC-Cluster1/target_01': 'CHAP_Mutual'
}
```

* **Parameters:**
  * **context** – Product context instance.
  * **desired_values** – Desired value for the certificate authority.
* **Returns:**
  Dict of status and current/desired value or errors (for failure).
* **Return type:**
  dict
