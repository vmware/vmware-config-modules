### *class* TaskAndEventRetentionPolicy

Bases: `BaseController`

Manage Task and Event retention policy with get and set methods.

Config Id - 1226
<br/>
Config Title - vCenter task and event retention must be set to a defined number of days.
<br/>

Controller Metadata
```json
{
  "name": "task_and_event_retention",
  "configuration_id": "1226",
  "path_in_schema": "compliance_config.vcenter.task_and_event_retention",
  "title": "vCenter task and event retention must be set to a defined number of days.",
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

Get Task and event retention policy for vCenter.

Sample get output
<br/>
```json
{
  "task_cleanup_enabled": true,
  "task_max_age": 50,
  "event_cleanup_enabled": true,
  "event_max_age": 50
}
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Tuple of dict with task and event retention policy and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set Task and Event retention policy.

Recommended value task and event retention: >=30 days
<br/>
Sample desired state
<br/>
```json
{
  "task_cleanup_enabled": true,
  "task_max_age": 30,
  "event_cleanup_enabled": true,
  "event_max_age": 30
}
```

Note: Increasing the events retention to more than 30 days will result in a significant increase of vCenter
database size and could shut down the vCenter Server.
<br/>
Please ensure that you enlarge the vCenter database accordingly.
<br/>
Applied changes will take effect only after restarting vCenter Server manually.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for the Task and event retention policies.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
