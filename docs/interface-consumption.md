# Config Modules Interface Consumption
## Metadata Interface
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