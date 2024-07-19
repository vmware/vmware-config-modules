### *class* RHttpProxyFips140_2CryptConfig

Bases: `BaseController`

ESXi controller to get/config ssh fips 140-2 validated cryptographic modules.

Config Id - 1117
<br/>
Config Title - The ESXi host rhttpproxy daemon must use FIPS 140-2 validated cryptographic modules to protect the confidentiality of remote access sessions
<br/>

Controller Metadata
```json
{
  "name": "rhttpproxy_fips_140_2_crypt_config",
  "configuration_id": "1117",
  "path_in_schema": "compliance_config.esxi.rhttpproxy_fips_140_2_crypt_config",
  "title": "The ESXi host rhttpproxy daemon must use FIPS 140-2 validated cryptographic modules to protect the confidentiality of remote access sessions",
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

Get rhttpproxy daemon FIPS 140-2 validated cryptographic modules config for esxi host.

* **Parameters:**
  **context** (*HostContext*) – ESXi context instance.
* **Returns:**
  Tuple of boolean value True/False and a list of errors.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set rhttpproxy daemon FIPS 140-2 validated cryptographic modules config for esxi host based on desired value.

* **Parameters:**
  * **context** (*HostContext*) – Esxi context instance.
  * **desired_values** (*dict*) – boolean value True/False to update config.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple
