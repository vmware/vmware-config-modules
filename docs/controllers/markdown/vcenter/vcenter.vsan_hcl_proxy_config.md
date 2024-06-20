### *class* VSANHCLProxyConfig

Bases: `BaseController`

Manage vSAN proxy configuration for vSAN enabled clusters.

Config Id - 418
<br/>
Config Title - Configure a proxy for the download of the public Hardware Compatibility List.
<br/>

Controller Metadata
```json
{
  "name": "vsan_proxy",
  "configuration_id": "418",
  "path_in_schema": "compliance_config.vcenter.vsan_proxy",
  "title": "Configure a proxy for the download of the public Hardware Compatibility List.",
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

Get vSAN proxy configuration for all cluster.

Sample get call output
<br/>
```json
[
  {
    "host": "time.vmware.com",
    "port": 100,
    "user": "proxy_user_1",
    "internet_access_enabled": false,
    "cluster_name": "sfo-m01-cl01"
  },
  {
    "host": "abc.vmware.com",
    "port": 50,
    "user": "proxy_user_2",
    "internet_access_enabled": true,
    "cluster_name": "sfo-m01-cl02"
  },
  {
    "host": "time.vmware.com",
    "port": 60,
    "user": "proxy_user_3",
    "internet_access_enabled": false,
    "cluster_name": "sfo-m01-cl03"
  }
]
```

* **Parameters:**
  **context** (*VcenterContext*) – Product context instance.
* **Returns:**
  Returns tuple with dict of vSAN proxy configurations for each cluster and list of error messages.
* **Return type:**
  Tuple

#### set(context, desired_values)

Set vSAN proxy configuration for each cluster.

Sample desired state for proxy config.
<br/>
```json
{
    "internet_access_enabled": true,
    "host": "hcl.vmware.com",
    "port": 80,
    "user": "proxy_user",
    "password": "super_complex_string"
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*dict*) – Desired values for vSAN cluster proxy configuration.
* **Returns:**
  Tuple of “status” and list of error messages.
* **Return type:**
  Tuple

#### check_compliance(context, desired_values)

Check compliance of vSAN proxy configuration for all clusters.

Password is not considered during compliance check.
<br/>
Password gets masked as (not shown) when we do a get call so we are ignoring this property from compliance
check.But it is still used for remediation.
<br/>
* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for vSAN proxy config.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  Dict

#### remediate(context, desired_values)

Function to remediate configuration drifts.

Sample desired state for proxy config.
<br/>
```json
{
    "internet_access_enabled": true,
    "host": "hcl.vmware.com",
    "port": 80,
    "user": "proxy_user",
    "password": "super_complex_string"
}
```

* **Parameters:**
  * **context** (*VcenterContext*) – Product context instance.
  * **desired_values** (*Dict*) – Desired values for vSAN proxy config.
* **Returns:**
  Dict of status and old/new values(for success) or errors (for failure).
* **Return type:**
  Dict
