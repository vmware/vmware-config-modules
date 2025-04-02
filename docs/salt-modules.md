# Salt Modules

Config-module workflows, namely check_compliance and remediate can be invoked through Salt using the specified [state](../config_modules_vmware/services/salt/states) and [execution](../config_modules_vmware/services/salt/modules) modules.

## Installation of config-modules with salt

For config-modules workflows to be invoked through salt framework, install config-modules along with the salt dependencies on the respective minions via the Salt master.

`salt '*' pip.install config_modules_vmware[salt]`


## Invoking config-modules through Salt example:

**Pre-requisites:**
* Salt Minion and Master installed and configured.
* Respective grains configured on the appliances:
```
        ESXI = "esxi"
        VCENTER = "vcenter"
        SDDC_MANAGER = "sddc_manager"
        NSXT_MANAGER = "nsxt_manager"
        NSXT_EDGE = "nsxt_edge"
        VRSLCM = "vrslcm"
        VIDM = "vidm"
        VRO = "vro"
        VRA = "vra"
        VRLI = "vrli"   
```

1. Create a desired state file (for vcenter) as below under salt file_roots location:
/srv/salt/desired_state.jinja:
```yaml
{% load_yaml as desired_state %}
compliance_config:
  vcenter:
    ntp:
      metadata:
        configuration_id: '1246'
        configuration_title: 'Synchronize system clocks to a universal time source for all devices to automatically synchronize.'
      value:
        mode: 'NTP'
        servers:
          - '10.0.0.250'
    dns:
      metadata:
        configuration_id: '1271'
        configuration_title: 'For systems using DNS resolution, at least two name servers must be configured.'
      value:
        mode: 'is_static'
        servers:
          - '10.0.0.250'
{% endload %}
```

2. Create a Salt State file:
/srv/salt/compliance.sls
```yaml
{% set product_category = salt['grains.get']('product') %}
{% from 'desired_state.jinja' import desired_state with context %}

compliance_controls:
  vmware_compliance_control.check_control:
    - control_config: {{desired_state}}
    - product: {{product_category}}
```

3. Invoke check_compliance workflow `salt '*' state.apply compliance test=true`

4. Invoke remediate workflow using salt command `salt '*' state.apply compliance`. (**Note:** Invoke this command with caution as it will change the configuration of the targetted appliance.)
