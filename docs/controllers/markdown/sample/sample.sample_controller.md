### *class* SampleController

Bases: `BaseController`

A one line summary of the controller.

After a blank line, any more details about the controller can be given.

Controller Metadata
```json
{
  "name": "sample_controller_name",
  "configuration_id": "-1",
  "path_in_schema": "compliance_config.sample_product.sample_controller_name",
  "title": "sample config title defined in compliance kit",
  "tags": [
    "sample",
    "test"
  ],
  "version": "1.0.0",
  "since": "",
  "products": [
    "vcenter"
  ],
  "components": [],
  "status": "DISABLED",
  "impact": null,
  "scope": "",
  "type": "COMPLIANCE",
  "functional_test_targets": []
}
```

#### \_\_init_\_()

Based on the configuration data, one can choose different comparator using ComparatorOptionForList enum.
Please refer Comparator Class and ComparatorOptionForList enum under utils for more details.
BaseController class has already init method with below values but if controller wants, it can
override those. These values are used during check_compliance/remediation.

#### get(context)

One line summary of the what is retrieved.

Optionally, after a blank line, more details may be given. For example, how the content is retrieved or
what format it will be in.
<br/>
Also describe any dependencies that may exist on other configurations or external libraries.
<br/>
Vertical bars can be used to add line blocks.
<br/>
Below is an example of a code block for a JSON object.
<br/>
```json
{
  "servers": [
    {
      "hostname": "8.8.4.4",
      "port": 90,
      "protocol": "TLS"
    },
    {
      "hostname": "8.8.1.8",
      "port": 90,
      "protocol": "TLS"
    }
  ]
}
```

* **Parameters:**
  **context** (*BaseContext*) – Product context instance.
* **Returns:**
  Tuple of current control value and a list of error messages if any.
  NOTE that the control value should be in the same format as the schema for this control.
* **Return type:**
  tuple

#### set(context, desired_values)

One line summary of what is being set.

More details about what the expected desired_values being passed in should be. Maybe an example if appropriate.
This should also describe any pre-requisite or post-requisite required for setting this value.
i.e. if a host needs to be in maintenance mode first, or needs to be restarted after.

* **Parameters:**
  * **context** (*BaseContext*) – The type of context, i.e. VcenterContext.
  * **desired_values** (*The expected type*) – The value that is to be set (dict, string, int, etc.).
* **Returns:**
  Tuple of a status (from the RemediateStatus enum) and a list of errors encountered if any.
* **Return type:**
  tuple

#### check_compliance(context, desired_values)

Check compliance of current configuration against provided desired values.

This function has a default implementation in the BaseController. If needed, you can overwrite it with your
own implementation. It should check the current value of the control against the provided desired_values and
return a dict with key “status” and a status from the ComplianceStatus enum. If
the control is NON_COMPLIANT, it should also include keys “current” and “desired” with their respective values.
If the operation failed, it should include a key “errors” and a list of the error messages.

* **Parameters:**
  * **context** (*BaseContext*) – Product context instance.
  * **desired_values** (*Any*) – Desired values for this control.
* **Returns:**
  Dict of status and current/desired value(for non_compliant) or errors (for failure).
* **Return type:**
  dict

#### remediate(context, desired_values)

Remediate current configuration drifts.

This function has a default implementation in the BaseController. If needed, you can overwrite it with your
own implementation. It should run check compliance and set it to the desired value if it is non-compliant.
This function should return a dict with key “status” and a status from the RemediateStatus enum.
If the value was changed it should also include keys “old” and “new” with their respective values.
If the operation failed, it should include a key “errors” and a list of the error messages.

* **Parameters:**
  * **context** (*BaseContext*) – Product context instance.
  * **desired_values** (*Any*) – Desired values for the specified configuration.
* **Returns:**
  Dict of status and old/new values(for success) or errors (for failure).
* **Return type:**
  dict
