## Testing Controls

### Developer testing (manual)
Test the newly created controller(s) by building config-module and running the compliance or remediate workflows against a VCF deployment.

#### Standalone testing
Since config-module is currently designed as a library, standalone testing can be performed by creating a class invoking respective config-modules functions.

Sample test class to test config-modules VC compliance workflow:

```python
import json
import logging

from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.interfaces.controller_interface import ControllerInterface

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

desired_state_input = {
    "compliance_config": {
        "vcenter": {
            "ntp": {
                "value": {
                    "mode": "NTP",
                    "servers": [
                        "10.0.0.5"
                    ]
                },
                "metadata": {
                    "configuration_id": "1246",
                    "configuration_title": "The vCenter Server must compare internal information system clocks at least every 24 hours with an authoritative time server"
                }
            }
        }
    }
}


def main():
    hostname = "ip_address"
    username = "sso_username"
    password = "sso_password"
    ssl_thumbprint = "ssl_thumbprint"

    vc_context = VcenterContext(hostname=hostname, username=username, password=password, ssl_thumbprint=ssl_thumbprint)
    with vc_context:
        vc_config_obj = ControllerInterface(vc_context)
        try:
            compliance_response = vc_config_obj.check_compliance(desired_state_spec=desired_state_input)
            print(json.dumps(compliance_response, indent=4))
        except Exception as e:
            print(f"An exception occurred: {str(e)}")


if __name__ == "__main__":
    main()
```
##### Sample response structure from config module
###### Sample desired spec:
```json
{
  "compliance_config": {
    "vcenter": {
      "ntp": {
        "metadata": {
          "configuration_id": "1246",
          "configuration_title": "The system must configure NTP time synchronization."
        },
        "value": {
          "servers": ["10.0.0.250", "216.239.35.0"],
          "mode": "NTP"
        }
      },
      "dns": {
        "metadata": {
          "configuration_id": "1271",
          "configuration_title": "DNS should be configured to a global value that is enforced by vCenter."
        },
        "value": {
          "servers": ["10.0.0.250"],
          "mode": "is_static"
        }
      }
    }
  }
}
```
###### Case 1: All controls are compliant
Check compliance response
```json
{
  "status": "COMPLIANT",
  "changes": {
    "compliance_config": {
      "vcenter": {
        "ntp": {
          "status": "COMPLIANT"
        },
        "dns": {
          "status": "COMPLIANT"
        }
      }
    }
  }
}
```
Remediation response
```json
{
  "status": "SUCCESS"
}
```

###### Case 2: At least one control is not compliant
Check compliance response
```json
{
  "status": "NON_COMPLIANT",
  "changes": {
    "compliance_config": {
      "vcenter": {
        "ntp": {
          "status": "NON_COMPLIANT",
          "current": {
            "servers": [
              "10.0.0.250"
            ]
          },
          "desired": {
            "servers": [
              "10.0.0.250",
              "216.239.35.0"
            ]
          }
        },
        "dns": {
          "status": "COMPLIANT",
        }
      }
    }
  }
}
```
Remediate response
```json
{
  "status": "SUCCESS",
  "changes": {
    "compliance_config": {
      "vcenter": {
        "ntp": {
          "status": "SUCCESS",
          "old": {
            "servers": [
              "10.0.0.250"
            ]
          },
          "new": {
            "servers": [
              "10.0.0.250",
              "216.239.35.0"
            ]
          }
        }
      }
    }
  }
}
```

