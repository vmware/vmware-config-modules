### *class* VimApiSessionTimeout

Bases: `BaseController`

ESXi controller class to get/set/check compliance/remediate VIM API session idle timeout(in minutes).

Config Id - 1116
<br/>
Config Title - The ESXi host must configure a session timeout for the vSphere API.
<br/>

Controller Metadata
```json
{
  "name": "vim_api_session_timeout",
  "configuration_id": "1116",
  "path_in_schema": "compliance_config.esxi.vim_api_session_timeout",
  "title": "The ESXi host must configure a session timeout for the vSphere API",
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

Get VIM API session idle timeout for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESX context instance.
* **Returns:**
  Tuple of an integer for VIM API session idle timeout(in minutes) and a list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set VIM API session idle timeout for esxi host.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*int*) – Desired value of VIM API session idle timeout(in minutes).
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
