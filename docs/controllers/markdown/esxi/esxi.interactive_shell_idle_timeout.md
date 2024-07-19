### *class* InteractiveShellIdleTimeout

Bases: `BaseController`

ESXi controller class to get/set/check compliance/remediate esxi shell interactive idle timeout(in seconds).

Config Id - 38
<br/>
Config Title - Configure the inactivity timeout to automatically terminate idle shell sessions.
<br/>

Controller Metadata
```json
{
  "name": "interactive_shell_idle_timeout",
  "configuration_id": "38",
  "path_in_schema": "compliance_config.esxi.interactive_shell_idle_timeout",
  "title": "Configure the inactivity timeout to automatically terminate idle shell sessions",
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

Get esxi interactive shell idle timeout for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for esxi interactive shell idle timeout(in seconds) and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set esxi interactive shell idle timeout for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of esxi interactive shell idle timeout(in seconds).
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
