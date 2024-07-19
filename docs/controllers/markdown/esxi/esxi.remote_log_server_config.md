### *class* RemoteLogServerConfig

Bases: `BaseController`

ESXi controller for get/set remote log server configurations.

Config Id - 164
<br/>
Config Title - Configure a remote log server for the ESXi hosts.
<br/>

Controller Metadata
```json
{
  "name": "remote_log_server_config",
  "configuration_id": "164",
  "path_in_schema": "compliance_config.esxi.remote_log_server_config",
  "title": "Configure a remote log server for the ESXi hosts.",
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

Get remote log server configurations for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of a list of remote log server string and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set remote log hosts for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*a list* *of* *log hosts* *(**str**)*) – Desired value of remote log hosts.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
