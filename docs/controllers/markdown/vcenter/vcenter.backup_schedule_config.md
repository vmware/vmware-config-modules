### *class* BackupScheduleConfig

Bases: `BaseController`

Manage vCenter back schedule config with get and set methods.

Config Id - 1220
<br/>
Config Title - The vCenter Server configuration must be backed up on a regular basis.
<br/>

Controller Metadata
```json
{
  "name": "backup_schedule_config",
  "configuration_id": "1220",
  "path_in_schema": "compliance_config.vcenter.backup_schedule_config",
  "title": "The vCenter Server configuration must be backed up on a regular basis.",
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

Get backup schedule config from vCenter.

sample get call output
<br/>
```json
{
  "backup_schedule_name": "DailyBackup",
  "enable_backup_schedule": true,
  "backup_location_url": "sftp://10.0.0.250:/root/backups",
  "backup_server_username": "root",
  "backup_parts": [
    "seat",
    "common"
  ],
  "recurrence_info": {
    "hour": 1,
    "minute": 0,
    "recurrence_type": "DAILY"
  },
  "retention_info": {
    "max_count": 5
  }
}
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of dict with key “servers” and list of error messages.
* **Return type:**
  tuple

#### set(context, desired_values)

Set Backup schedule config for vCenter.

Sample desired state for Backup schedule config
<br/>
```json
{
  "backup_schedule_name": "DailyBackup",
  "enable_backup_schedule": true,
  "backup_location_url": "sftp://10.0.0.250:/root/backups",
  "backup_server_username": "root",
  "backup_server_password": "HFKMo18wrwBh.k.H",
  "backup_encryption_password": "HFKMo18wrwBh.k.H",
  "backup_parts": [
    "seat",
    "common"
  ],
  "recurrence_info": {
    "recurrence_type": "DAILY",
    "hour": 1,
    "minute": 0
  },
  "retention_info": {
    "max_count": 5
  }
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for the vCenter backup schedule config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of vCenter backup schedules.

Password is not considered during compliance check.
<br/>
Due to security restrictions we cannot get the current password. But it is still used for remediation.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for vCenter backup schedule config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict
