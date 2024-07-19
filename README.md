# Config Modules

Config-modules is a library that can be utilized by services written in python to run compliance checks (audit and remediation) for multiple products.

## Why Config Modules

1. **Consistent Interface**: Config-modules design helps achieve a consistent interface to invoke compliance workflows, no matter the differences in product level implementation. 
2. **Simplified Implementation**: Using a schema based approach helps achieve a simplified controller implementation. Schema serves as the contract between the customer input and the controller logic.
3. **Future-proof integration**: The config module design enables products to catch up any missing APIs without disrupting existing upstream implementations. For example, VC Profile API is under development, we are working with respective product owners to close the gap in future versions. 
4. **Adaptability**: The config module is highly reusable across various automation integrations, offering versatility in different deployment scenarios.
5. **Independent development and Testing**: Config module design enables controller owners to independently develop and test product specific drift and remediation.
6. **Seamless SaltStack Integration**: Leveraging the strengths of SaltStack, config-modules seamlessly integrates as a library for Salt extensions, enhancing exisitng workflowless.

# Documentation Index

| Document                                                                                    |
|---------------------------------------------------------------------------------------------|
| 1. [Contributing and Getting Started](CONTRIBUTING.md)                                      |
| 2. [Configuration](docs/configuration.md)                                                   |
| 3. [Instructions to Create New Controllers](docs/instructions-to-create-new-controllers.md) |
| 4. [Testing Controllers](docs/testing-controllers.md)                                       |
| 5. [Controller Documentation](docs/controllers/markdown/index.md)                           |
| 6. [Metadata](docs/metadata.md)                                                             |
| 7. [Functional Test](functional_tests/README.md)                                            |
| 8. [API Service Documentation](docs/api-service.md)                                         |
| 9. [Building and Running in Docker](docs/docker-instructions.md)                            |

## Directory Structure

```
|--config_modules_vmware
|  |--controllers               <---- logic for controllers               
|  |  |--vcenter               
|  |  |--sddc_manager
|  |  |--....
|  |--framework                 <---- framework related classes
|  |  |--auth       
|  |  |  |--contexts            <---- product specific context
|  |  |--clients                <---- product specific client connections
|  |  |--models                 <---- model class folder
|  |  |--utils                  <---- utils
|  |--interfaces                <---- user interfaces and APIs to call. 
|  |--schemas                   <---- schemas and related utility functions 
|  |--services                  <---- service classes (mapper, operations, etc)
|  |--tests                     <---- unit test folder
|--functional_tests             <---- functional test folder
|--docs                         <---- useful documentation
|--devops                       <---- scripts for CI/CD
```
