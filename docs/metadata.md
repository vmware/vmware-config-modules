# Config Modules Metadata Publishing

Metadata can be included in the responses from the ControllerInterface get_current_configuration, remediate_with_desired_state and check_compliance functions. Configuration pertaining to metadata publishing can be made in the [config.ini](../config_modules_vmware/services/config.ini) or config-overrides.ini file.

## Steps to create custom metadata and publish using config-modules directly
1. To enable publishing of metadata in the workflow responses, set the value `PublishMetadata` to `true` in the config.ini. [See [configuration](./configuration.md) for more information on creating and using config-overrides.ini.]
2. [Optional - Creating custom metadata for publishing]. Custom metadata can be provided to each controller through a JSON file. The absolute path to the file should be put in the `config.ini` under `metadata:MetadataFileName`. Custom metadata can also be pre-validated using the static function  `validate_custom_metadata` from the [ControllerMetadataInterface](../config_modules_vmware/interfaces/metadata_interface.py). It accepts the custom metadata as a dict and will raise an exception if it finds any validation errors.
The contents of the custom metadata file should be in json format described below, similar to the controller schema.
```json
{
  "PRODUCT": {
    "CONTROLLER_NAME": {
      "metadata": {
        "custom_metadata_key": "custom metadata value. This can also be a complex type (dict). It can also override default metadata that is built in to the controller, like the configuration_id or title" 
      }
    }
  }
}
```
For example:
```json
{
  "vcenter": {
    "backup_schedule_config": {
      "metadata": {
        "new_metadata_key": "new_metadata_value",
        "new_complex_metadata": {
          "child_new_metadata_key": "child_new_metadata_value"
        },
        "title": "This is my new overridden title"
      }
    }
  }
}
```
3. The metadata that is published can either be only the custom provided metadata or all of the controller's existing metadata. This is controlled in the config.ini with the `IncludeOnlyCustomMetadata` flag, which only publishes custom metadata and ignores any existing metadata from the controllers.

## Steps to create custom metadata and publish using salt modules.

Steps to create custom metadata for publishing through salt.
1. Create a config-overrides.ini file overwriting the values in config.ini, as below:
```
# Configuration for metadata of controllers
# PublishMetadata: To include / exclude the metadata from the controllers in the response
# MetadataFileName: An absolute path to the JSON file with the desired custom metadata.
#   The contents of this file should match the schema starting at product level. For example:
#     {
#         "vcenter": {
#             "ntp": {
#               "metadata": {
#                 "new_metadata_key": "new_metadata_value"
#               }
#             }
#         }
#     }
# IncludeOnlyCustomMetadata: If the metadata being published in the responses
#    should include only the custom metadata from the file, or all controller metadata.
[metadata]
PublishMetadata=true
MetadataFileName=/tmp/config-module/controller_metadata.json
IncludeOnlyCustomMetadata=false
```
2. Copy config-overrides.ini file to some directory on the targetted minion (here it is "/opt/saltstack/salt/extras-3.10/config_modules_vmware/services/" but can be any directory)
```shell
salt-cp --chunked -G 'product:<<product_category>>' config-overrides.ini /opt/saltstack/salt/extras-3.10/config_modules_vmware/services/
```
3. Set the "OVERRIDES_PATH" env variable to that same directory
```shell
salt -G 'product:<<product_category>>' environ.setenv '{"OVERRIDES_PATH": "/opt/saltstack/salt/extras-3.10/config_modules_vmware/services/"}' update_minion=True
```
4. Create the metadata file under salt environment /srv/salt/custom_metadata.jinja (using jinja format as a sample).

```
{% load_yaml as custom_metadata %}
vcenter:
  ntp:
    metadata:
      global_key: "global_value"
      configuration_id: "1111"
{% endload %}
```
5. Create a new state file ( (/srv/salt/custom_metadata.sls) to validate and persist the custom metadata onto the minions. The state file follows similar approach as the Salt file.managed module and the destination path should match the value specified for key `MetadataFileName` in the config-overrides from step 1. [There is also a salt execution module [controller_metadata.py](../config_modules_vmware/services/salt/modules/controller_metadata.py) that can be used to only validate and not persist the custom metadata.]
```
{% from 'custom_metadata.jinja' import custom_metadata with context %}

# Pass controller metadata contents to 'controller_metadata'
# Supports additional arguments from salt.states.file.managed (except 'contents' param which is being used)
# https://docs.saltproject.io/en/latest/ref/states/all/salt.states.file.html#salt.states.file.managed
/tmp/config-module/controller_metadata.json:
    vmware_controller_metadata.managed:
    - controller_metadata: {{custom_metadata}}
    - user: root
    - group: root
    - mode: 644
    - makedirs: True
    - replace: True

```
6. By invoking the below salt command, the custom metadata will first be validated, raising an exception if it encounters any validation errors. Otherwise, it will proceed with persisting the file onto the minions.

```shell
salt -G 'product:<<product_category>>' state.apply custom_metadata
```

## Querying Metadata
To query controller metadata, call the static function `get_metadata_from_query` from the [ControllerMetadataInterface](../config_modules_vmware/interfaces/metadata_interface.py) and pass it a query function. See the next section for more information on what the query function is.
### Built-in query functions
A few common query functions have been built into the framework. See [ControllerMetadataInterface](../config_modules_vmware/interfaces/metadata_interface.py) to see what is available before defining custom functions.

Below is an example of using one of these built-in functions to query for controllers with the configuration ID 1234.
```python
controllers_with_id_1234 = ControllerMetadataInterface.get_metadata_from_query(ControllerMetadataInterface.query_by_id(1234))
```
### Defining a query function
A query function is expected to take in a single parameter, an instance of ControllerMetadata, and return True if that metadata complies with the query and False otherwise.

For example, to query for controller metadata that has "TEST" in its title, a function could be defined like this 
```python
def metadata_title_test(metadata: ControllerMetadata):
    return "TEST" in metadata.title
```
That function would then be passed to the `get_metadata_from_query` function like this
```python
controllers_with_test_in_the_title = ControllerMetadataInterface.get_metadata_from_query(metadata_title_test)
```
Obviously this is a very simple example and the logic in the function can be more complex.

### Using a lambda function
For simple queries, it may be sufficient to define a lambda function. 

Below is an example of a lambda function to check for controllers that are disabled.
```python
controllers_with_disabled_status = ControllerMetadataInterface.get_metadata_from_query(lambda metadata: metadata.status == ControllerMetadata.ControllerStatus.DISABLED)
```