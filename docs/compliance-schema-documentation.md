## Compliance Schema Documentation

Compliance Schema link: [Compliance Schema](../config_modules_vmware/schemas/compliance_reference_schema.json)

1. Schema serves as a contract between the customer provided desired state value and the controller class inside the config-module.
2. Config-module validates the spec provided by the customer against the compliance reference schema. This validation is done before the spec reaches any controller class.
3. The compliance reference schema is based on [JSONSchema specification](https://json-schema.org/specification).
4. All controls in the schema are grouped based on the product type (vcenter, sddc_manager, etc.)
5. Each control spec has a 'metadata' property, which is purely used to identity the control. This is not used by config-modules.
6. The 'value' property inside a control spec is what a controller class receives and operates on.

##### Sample compliance schema with one control and explanation
```
{
  "$schema": "http://json-schema.org/draft-07/schema#",  ----> JSONSchema version 
  "title": "Compliance Reference Schema",
  "description": "Version 1.0.0; last updated 4-Jan-2024",
  "type": "object",
  "properties": {
    "compliance_config": {
      "type": "object",
      "title": "Compliance configuration",
      "description": "Includes all products and compliance controls under those products",
      "properties": {
        "vcenter": {                            ----> Controls are grouped by product type
          "type": "object",
          "title": "Compliance controls related to vcenter",
          "properties": {
            "syslog": {                         ----> syslog vcenter control. 
              "type": "object",
              "properties": {
                "metadata": {                   ----> Every control includes a metadata section to identify the control
                  "$ref": "#/definitions/metadata"
                },
                "value": {                      ----> Corresponding control class acts on this value
                  "type": "object",
                  "properties": {
                    "servers": {
                      "type": "array",
                      "description": "A valid list of syslog servers",
                      "items": {
                        "type": "object",
                        "properties": {
                          "hostname": {
                            "type": "string"
                          },
                          "port": {
                            "type": "number"
                          },
                          "protocol": {
                            "enum": [
                              "TLS",
                              "UDP",
                              "RELP",
                              "TCP"
                            ]
                          }
                        },
                        "required": [
                          "hostname",
                          "port",
                          "protocol"
                        ],
                        "additionalProperties": false
                      },
                      "minItems": 1             ----> JSONSchema validator mentioning that the array should have min 1 item
                    }
                  },
                  "required": [
                    "servers"
                  ],
                  "additionalProperties": false
                }
              },
              "required": [
                "value"
              ],
              "additionalProperties": false
            }
          }
        }
      }
    }
  },
  "required": [                               ----> JSONSchema validator mentioning a required property
    "compliance_config"
  ],
  "additionalProperties": false,              ----> validator mentioning that no additional properties can be specified
  "definitions": {                            ----> common definitions used across _properties_
    "metadata": {
      "type": "object",
      "title": "Metadata",
      "description": "Metadata for a configuration control",
      "properties": {
        "configuration_id": {
          "type": "string",
          "description": "This is the configuration ID listed in the compliance kit"
        },
        "configuration_title": {
          "type": "string",
          "description": "This is the configuration title listed in the compliance kit"
        }
      },
      "required": [
        "configuration_id",
        "configuration_title"
      ]
    }
  }
}
```

##### Sample desired spec based on the above sample compliance schema:
```json
{
  "compliance_config": {
    "vcenter": {
      "syslog": {
        "value": {
          "servers": [
            {
              "hostname": "10.193.2.105",
              "port": 514,
              "protocol": "UDP"
            }
          ]
        },
        "metadata": {
          "configuration_id": "1218",
          "configuration_title": "Configure the appliance to send logs to a central log server."
        }
      }
    }
  }
}
```