###### Case 3: At least for one control, the check compliance operation failed.
Check Compliance response
```json
{
  "status": "FAILED",
  "changes": {
    "compliance_config": {
      "vcenter": {
        "ntp": {
          "status": "FAILED",
          "errors": [
            "failed to get ntp servers"
          ]
        },
        "dns": {
          "status": "NON_COMPLIANT",
          "current": {
            "servers": [
              "10.0.0.250", "10.0.0.251"
            ]
          },
          "desired": {
            "servers": [
              "10.0.0.250"
            ]
          }
        }
      }
    }
  }
}
```
Remediate response
```json
{
  "status": "FAILED",
  "changes": {
    "compliance_config": {
      "vcenter": {
        "ntp": {
          "status": "FAILED",
          "errors": [
            "failed to get ntp servers"
          ]
        },
        "dns": {
          "status": "SUCCESS",
          "old": {
            "servers": [
              "10.0.0.250", "10.0.0.251"
            ]
          },
          "new": {
            "servers": [
              "10.0.0.250"
            ]
          }
        }
      }
    }
  }
}
```
###### Case 4: The desired state spec contains controls for a non-targeted product
Check compliance is performed against product ‘vcenter’ where all vcenter controls are compliant but desired spec had sddc_maanger product as well.
Check compliance response
```json
{
    "status": "COMPLIANT",
    "changes": {
        "compliance_config": {
            "vcenter": {
                "ntp": {
                    "status": "COMPLIANT"
                },
                "dns": {
                    "status": "COMPLIANT"
                }
            },
            "sddc_manager": {
                "status": "SKIPPED",
                "errors": [
                    "Controls are not applicable for product vcenter"
                ]
            }
        }
    }
}
```
Remediate response
```json
{
    "status": "SUCCESS",
    "changes": {
        "compliance_config": {
            "sddc_manager": {
                "status": "SKIPPED",
                "errors": [
                    "Controls are not applicable for product vcenter"
                ]
            }
        }
    }
}
```
###### Case 5: Remediation is not implemented for the control
Check compliance response
```json
{
    "status": "NON_COMPLIANT",
    "changes": {
        "compliance_config": {
            "vcenter": {
                "cert_config": {
                    "status": "NON_COMPLIANT",
                    "desired": {
                        "certificate_issuer": [
                            "test"
                        ]
                    },
                    "current": "OU=VMware Engineering, O=vcenter-1.vrack.vsphere.local, ST=California, C=US, DC=local, DC=vsphere, CN=CA"
                }
            }
        }
    }
}
```
Remediate response
```json
{
    "status": "SUCCESS",
    "changes": {
        "compliance_config": {
            "vcenter": {
                "cert_config": {
                    "status": "SKIPPED",
                    "message": [
                        "Set is not implemented as this control requires manual intervention"
                    ],
                    "desired": {
                        "certificate_issuer": [
                            "test"
                        ]
                    },
                    "current": "OU=VMware Engineering, O=vcenter-1.vrack.vsphere.local, ST=California, C=US, DC=local, DC=vsphere, CN=CA"
                }
            }
        }
    }
}
```
###### Case 6: Sample response for ESXi product where vcenter is used to perform check compliance/remediation on list of target hosts (Default target is all hosts)
Check compliance response
```json
{
  "status": "COMPLIANT",
  "changes": {
    "esxi-1.vrack.vsphere.local": {
      "status": "COMPLIANT",
      "host_changes": {
        "compliance_config": {
          "esxi": {
            "bridge_protocol_data_unit_filter": {
              "status": "COMPLIANT"
            }
          }
        }
      }
    },
    "esxi-2.vrack.vsphere.local": {
      "status": "COMPLIANT",
      "host_changes": {
        "compliance_config": {
          "esxi": {
            "bridge_protocol_data_unit_filter": {
              "status": "COMPLIANT"
            }
          }
        }
      }
    }
  }
}
```
Remediation response
```json
{
  "status": "SUCCESS"
}
```
###### Case 7: Fail to validate desired state against schema. Desired spec for control(s) is not adhering to schema.
Check compliance response
```json
{
  "message": "['10.0.0.250', '10.0.0.250'] has non-unique elements\n\nFailed validating 'uniqueItems' in schema['properties']['compliance_config']['properties']['sddc_manager']['properties']['ntp']['properties']['value']['properties']['servers']:\n    {'description': 'A valid list of reachable NTP servers',\n     'items': {'type': 'string'},\n     'type': 'array',\n     'uniqueItems': True}\n\nOn instance['compliance_config']['vcenter']['ntp']['value']['servers']:\n    ['10.0.0.250', '10.0.0.250']",
  "status": "ERROR"
}
```
###### Case 8: Exception during reaching the product due to auth failure (incorrect password)
Check compliance response
```json
{
  "status": "FAILED",
  "changes": {
    "compliance_config": {
      "vcenter": {
        "ntp": {
          "status": "FAILED",
          "errors": [
            "401 Client Error:  for url: https://10.0.0.4/v1/tokens/"
          ]
        }
      }
    }
  }
}
```

#### Integration testing with Salt
For testing with salt, 
- Copy the changes to the appliance where salt minion is running. There are two ways to achieve this:
  1. Build and install config-module on the minion (recommended):
     - Build config-modules as a wheel artifact `python3 -m build`
     - Uninstall existing config-modules installation:
       ```
       salt '*' pip.uninstall config_modules
       salt '*' file.remove /opt/saltstack/salt/extras-3.10/config_modules_vmware
       ```
     - Install the wheel artifact on the target minions:
        ```
        salt-cp --chunked '*' dist/config_modules.whl ~/config_modules.whl
        salt '*' pip.install ~/config-module.whl
        ```
  2. Copy or replace the individual file changes to the corresponding config-modules install location in the salt minion (default location is `/opt/saltstack/salt/extras-3.10/config_modules_vmware/..`)
- Create a desired state file (based on the compliance schema) and a state file to invoke check_compliance or remediate workflows (https://github.com/saltstack/salt-ext-modules-vmware/blob/jpmc_compatibility_control/src/saltext/vmware/states/compliance_control.py#L17).

   Sample desired state file (_desired_state.jinja_):
   ```
    {% load_yaml as control_config %}
    compliance_config:
      networking:
        ntp:
          metadata:
            configuration_id: '1246,1601'
            configuration_title: 'Synchronize system clocks to a universal time source for all devices to automatically synchronize.'
          value:
            mode: NTP
            servers:
            - 10.0.0.250
    {% endload %}
   ```
   Sample state file (_network_policy.sls_)
   ```
    {% set product_category = salt['grains.get']('product') %}
    {% from 'desired_state.jinja' import control_config with context %}

    networking_policy_control:
      vmware_compliance_control.check_control:
        - control_config: {{control_config}}
        - product: {{product_category}}
   ```
- Run the state file targeting the minions:
   ```
   (check_compliance) : salt '*' state.apply network_policy test=true
   (remediate) : salt '*' state.apply network_policy
   ```


### Unit testing
For any newly created controller(s), unit test cases need to be added, covering all code paths. This will be run as part of pre-commit (CI) and post-commit (CD) pipelines. It is recommended to use `pytest` module for unit testing.

Unit test cases can be run locally by invoking the script [../devops/scripts/run_functional_tests.sh](../devops/scripts/run_functional_tests.sh) from the root directory. This script also runs the code coverage and produces a report.
[Note: the script is named functional tests as the current CI pipeline expects this.]
