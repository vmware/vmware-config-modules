## Instructions to write a new control

## Glossary

|        Term         | Meaning                                                                      |
|:-------------------:|:-----------------------------------------------------------------------------|
|  compliance schema  | Unified schema to represent each control and its value.                      |
|   control / rule    | Specific product feature configuration required for compliance.              |
|     controller      | Execution script for one or more controls.                                   |
|    desired state    | The expected state for a control to be in, for the system to be compliant.   |

## Disclaimer
The below instructions are for implementing a controller based on current framework implementation that was done for MVP. There will be changes to support new requirements however these changes will be evaluated and designed to not break existing functionality.

## Steps to write a new controller
1. [Evaluate procedures or APIs for the controller implementation.](#1-evaluate-procedures-or-apis-for-the-controller-implementation)
2. [Define compliance schema for the new control.](#2-define-compliance-schema)
3. [Writing the controller class for the controls' compliance workflows.](#3-writing-the-controller-class)
4. [Update the config mapping file.](#4-update-the-config-mapping-file)
5. [Auto-generate documentation for the new controller.](#5-auto-generate-documentation-for-the-new-controller)
6. [Create product context (only required if writing control for a new product).](#6-create-new-product-context)
7. [Write unit test cases for the new controller.](#7-write-unit-test-cases-for-the-new-controller)
8. [Specify any external dependencies.](#8-add-any-external-dependencies)

### 1. Evaluate procedures or APIs for the controller implementation
This process involves figuring out the publicly available APIs or scripts that can be utilized for the audit and remediation workflows for the control. This would also require getting sign-off from the product team on using the right procedure for the control.

### 2. Define compliance schema

##### [NOTE: This is only applicable for `COMPLIANCE` type controls]

Specification for each control should be defined in the [compliance schema](../config_modules_vmware/schemas/compliance_reference_schema.json). This schema serves as a standardized representation of the control's value, and the controller implementation for that control would be implemented based on the schema. The schema is based on [JSONSchema specification](https://json-schema.org/specification) and documentation about the compliance reference schema is captured [here](../docs/compliance-schema-documentation.md)

#### Things to follow while writing schema spec for a new control

1. Controls need to be grouped under a product which they belong to (e.g vcenter, sddc_maanger etc.).
2. Each control needs to have a `value` field which will contain the primitive or complex value for that control.
3. Each control needs to include `metadata` as one of its properties. `metadata` currently includes two properties - `configuration_id` and `configuration_title` for the control. These properties correspond to the config ID and title specified in the compliance kit published by VMware. When specified as part of input desired state, these properties help identify the control and would be used in reporting, in-future.
4. Any restrictions for the control's value should be added to the schema. Available list of JSONSchema validations: https://json-schema.org/draft-07/draft-handrews-json-schema-validation-01. If a validation is required that is not covered by jsonSchema validators, it can be implemented in the controller implementation as well.

Sample schema format for a new control (my_control):
```json
{
  "compliance_config": {                            <--- root
    "properties": {
      "my_product": {                                 <--- product
          "my_control": {                           <--- control key
            "type": "object",
            "properties": {
              "metadata": {                         
                "$ref": "#/definitions/metadata",   <--- includes 'configuration_id' and 'configuration_title'
              },
              "value": {                            <--- control value spec
                "type": "object",
                "properties": {
                  "config_1": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "value_list": {
                          "type": "string"
                        },
                        "name": {
                          "type": "string"
                        }
                        }
                      }
                      },
                      "required": [ "value_list", "name" ]  <--- list validator
                    },
                    "uniqueKey": "name",           <--- (Optional) property name to uniquely identify  each elements/instances in an array. Validation should be added by respective controllers.
                    "minItems": 1                   <--- property validator
                  },
                  "config_2": {
                    "type": "number",
                    "minimum": 0,                   <--- number validator
                    "maximum": 100                  <--- number validator
                  },
                  "config_3": {
                    "type": "string",
                    "maxLength": 12                 <--- string validator
                  }
                },
                "required": [ "config_2" ],         <--- property validator
                "additionalProperties": false,      <--- property validator 
```

#### Schema usage
1. The schema is used in validating the input desired state, making sure that the controllers can work consistently.
2. The schema serves as a reference for the customer to create the input desired state.

### 3. Writing the Controller class
Create a new python file for the new controller class. Controllers should all be located under [config_modules_vmware/controllers](../config_modules_vmware/controllers) in the respective product subdirectory. If the control is for a new product that is not yet implemented in config-modules, a subdirectory for the new product should be added, which will contain the newly created controller. The subdirectory should be named after the product that the control is associated with. In addition to the controller it also must have an `__init.py__` file created.

Every controller class must do the following:
1. Inherit from the parent [BaseController](../config_modules_vmware/controllers/base_controller.py) class.
2. Instantiate a class attribute called `metadata` of type [ControllerMetadata](../config_modules_vmware/framework/models/controller_models/metadata.py).
3. Implement the `get` and `set` methods. These functions would be used by the framework for **check compliance** and **remediate** workflows respectively.

##### Example class and metadata definition
```python
logger = LoggerAdapter(logging.getLogger(__name__))

class SampleController(BaseController):
    """ Class for config operations related to this Sample Controller"""
    metadata = ControllerMetadata(
        name="sample_controller_name",  # controller name
        path_in_schema="compliance_config.sample_product.sample_controller_name",  # path in the schema to this controller's definition.
        configuration_id="-1",  # configuration ID as defined in compliance kit.
        title="sample config title defined in compliance kit",  # controller title as defined in compliance kit.
        tags=["sample", "test"],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.DISABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        type=ControllerMetadata.ControllerType.COMPLIANCE, # controller type i.e. compliance control or whole product configuration
    )
```

##### Get function
The `get` function should include implementation to retrieve a control's current value from the product. This function takes in `context: BaseContext` as input, which refers to the product's context class (eg. [VcenterContext](../config_modules_vmware/framework/auth/contexts/vc_context.py)). This context holds the auth information and any clients that are initialized as part of creating the context. The `get` function is expected to return a tuple of the retrieved value, in the format of the [compliance schema](../config_modules_vmware/schemas/compliance_reference_schema.json) value for that control, and a list of errors encountered, if any. The returned value would then be compared with the input desired state to identify for any drifts, hence the need for this `get` function to return in similar format as the control spec defined in the compliance schema.
[Note: There are plans to model the return types from these functions into its own classes for future proofing.]

When implementing a `CONFIGURATION` type control (i.e. vCenter Profiles), the `get` function also accepts an optional parameter `template`. This will default to `None` but if provided can be used to filter and populate the results from the product control's current value. For `COMPLIANCE` type controls, the `template` parameter will not be used and can be safely ignored.

```python
def get(self, context: BaseContext, template: dict = None) -> Tuple[Any, List[str]]:
```

BaseClass 'check_compliance' method reports the drifts(only those fields which are non-compliant) between desired and current. If customization is needed to compare the input desired state with the retrieved value (like ignoring certain fields, etc), the controller can override the `check_compliance` method:
```python
def check_compliance(self, context: BaseContext, desired_values: Any) -> Dict:
```

##### Set function
The `set` function should include implementation to set the desired values on the product for remediation. This function is expected to return a tuple of the status from the set operation (from the [RemediateStatus enum](../config_modules_vmware/framework/models/output_models/remediate_response.py)) and a list of errors encountered, if any.
```python
def set(self, context: BaseContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
```
By default, remediate workflow first invokes the `check_compliance` method and invokes `set` method only if the values are non_compliant. An override capability is provided to override the default `remediate` function behavior.
```python
def remediate(self, context: BaseContext, desired_values: Any) -> Dict:
```
See [SampleController](../config_modules_vmware/controllers/sample/sample_controller.py) for reference implementation.

[Note: Newer functions to handle new requirements would be added in future.]

### 4. Update the Config Mapping file

##### Compliance Controls
The controller classes are ultimately invoked by the framework, which dynamically imports the appropriate controller class based on the input desired state from the user. The right controller class is imported based on the mapping defined in [control_config_mapping.json](../config_modules_vmware/services/mapper/control_config_mapping.json). This maps a control key to the path where the controller class can be found.

For example, let us say a new controller, for control `my_control` is implemented at `../config_modules_vmware/controllers/my_product/my_control_config.py` and has defined the `MyControlConfig` class. The control_config_mapping.json file then needs to be updated with something like the example below:
```json
{
  "compliance_config": {
    "my_product": {
      "my_control": "config_modules_vmware.controllers.my_product.my_controller.MyControlConfig"
    },
    ...
  }
}
```
The control_config_mapping.json file follows a similar structure as the [compliance schema](../config_modules_vmware/schemas/compliance_reference_schema.json) until the control key (`my_control`). For example, for a control spec (`syslog`) that is applicable for product (`vcenter`):
```json
{
  "compliance_config": {
    "vcenter": {
      "syslog": {
        "value": {
          "servers": [
            {
              "hostname": "8.8.4.4",
              "port": 90,
              "protocol": "TLS"
            }
          ]
        }
      }
    }
  }
}
```
the corresponding entry in the config mapping file would look like:
```json
{
  "compliance_config": {
    "vcenter": {
      "syslog": "config_modules_vmware.controllers.vcenter.syslog_config.SyslogConfig"
    }
  }
}
```

##### Configuration Controls

For configuration type controls (i.e. vCenter Profiles), a separate mapping file is used - [configuration_mapping.json](../config_modules_vmware/services/mapper/configuration_mapping.json).

This maps a product to a control. Each control can support multiple product versions. The control internally will fetch the product version and invoke the corresponding logic for that version.

```json
{
  "vcenter": "config_modules_vmware.controllers.vcenter.vc_profile.VcProfile"
}
```

### 5. Auto-generate documentation for the new controller
Documentation for each controller is auto-generated based on the docstrings written in the class. Refer to the [SampleController](../config_modules_vmware/controllers/sample/sample_controller.py) for examples of how to format the docstrings. Documentation for the [SampleController](../config_modules_vmware/controllers/sample/sample_controller.py) is located at [sample.sample_controller.md](./controllers/markdown/sample/sample.sample_controller.md).

Controller developer needs to run a script to auto-generate the docstring and check-in as part of merge request process.

After writing a new controller, running the script [generate_markdown_docs.sh](../devops/scripts/generate_markdown_docs.sh) will create a new markdown file for the controller at `./controllers/markdown/my_product/my_controller.md`.

**Do not forget to `git add` the auto-generated documentation directories and files that were created for your new controller.**

### 6. Create new product context
**[This section is only required to onboard a new product to config-modules.]**

#### Register product auth context
Extend the `../config_modules_vmware/framework/auth/contexts/base_context.py` class and create a context for the new product in the `../config_modules_vmware/framework/auth/contexts/my_product/` directory. This context class should also assign the `product_category` (vcenter/nsx/sddc_manager...) attribute in the BaseContext class. The product context class includes any credentials information that are required by the controllers and holds any connection to be used in the controller implementation.

For e.g, [VcenterContext](../config_modules_vmware/framework/auth/contexts/vc_context.py) contains the sso_credentials and initializes vmomi and rest clients to be used in the controllers.

#### Product clients
Create any required product specific interfaces or dependencies that are required by the controllers or context under `../config_modules_vmware/lib/my_product/`. Example: [VcVmomiSSOClient](../config_modules_vmware/framework/clients/vcenter/vc_vmomi_sso_client.py)

#### Please refer below for saltext changes required if any new product is added.
[SaltExt Changes to support new product](./saltext-changes_to_support_new_product.md)

### 7. Write unit test cases for the new controller
Unit test cases must be written for any new controller, covering all code paths. Sample unit test case for the [SampleController](../config_modules_vmware/controllers/sample/sample_controller.py) is at [TestSampleController](../config_modules_vmware/tests/controllers/sample/test_sample_controller.py).

### 8. Add any external dependencies
Any external dependencies that are imported and utilized in the controller class should be specified in the `requirements/prod-requirements.txt`. This makes sure that the dependency is pulled and installed whenever config-module is installed on the target system.
