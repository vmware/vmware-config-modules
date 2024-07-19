### *class* ProxyConfig

Bases: `BaseController`

Class for Proxy config with get and set methods.
| ConfigID - 1604
| ConfigTitle - Enable/Disable lcm proxy configuration.

Controller Metadata
```json
{
  "name": "proxy_config",
  "configuration_id": "1604",
  "path_in_schema": "compliance_config.sddc_manager.proxy_config",
  "title": "Enable/Disable lcm proxy configuration",
  "tags": [],
  "version": "1.0.0",
  "since": "",
  "products": [
    "sddc_manager"
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

Get Proxy Configuration from SDDC Manager.

* **Parameters:**
  **context** (*SDDCManagerContext*) – Product context instance.
* **Returns:**
  Tuple of proxy enabled boolean value and a list of errors if any.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set Proxy Configuration in SDDC Manager.

* **Parameters:**
  * **context** (*SDDCManagerContext*) – Product context instance.
  * **desired_values** (*boolean*) – Desired value for the Proxy config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  tuple
