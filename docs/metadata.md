# Config Modules Interface Consumption
## Metadata config
Metadata config settings can be made in the [config.ini](../config_modules_vmware/services/config.ini) or config-overrides.ini file. See [configuration](./configuration.md) for more information on creating and using config-overrides.ini.  
The metadata that is included can either be only the custom provided metadata or all of the controller's metadata. This is controlled in the config.ini with the `IncludeOnlyCustomMetadata` flag. More on custom metadata in the next section. 
### Including metadata in the responses
Metadata can be included in the responses from the ControllerInterface get_current_configuration, remediate_with_desired_state and check_compliance functions. 
To do this, set the value `PublishMetadata` to `true` in the config.ini.
### Custom Metadata
Custom metadata can be provided to each controller through a JSON file. The absolute path to the file should be put in the `config.ini` under `metadata:MetadataFileName`.
The contents of this file should be in json format described below, similar to the controller schema.
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

#### Validating custom metadata

Custom metadata can be validated using the static function  `validate_custom_metadata` from the [ControllerMetadataInterface](../config_modules_vmware/interfaces/metadata_interface.py). It accepts the custom metadata as a dict and will raise an exception if it finds any validation errors.

There is also a salt extension module provided by [controller_metadata.py](https://github.com/saltstack/salt-ext-modules-vmware/blob/unified_config_management/src/saltext/vmware/states/controller_metadata.py). This salt state module will invoke the `validate_custom_metadata` method before invoking the `file.managed` state module to persist the file on the salt minions.

##### Sample salt state file

Below is a sample salt state file which uses the controller metadata state module to validate and persist the custom metadata onto the salt minions.

```yaml
# custom_metadata.sls

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

By invoking a command like below using salt, it will first validate the custom metadata, raising an exception if it encounters a validation errors. Otherwise, it will proceed with persisting the file onto the minions.

```shell
$ salt -G 'product:<<product_category>>' state.apply custom_metadata
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