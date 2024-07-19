# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from typing import Callable
from typing import Dict

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.logging.logging_context import HostnameLoggingContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceResponse
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationResponse
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.models.output_models.output_response import OutputResponse
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateResponse
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.interfaces.metadata_interface import ControllerMetadataInterface
from config_modules_vmware.services.workflows.compliance_operations import ComplianceOperations
from config_modules_vmware.services.workflows.configuration_operations import ConfigurationOperations
from config_modules_vmware.services.workflows.operations_interface import Operations

logger = LoggerAdapter(logging.getLogger(__name__))


class ControllerInterface:
    """Class to implement config management functionalities for control config(s)."""

    def __init__(self, context: BaseContext):
        self._context = context
        ControllerMetadataInterface.load_custom_metadata_file()

    def get_current_configuration(
        self,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
        controller_type: ControllerMetadata.ControllerType = ControllerMetadata.ControllerType.COMPLIANCE,
        template: dict = None,
    ) -> Dict:
        """Get current configuration from controllers.

        Sample response for PARTIAL case:

        .. code-block:: json

            {
              "result": {
                "compliance_config": {
                  "vcenter": {
                    "ntp": {
                      "value": {
                        "mode": "NTP",
                        "servers": ["10.0.0.250"]
                      }
                    },
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
              },
              "status": "PARTIAL",
              "message": "Failed to get configuration for - [networking.dns]"
            }

        Sample response for SUCCESS case:

        .. code-block:: json

            {
              "result": {
                "compliance_config": {
                  "vcenter": {
                    "ntp": {
                      "value": {
                        "mode": "NTP",
                        "servers": ["10.0.0.250"]
                      }
                    },
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
              },
              "status": "SUCCESS"
            }

        Sample response for FAILED case:

        .. code-block:: json

            {
              "status": "FAILED",
              "message": "Failed to get configuration for - [vcenter.ntp, vcenter.dns]"
            }

        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        :param controller_type: Type of controller to invoke
        :type controller_type: ControllerMetadata.ControllerType
        :param template: Template to populate for the targeted configuration
        :type template: dict
        :return: Get Current Configuration output.
        :rtype: dict
        """
        with HostnameLoggingContext(self._context.hostname):
            logger.info("Running get current configuration.")
            get_current_output = GetCurrentConfigurationResponse()
            try:
                self._invoke_workflow(
                    template,
                    get_current_output,
                    Operations.GET_CURRENT,
                    metadata_filter,
                    controller_type,
                )
            except Exception as e:
                logging.error(f"Exception in get current configuration {e}")
                get_current_output.status = GetCurrentConfigurationStatus.ERROR
                get_current_output.message = str(e)
            return get_current_output.to_dict()

    def check_compliance(
        self,
        desired_state_spec: Dict = None,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
        controller_type: ControllerMetadata.ControllerType = ControllerMetadata.ControllerType.COMPLIANCE,
    ) -> Dict:
        """Check audit compliance for the product or product attributes.

        Sample desired_state_spec:

        .. code-block:: json

            {
              "compliance_config": {
                "vcenter": {
                  "ntp": {
                    "metadata": {
                      "configuration_id": "1246",
                      "configuration_title": "Configure the ntp servers"
                    },
                    "value": {
                        "mode": "NTP",
                        "servers": ["10.0.0.250", "216.239.35.8"]
                    }
                  },
                  "dns": {
                    "metadata": {
                      "configuration_id": "0000",
                      "configuration_title": "Configure the dns servers"
                    },
                    "value": {
                        "mode": "is_static",
                        "servers": ["10.0.0.250"]
                    }
                  },
                  "syslog": {
                    "metadata": {
                      "configuration_id": "1218",
                      "configuration_title": "Configure the dns servers"
                    },
                    "value": {
                        "servers": [{"hostname": "8.8.4.4",
                        "port": 90,
                        "protocol": "TLS"},
                        {"hostname": "8.8.1.8",
                        "port": 90,
                        "protocol": "TLS"}]
                    }
                  }
                }
              }
            }

        Sample response for non_compliant case:

        .. code-block:: json

            {
                "changes": {
                    "compliance_config": {
                        "vcenter": {
                            "ntp": {
                                "status": "COMPLIANT"
                            },
                            "dns": {
                                "status": "COMPLIANT"
                            },
                            "syslog": {
                                "status": "NON_COMPLIANT",
                                "current": {
                                    "servers": [
                                        {
                                            "hostname": "8.8.4.4",
                                            "protocol": "TLS",
                                            "port": 90
                                        }
                                    ]
                                },
                                "desired": {
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
                            }
                        }
                    }
                },
                "status": "NON_COMPLIANT"
            }

        Sample response for compliant case:

        .. code-block:: json

            {
                "changes": {
                    "compliance_config": {
                        "vcenter": {
                            "ntp": {
                                "status": "COMPLIANT"
                            },
                             "dns": {
                                "status": "COMPLIANT"
                            },
                            "syslog": {
                                "status": "COMPLIANT",
                            }
                        }
                    }
                },
                "status": "COMPLIANT"
            }


        Sample response for failure cases:

        .. code-block:: json

            {
                "changes": {
                    "compliance_config": {
                        "vcenter": {
                            "ntp": {
                                "status": "FAILED",
                                "errors": [
                                    "failed to get ntp servers."
                                ]
                            },
                            "dns": {
                                "status": "COMPLIANT"
                            },
                            "syslog": {
                                "status": "NON_COMPLIANT",
                                "current": {
                                    "servers": [
                                        {
                                            "hostname": "8.8.4.4",
                                            "protocol": "TLS",
                                            "port": 90
                                        }
                                    ]
                                },
                                "desired": {
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
                            }
                        }
                    }
                },
                "status": "FAILED"
            }

        Sample response for failure cases before reaching control logic:

        .. code-block:: json

            {
                "status": "FAILED",
                "message": "exception message"
            }

        :param desired_state_spec: Desired state controls spec.
        :type desired_state_spec: dict
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        :param controller_type: Type of controller to invoke
        :type controller_type: ControllerMetadata.ControllerType
        :return: Compliance output.
        :rtype: dict
        """
        with HostnameLoggingContext(self._context.hostname):
            logger.info("Running check compliance workflow with desired spec.")
            compliance_output = ComplianceResponse()
            compliance_output.status = ComplianceStatus.COMPLIANT

            try:
                self._invoke_workflow(
                    desired_state_spec, compliance_output, Operations.CHECK_COMPLIANCE, metadata_filter, controller_type
                )
            except Exception as e:
                logging.error(f"Exception in check compliance workflow {e}")
                compliance_output.status = ComplianceStatus.ERROR
                compliance_output.message = str(e)
            return compliance_output.to_dict()

    def remediate_with_desired_state(
        self,
        desired_state_spec: Dict = None,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
        controller_type: ControllerMetadata.ControllerType = ControllerMetadata.ControllerType.COMPLIANCE,
    ) -> Dict:
        """Remediate product attributes which are non-compliant.

        Sample desired_state_spec:

        .. code-block:: json

            {
              "compliance_config": {
                "vcenter": {
                  "ntp": {
                    "metadata": {
                      "configuration_id": "1246",
                      "configuration_title": "Configure the ntp servers"
                    },
                    "value": {
                        "mode": "NTP",
                        "servers": ["10.0.0.250", "216.239.35.8"]
                    }
                  },
                  "dns": {
                    "metadata": {
                      "configuration_id": "0000",
                      "configuration_title": "Configure the dns servers"
                    },
                    "value": {
                        "mode": "is_static",
                        "servers": ["10.0.0.250"]
                    }
                  },
                  "syslog": {
                    "metadata": {
                      "configuration_id": "1218",
                      "configuration_title": "Configure the dns servers"
                    },
                    "value": {
                        "servers": [{"hostname": "8.8.4.4",
                        "port": 90,
                        "protocol": "TLS"},
                        {"hostname": "8.8.1.8",
                        "port": 90,
                        "protocol": "TLS"}]
                    }
                  }
                }
              }
            }

        Sample response for successful remediation cases:

        .. code-block:: json

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
                                        "216.239.35.8"
                                    ]
                                }
                            },
                            "dns": {
                                "status": "SUCCESS"
                            },
                            "syslog": {
                                "status": "SUCCESS",
                                "old": {
                                    "servers": [
                                        {
                                            "hostname": "8.8.4.4",
                                            "protocol": "TLS",
                                            "port": 90
                                        }
                                    ]
                                },
                                "new": {
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
                            }
                        }
                    }
                }
            }

        Sample response for failed remediation cases:

        .. code-block:: json

            {
                "status": "FAILED",
                "changes": {
                    "compliance_config": {
                        "vcenter": {
                            "ntp": {
                                "status": "FAILED",
                                "errors": [
                                    "failed to set ntp servers.",
                                    "failed to set ntp mode."
                                ]
                            },
                            "dns": {
                                "status": "SUCCESS"
                            },
                            "syslog": {
                                "status": "SUCCESS",
                                "old": {
                                    "servers": [
                                        {
                                            "hostname": "8.8.4.4",
                                            "protocol": "TLS",
                                            "port": 90
                                        }
                                    ]
                                },
                                "new": {
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
                            }
                        }
                    }
                }
            }

        :param desired_state_spec: Desired state controls spec.
        :type desired_state_spec: dict
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        :param controller_type: Type of controller to invoke
        :type controller_type: ControllerMetadata.ControllerType
        :return: Remediation output.
        :rtype: dict
        """
        with HostnameLoggingContext(self._context.hostname):
            logger.info("Running remediation workflow with desired spec.")
            remediation_output = RemediateResponse()
            remediation_output.status = RemediateStatus.SUCCESS
            try:
                self._invoke_workflow(
                    desired_state_spec, remediation_output, Operations.REMEDIATE, metadata_filter, controller_type
                )
            except Exception as e:
                logging.error(f"Exception in remediation workflow {e}")
                remediation_output.status = RemediateStatus.ERROR
                remediation_output.message = str(e)
            return remediation_output.to_dict()

    def _invoke_workflow(
        self,
        desired_state_spec: dict,
        output_response: OutputResponse,
        operation: Operations,
        metadata_filter: Callable[[ControllerMetadata], bool] = None,
        controller_type: ControllerMetadata.ControllerType = ControllerMetadata.ControllerType.COMPLIANCE,
    ):
        """Invokes the respective workflow based on the input operation specified.

        Response is returned in the provided output_response.

        :param desired_state_spec: The input desired state spec.
        :param output_response: Instance of OutputResponse class.
        :param operation: The operation to invoke.
        :param metadata_filter: Function used to filter controllers based on metadata.
        :type metadata_filter: Callable[[ControllerMetadata], bool]
        :param controller_type: Type of controller to invoke
        :type controller_type: ControllerMetadata.ControllerType
        """
        controller_operation = {
            ControllerMetadata.ControllerType.COMPLIANCE: ComplianceOperations,
            ControllerMetadata.ControllerType.CONFIGURATION: ConfigurationOperations,
        }[controller_type]
        workflow_response = controller_operation.operate(
            self._context,
            operation,
            input_values=desired_state_spec,
            metadata_filter=metadata_filter,
        )
        output_response.status = workflow_response.get(consts.STATUS)
        if operation == Operations.GET_CURRENT:
            output_response.result = workflow_response.get(consts.RESULT, {})
        else:
            output_response.changes = workflow_response.get(consts.RESULT, {})
        if consts.MESSAGE in workflow_response:
            output_response.message = workflow_response.get(consts.MESSAGE)
