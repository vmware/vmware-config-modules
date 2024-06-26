# Changes in saltext to create auth context for new product

This document outlines the changes required to be done in the saltext to create a new product authentication context. The changes are to be made in utils/compliance_control.py located at the provided link.
#### Utils file path: https://github.com/saltstack/salt-ext-modules-vmware/blob/unified_config_management/src/saltext/vmware/utils/compliance_control.py

### Steps to support a new product (Product name: 'new_product')
If a new product is introduced, you need to add support for it in the create_auth_context function in saltext. Auth context objects creation is to be done in salt-ext(client side) to keep config module separated from salt constructs.
Saltext compliance_control module will consume config-module ControllerInterface check compliance/remediation APIs against a product using corresponding authentication context. 
##### 1. Determine the corresponding product context class from dir [contexts](../config_modules_vmware/framework/auth/contexts) and product enum from the [ProductEnum](../config_modules_vmware/framework/auth/contexts/base_context.py)
##### 2. [Optional] Configure pillar and/or grains for the product which needs to be fetched and used to create authentication context (data like username, password etc)
##### 3. Add utility function to create the authentication context for the new product.
This function initializes the authentication context class with the required configuration parameters read from the pillar/grains configured for the product.
##### Sample code
```python
from config_modules_vmware.framework.auth.contexts.new_product_context import NewProductContext

def _create_new_product_context(conf):
    return NewProductContext(
        hostname=conf["host"],
        username=conf["user"],
        # Add other required parameters to instantiate the authentication context object for the product
    )
```
##### 4. Modify the existing function _create_product_context
This function is responsible for fetching the conf from pillar/grains and based on the product type create specific product authentication context
##### Sample code
```python
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext

def _create_product_context(config, product, ids=None):
    conf = ( 
            config.get("pillar", {}).get(product)
            or config.get("grains", {}).get(product)
            or {}
    ) # Read the conf from pillar or grains etc
    if product == BaseContext.ProductEnum.NEW_PRODUCT.value:
       return _create_new_product_context(conf)
```

#### Example of creating a 'vcenter' product auth context.
To illustrate how to create a sample product context on the salt-ext side, let's consider an example scenario of creating a vcenter authentication context

#### Sample pillar conf for product 'vcenter'
```yaml
vcenter:
    host: <vc_ip>
    password: <vc_password>
    user: <vc_uname>
    ssl_thumbprint: <vc_ssl_thumbprint>
```
Note: For developer or testing deployments, you can skip ssl thumbprint verification by adding "verify_ssl: False" in the pillar configuration for vcenter and sddc-manager minions. This is **NOT** recommended for production deployments.

#### Sample python code to create authentication context for product 'vcenter'
```python
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext

def _create_vcenter_context(conf):
    return VcenterContext(
        hostname=conf["host"],
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
    )

# Please refer the latest utils/compliance_control.py to check currently supported products.
# Below is an example for vcenter only. For any new product you can add elif for the product and return respective create_context.
def _create_product_context(config, product, ids=None):
    # If there is a parent product ( for e.g., for 'esxi', parent product is 'vcenter') get the pillar/grains info for parent product 
    # Else get for the pillar/grains for the product
    # Read conf from the pillar or grains for the parent_product or product, then create respective product auth context.
    conf = config.get("pillar", {}).get(product)
    if product == BaseContext.ProductEnum.VCENTER.value:
       return _create_vcenter_context(conf)
    # Add support for other products here

def create_auth_context(config, product, ids=None):
    return _create_product_context(config=config, product=product, ids=ids)
```

