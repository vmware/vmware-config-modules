### *class* HostClientSessionIdleTimeout

Bases: `BaseController`

ESXi controller class to get/set/check compliance/remediate host client session idle timeout(in seconds).

Config Id - 564
<br/>
Config Title - ESXi host must configure host client session timeout.
<br/>

Controller Metadata
```json
{
  "name": "host_client_session_idle_timeout",
  "configuration_id": "564",
  "path_in_schema": "compliance_config.esxi.host_client_session_idle_timeout",
  "title": "ESXi host must configure host client session timeout",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "esxi"
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

Get host client session idle timeout for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for host client session idle timeout(in seconds) and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set host client session timeout for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of host client session idle timeout(in seconds).
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
