# Copyright 2024 Broadcom. All Rights Reserved.
import json

from mock import MagicMock

from config_modules_vmware.controllers.esxi.utils import cluster_config_utils
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.vcenter.vc_consts import VC_API_BASE
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Status
from config_modules_vmware.framework.utils import utils

class TestClusterConfigUtils:

    def setup_method(self):
        # VC API Base url
        self.mock_vc_host_name = "mock-vc.eng.vmware.com"
        self.vc_base_url = VC_API_BASE.format(self.mock_vc_host_name)

        self.mock_vc_rest_client = MagicMock()
        self.mock_vc_rest_client.get_base_url.return_value = self.vc_base_url

        self.mock_esxi_context = self.create_context_mock()
        self.mock_esxi_context.vc_rest_client.return_value = self.mock_vc_rest_client
        self.mock_esxi_context.hostname = self.mock_vc_host_name

        self.mock_cluster_moid = "domain-c9"
        self.mock_task_id = "ca65525c-b324-49e1-9e7e-008d08dfecb4:com.vmware.esx.settings.clusters.configuration"

    def create_context_mock(self):
        context_mock = MagicMock()
        context_mock.product_category = "esxi"
        return context_mock


    def test_success_compliant(self):
        task_response = json.loads('''
        {
            "parent": "",
            "cancelable": true,
            "end_time": "2024-11-08T19:39:57.399Z",
            "description": {
                "args": [],
                "default_message": "Task created by VMware vSphere Lifecycle Manager",
                "localized": "Task created by VMware vSphere Lifecycle Manager",
                "id": "com.vmware.vcIntegrity.lifecycle.Task.Description"
            },
            "target": {
                "id": "domain-c9",
                "type": "ClusterComputeResource"
            },
            "result": {
                "summary": {
                    "args": [],
                    "default_message": "All hosts in this cluster are compliant.",
                    "localized": "All hosts in this cluster are compliant.",
                    "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Summary.Compliant"
                },
                "cluster_status": "COMPLIANT",
                "failed_hosts": [],
                "hosts": [
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is in compliance with desired configuration.",
                                "localized": "Host is in compliance with desired configuration.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.CompliantHost"
                            },
                            "host_compliance": {
                                "status": "COMPLIANT"
                            },
                            "host_status": {
                                "start_time": "2024-11-08T19:39:46.487Z",
                                "end_time": "2024-11-08T19:39:57.311Z",
                                "notifications": {
                                    "warnings": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                            "time": "2024-11-08T19:39:48.858Z",
                                            "message": {
                                                "args": [],
                                                "default_message": "Host '10.192.60.248' is not in compliance with desired image of the cluster.",
                                                "localized": "Host '10.192.60.248' is not in compliance with desired image of the cluster.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                                "params": [
                                                    {
                                                        "value": {
                                                            "s": "10.192.60.248"
                                                        },
                                                        "key": "host"
                                                    }
                                                ]
                                            },
                                            "type": "WARNING"
                                        }
                                    ],
                                    "info": [
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.start",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:39:50.549Z",
                                            "message": {
                                                "args": [
                                                    "10.192.60.248"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.60.248' started.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.60.248' started.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.start"
                                            },
                                            "type": "INFO"
                                        },
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.complete",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:39:50.552Z",
                                            "message": {
                                                "args": [
                                                    "10.192.60.248"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.60.248' is complete.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.60.248' is complete.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.complete"
                                            },
                                            "type": "INFO"
                                        }
                                    ]
                                },
                                "status": "OK"
                            }
                        },
                        "key": "host-17"
                    },
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is in compliance with desired configuration.",
                                "localized": "Host is in compliance with desired configuration.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.CompliantHost"
                            },
                            "host_compliance": {
                                "status": "COMPLIANT"
                            },
                            "host_status": {
                                "start_time": "2024-11-08T19:39:46.508Z",
                                "end_time": "2024-11-08T19:39:57.357Z",
                                "notifications": {
                                    "warnings": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                            "time": "2024-11-08T19:39:48.601Z",
                                            "message": {
                                                "args": [],
                                                "default_message": "Host '10.192.48.91' is not in compliance with desired image of the cluster.",
                                                "localized": "Host '10.192.48.91' is not in compliance with desired image of the cluster.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                                "params": [
                                                    {
                                                        "value": {
                                                            "s": "10.192.48.91"
                                                        },
                                                        "key": "host"
                                                    }
                                                ]
                                            },
                                            "type": "WARNING"
                                        }
                                    ],
                                    "info": [
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.start",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:39:50.556Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.91"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.91' started.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.91' started.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.start"
                                            },
                                            "type": "INFO"
                                        },
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.complete",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:39:50.559Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.91"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.91' is complete.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.91' is complete.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.complete"
                                            },
                                            "type": "INFO"
                                        }
                                    ]
                                },
                                "status": "OK"
                            }
                        },
                        "key": "host-23"
                    },
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is in compliance with desired configuration.",
                                "localized": "Host is in compliance with desired configuration.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.CompliantHost"
                            },
                            "host_compliance": {
                                "status": "COMPLIANT"
                            },
                            "host_status": {
                                "start_time": "2024-11-08T19:39:46.527Z",
                                "end_time": "2024-11-08T19:39:57.349Z",
                                "notifications": {
                                    "warnings": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                            "time": "2024-11-08T19:39:48.502Z",
                                            "message": {
                                                "args": [],
                                                "default_message": "Host '10.192.48.214' is not in compliance with desired image of the cluster.",
                                                "localized": "Host '10.192.48.214' is not in compliance with desired image of the cluster.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                                "params": [
                                                    {
                                                        "value": {
                                                            "s": "10.192.48.214"
                                                        },
                                                        "key": "host"
                                                    }
                                                ]
                                            },
                                            "type": "WARNING"
                                        }
                                    ],
                                    "info": [
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.start",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:39:50.562Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.214"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.214' started.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.214' started.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.start"
                                            },
                                            "type": "INFO"
                                        },
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.complete",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:39:50.565Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.214"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.214' is complete.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.214' is complete.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.complete"
                                            },
                                            "type": "INFO"
                                        }
                                    ]
                                },
                                "status": "OK"
                            }
                        },
                        "key": "host-29"
                    }
                ],
                "non_compliant_hosts": [],
                "skipped_hosts": [],
                "commit": "config-commit-2",
                "end_time": "2024-11-08T19:39:57.371Z",
                "compliant_hosts": [
                    "host-17",
                    "host-23",
                    "host-29"
                ],
                "host_info": [
                    {
                        "value": {
                            "name": "10.192.60.248"
                        },
                        "key": "host-17"
                    },
                    {
                        "value": {
                            "name": "10.192.48.91"
                        },
                        "key": "host-23"
                    },
                    {
                        "value": {
                            "name": "10.192.48.214"
                        },
                        "key": "host-29"
                    }
                ],
                "software_commit": "1"
            },
            "start_time": "2024-11-08T19:39:45.987Z",
            "last_update_time": "2024-11-08T19:39:57.420Z",
            "service": "com.vmware.esx.settings.clusters.configuration",
            "progress": {
                "total": 100,
                "completed": 100,
                "message": {
                    "args": [],
                    "default_message": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "localized": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "id": "com.vmware.vcIntegrity.lifecycle.Task.Progress"
                }
            },
            "operation": "check_compliance$task",
            "user": "Administrator@VSPHERE.LOCAL",
            "notifications": {
                "warnings": [],
                "errors": [],
                "info": [
                    {
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Started",
                        "time": "2024-11-08T19:39:49.186Z",
                        "message": {
                            "args": [
                                "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                                "VALIDATE"
                            ],
                            "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' started 'VALIDATE' operation.",
                            "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' started 'VALIDATE' operation.",
                            "id": "com.vmware.vcIntegrity.lifecycle.plugin.Started"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.start",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:39:50.536Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Networking validation plugin on cluster 'cluster1' started.",
                            "localized": "Networking validation plugin on cluster 'cluster1' started.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.start"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.switches.start",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:39:50.541Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Validate DVS configurations for cluster 'cluster1' started.",
                            "localized": "Validate DVS configurations for cluster 'cluster1' started.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.switches.start"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.vmknics.start",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:39:50.545Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Validate dvportgroup of vmknics for cluster 'cluster1' started.",
                            "localized": "Validate dvportgroup of vmknics for cluster 'cluster1' started.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.vmknics.start"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.vmknics.complete",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:39:50.568Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Validate dvportgroup of vmknics for cluster 'cluster1' is complete.",
                            "localized": "Validate dvportgroup of vmknics for cluster 'cluster1' is complete.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.vmknics.complete"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.complete",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:39:50.572Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Networking validation plugin on cluster 'cluster1' is complete.",
                            "localized": "Networking validation plugin on cluster 'cluster1' is complete.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.complete"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Completed",
                        "time": "2024-11-08T19:39:50.587Z",
                        "message": {
                            "args": [
                                "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                                "VALIDATE"
                            ],
                            "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' successfully completed 'VALIDATE' operation.",
                            "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' successfully completed 'VALIDATE' operation.",
                            "id": "com.vmware.vcIntegrity.lifecycle.plugin.Completed"
                        },
                        "type": "INFO"
                    }
                ]
            },
            "status": "SUCCEEDED"
        }
        ''')
        expected_drift_response = {
            "result": {
                "schema_version": "1.0",
                "id": "ca65525c-b324-49e1-9e7e-008d08dfecb4",
                "name": "config_modules_vmware.controllers.esxi.cluster_config",
                "timestamp": "2024-11-08T19:39:57.371Z",
                "description": "All hosts in this cluster are compliant.",
                "status": Status.COMPLIANT,
                "target": {
                    "hostname": "mock-vc.eng.vmware.com",
                    "type": BaseContext.ProductEnum.VCENTER,
                    "id": "domain-c9"
                }
            },
            "status": ComplianceStatus.COMPLIANT,
        }

        drift_response = cluster_config_utils.transform_to_drift_schema(self.mock_esxi_context, self.mock_cluster_moid, self.mock_task_id, task_response, [])
        assert drift_response == expected_drift_response

    def test_success_non_compliant(self):
        task_response = json.loads('''
        {
            "parent": "",
            "cancelable": true,
            "end_time": "2024-11-08T19:40:44.651Z",
            "description": {
                "args": [],
                "default_message": "Task created by VMware vSphere Lifecycle Manager",
                "localized": "Task created by VMware vSphere Lifecycle Manager",
                "id": "com.vmware.vcIntegrity.lifecycle.Task.Description"
            },
            "target": {
                "id": "domain-c9",
                "type": "ClusterComputeResource"
            },
            "result": {
                "summary": {
                    "args": [
                        "3",
                        "0"
                    ],
                    "default_message": "3 hosts are out of compliance and 0 hosts have unknown status.",
                    "localized": "3 hosts are out of compliance and 0 hosts have unknown status.",
                    "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Summary.NotCompliant"
                },
                "cluster_status": "NOT_COMPLIANT",
                "failed_hosts": [],
                "hosts": [
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is out of compliance with desired configuration.",
                                "localized": "Host is out of compliance with desired configuration.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.NonCompliantHost"
                            },
                            "host_compliance": {
                                "compliance_info": {
                                    "sets": [
                                        {
                                            "path": "/profile/esx/security/settings/account_lock_failures",
                                            "current": "0",
                                            "target": "100"
                                        }
                                    ]
                                },
                                "status": "NON_COMPLIANT"
                            },
                            "host_status": {
                                "start_time": "2024-11-08T19:40:33.844Z",
                                "end_time": "2024-11-08T19:40:44.423Z",
                                "notifications": {
                                    "warnings": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                            "time": "2024-11-08T19:40:36.003Z",
                                            "message": {
                                                "args": [],
                                                "default_message": "Host '10.192.60.248' is not in compliance with desired image of the cluster.",
                                                "localized": "Host '10.192.60.248' is not in compliance with desired image of the cluster.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                                "params": [
                                                    {
                                                        "value": {
                                                            "s": "10.192.60.248"
                                                        },
                                                        "key": "host"
                                                    }
                                                ]
                                            },
                                            "type": "WARNING"
                                        }
                                    ],
                                    "info": [
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.start",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:40:37.675Z",
                                            "message": {
                                                "args": [
                                                    "10.192.60.248"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.60.248' started.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.60.248' started.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.start"
                                            },
                                            "type": "INFO"
                                        },
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.complete",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:40:37.679Z",
                                            "message": {
                                                "args": [
                                                    "10.192.60.248"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.60.248' is complete.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.60.248' is complete.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.complete"
                                            },
                                            "type": "INFO"
                                        }
                                    ]
                                },
                                "status": "OK"
                            }
                        },
                        "key": "host-17"
                    },
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is out of compliance with desired configuration.",
                                "localized": "Host is out of compliance with desired configuration.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.NonCompliantHost"
                            },
                            "host_compliance": {
                                "compliance_info": {
                                    "sets": [
                                        {
                                            "path": "/profile/esx/security/settings/account_lock_failures",
                                            "current": "0",
                                            "target": "100"
                                        }
                                    ]
                                },
                                "status": "NON_COMPLIANT"
                            },
                            "host_status": {
                                "start_time": "2024-11-08T19:40:33.869Z",
                                "end_time": "2024-11-08T19:40:44.618Z",
                                "notifications": {
                                    "warnings": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                            "time": "2024-11-08T19:40:35.911Z",
                                            "message": {
                                                "args": [],
                                                "default_message": "Host '10.192.48.91' is not in compliance with desired image of the cluster.",
                                                "localized": "Host '10.192.48.91' is not in compliance with desired image of the cluster.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                                "params": [
                                                    {
                                                        "value": {
                                                            "s": "10.192.48.91"
                                                        },
                                                        "key": "host"
                                                    }
                                                ]
                                            },
                                            "type": "WARNING"
                                        }
                                    ],
                                    "info": [
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.start",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:40:37.683Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.91"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.91' started.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.91' started.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.start"
                                            },
                                            "type": "INFO"
                                        },
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.complete",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:40:37.687Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.91"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.91' is complete.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.91' is complete.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.complete"
                                            },
                                            "type": "INFO"
                                        }
                                    ]
                                },
                                "status": "OK"
                            }
                        },
                        "key": "host-23"
                    },
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is out of compliance with desired configuration.",
                                "localized": "Host is out of compliance with desired configuration.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.NonCompliantHost"
                            },
                            "host_compliance": {
                                "compliance_info": {
                                    "sets": [
                                        {
                                            "path": "/profile/esx/security/settings/account_lock_failures",
                                            "current": "0",
                                            "target": "100"
                                        }
                                    ]
                                },
                                "status": "NON_COMPLIANT"
                            },
                            "host_status": {
                                "start_time": "2024-11-08T19:40:33.892Z",
                                "end_time": "2024-11-08T19:40:44.466Z",
                                "notifications": {
                                    "warnings": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                            "time": "2024-11-08T19:40:35.731Z",
                                            "message": {
                                                "args": [],
                                                "default_message": "Host '10.192.48.214' is not in compliance with desired image of the cluster.",
                                                "localized": "Host '10.192.48.214' is not in compliance with desired image of the cluster.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.configuration.ImageNonCompliant",
                                                "params": [
                                                    {
                                                        "value": {
                                                            "s": "10.192.48.214"
                                                        },
                                                        "key": "host"
                                                    }
                                                ]
                                            },
                                            "type": "WARNING"
                                        }
                                    ],
                                    "info": [
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.start",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:40:37.690Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.214"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.214' started.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.214' started.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.start"
                                            },
                                            "type": "INFO"
                                        },
                                        {
                                            "id": "com.vmware.esx.network.host.validate.vmknics.complete",
                                            "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                                            "time": "2024-11-08T19:40:37.693Z",
                                            "message": {
                                                "args": [
                                                    "10.192.48.214"
                                                ],
                                                "default_message": "Validate dvportgroup of vmknics for host '10.192.48.214' is complete.",
                                                "localized": "Validate dvportgroup of vmknics for host '10.192.48.214' is complete.",
                                                "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.host.validate.vmknics.complete"
                                            },
                                            "type": "INFO"
                                        }
                                    ]
                                },
                                "status": "OK"
                            }
                        },
                        "key": "host-29"
                    }
                ],
                "non_compliant_hosts": [
                    "host-17",
                    "host-23",
                    "host-29"
                ],
                "skipped_hosts": [],
                "commit": "config-commit-3",
                "end_time": "2024-11-08T19:40:44.631Z",
                "compliant_hosts": [],
                "host_info": [
                    {
                        "value": {
                            "name": "10.192.60.248"
                        },
                        "key": "host-17"
                    },
                    {
                        "value": {
                            "name": "10.192.48.91"
                        },
                        "key": "host-23"
                    },
                    {
                        "value": {
                            "name": "10.192.48.214"
                        },
                        "key": "host-29"
                    }
                ],
                "software_commit": "1"
            },
            "start_time": "2024-11-08T19:40:33.332Z",
            "last_update_time": "2024-11-08T19:40:44.671Z",
            "service": "com.vmware.esx.settings.clusters.configuration",
            "progress": {
                "total": 100,
                "completed": 100,
                "message": {
                    "args": [],
                    "default_message": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "localized": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "id": "com.vmware.vcIntegrity.lifecycle.Task.Progress"
                }
            },
            "operation": "check_compliance$task",
            "user": "Administrator@VSPHERE.LOCAL",
            "notifications": {
                "warnings": [],
                "errors": [],
                "info": [
                    {
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Started",
                        "time": "2024-11-08T19:40:36.313Z",
                        "message": {
                            "args": [
                                "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                                "VALIDATE"
                            ],
                            "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' started 'VALIDATE' operation.",
                            "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' started 'VALIDATE' operation.",
                            "id": "com.vmware.vcIntegrity.lifecycle.plugin.Started"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.start",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:40:37.648Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Networking validation plugin on cluster 'cluster1' started.",
                            "localized": "Networking validation plugin on cluster 'cluster1' started.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.start"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.switches.start",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:40:37.659Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Validate DVS configurations for cluster 'cluster1' started.",
                            "localized": "Validate DVS configurations for cluster 'cluster1' started.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.switches.start"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.vmknics.start",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:40:37.667Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Validate dvportgroup of vmknics for cluster 'cluster1' started.",
                            "localized": "Validate dvportgroup of vmknics for cluster 'cluster1' started.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.vmknics.start"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.vmknics.complete",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:40:37.697Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Validate dvportgroup of vmknics for cluster 'cluster1' is complete.",
                            "localized": "Validate dvportgroup of vmknics for cluster 'cluster1' is complete.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.vmknics.complete"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.esx.network.cluster.validate.complete",
                        "originator": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]",
                        "time": "2024-11-08T19:40:37.701Z",
                        "message": {
                            "args": [
                                "cluster1"
                            ],
                            "default_message": "Networking validation plugin on cluster 'cluster1' is complete.",
                            "localized": "Networking validation plugin on cluster 'cluster1' is complete.",
                            "id": "ext[com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre]com.vmware.esx.network.cluster.validate.complete"
                        },
                        "type": "INFO"
                    },
                    {
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Completed",
                        "time": "2024-11-08T19:40:37.717Z",
                        "message": {
                            "args": [
                                "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                                "VALIDATE"
                            ],
                            "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' successfully completed 'VALIDATE' operation.",
                            "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' successfully completed 'VALIDATE' operation.",
                            "id": "com.vmware.vcIntegrity.lifecycle.plugin.Completed"
                        },
                        "type": "INFO"
                    }
                ]
            },
            "status": "SUCCEEDED"
        }
        ''')
        expected_drift_response = {
            "result": {
                "schema_version": "1.0",
                "id": "ca65525c-b324-49e1-9e7e-008d08dfecb4",
                "name": "config_modules_vmware.controllers.esxi.cluster_config",
                "timestamp": "2024-11-08T19:40:44.631Z",
                "description": "3 hosts are out of compliance and 0 hosts have unknown status.",
                "status": Status.NON_COMPLIANT,
                "target": {
                    "hostname": "mock-vc.eng.vmware.com",
                    "type": BaseContext.ProductEnum.VCENTER,
                    "id": "domain-c9"
                }
            },
            "status": ComplianceStatus.NON_COMPLIANT,
        }

        drift_response = cluster_config_utils.transform_to_drift_schema(self.mock_esxi_context, self.mock_cluster_moid, self.mock_task_id, task_response, [])
        assert drift_response == expected_drift_response

    def test_task_failed(self):
        task_response = json.loads('''
        {
            "parent": "",
            "cancelable": true,
            "end_time": "2024-11-06T18:41:20.147Z",
            "description": {
                "args": [],
                "default_message": "Task created by VMware vSphere Lifecycle Manager",
                "localized": "Task created by VMware vSphere Lifecycle Manager",
                "id": "com.vmware.vcIntegrity.lifecycle.Task.Description"
            },
            "error": {
                "@class": "com.vmware.vapi.std.errors.internal_server_error",
                "error_type": "INTERNAL_SERVER_ERROR",
                "messages": [
                    {
                        "args": [
                            "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                            "VALIDATE"
                        ],
                        "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation.",
                        "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation.",
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Failed"
                    }
                ]
            },
            "target": {
                "id": "domain-c9",
                "type": "ClusterComputeResource"
            },
            "result": {
                "summary": {
                    "args": [],
                    "default_message": "Internal error occurred. Check compliance is skipped.",
                    "localized": "Internal error occurred. Check compliance is skipped.",
                    "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.InternalError"
                },
                "cluster_status": "NOT_COMPLIANT",
                "failed_hosts": [],
                "hosts": [
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is disconnected. Check compliance is skipped.",
                                "localized": "Host is disconnected. Check compliance is skipped.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.Disconnected"
                            },
                            "host_status": {
                                "start_time": "2024-11-06T18:41:18.819Z",
                                "end_time": "2024-11-06T18:41:18.825Z",
                                "notifications": {
                                    "errors": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected",
                                            "time": "2024-11-06T18:41:18.825Z",
                                            "message": {
                                                "args": [
                                                    "10.162.82.221"
                                                ],
                                                "default_message": "Host 10.162.82.221 is disconnected. Connect the host and retry.",
                                                "localized": "Host 10.162.82.221 is disconnected. Connect the host and retry.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected"
                                            },
                                            "resolution": {
                                                "args": [
                                                    "10.162.82.221"
                                                ],
                                                "default_message": "Reconnect the host '10.162.82.221' and try again.",
                                                "localized": "Reconnect the host '10.162.82.221' and try again.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected.GenericResolution"
                                            }
                                        }
                                    ]
                                },
                                "status": "SKIPPED"
                            }
                        },
                        "key": "host-17"
                    },
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is disconnected. Check compliance is skipped.",
                                "localized": "Host is disconnected. Check compliance is skipped.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.Disconnected"
                            },
                            "host_status": {
                                "start_time": "2024-11-06T18:41:18.838Z",
                                "end_time": "2024-11-06T18:41:18.842Z",
                                "notifications": {
                                    "errors": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected",
                                            "time": "2024-11-06T18:41:18.842Z",
                                            "message": {
                                                "args": [
                                                    "10.162.86.183"
                                                ],
                                                "default_message": "Host 10.162.86.183 is disconnected. Connect the host and retry.",
                                                "localized": "Host 10.162.86.183 is disconnected. Connect the host and retry.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected"
                                            },
                                            "resolution": {
                                                "args": [
                                                    "10.162.86.183"
                                                ],
                                                "default_message": "Reconnect the host '10.162.86.183' and try again.",
                                                "localized": "Reconnect the host '10.162.86.183' and try again.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected.GenericResolution"
                                            }
                                        }
                                    ]
                                },
                                "status": "SKIPPED"
                            }
                        },
                        "key": "host-23"
                    },
                    {
                        "value": {
                            "summary": {
                                "args": [],
                                "default_message": "Host is disconnected. Check compliance is skipped.",
                                "localized": "Host is disconnected. Check compliance is skipped.",
                                "id": "com.vmware.vcIntegrity.lifecycle.ConfigurationCheckComplianceTask.Host.Summary.Disconnected"
                            },
                            "host_status": {
                                "start_time": "2024-11-06T18:41:18.854Z",
                                "end_time": "2024-11-06T18:41:18.857Z",
                                "notifications": {
                                    "errors": [
                                        {
                                            "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected",
                                            "time": "2024-11-06T18:41:18.857Z",
                                            "message": {
                                                "args": [
                                                    "10.162.86.67"
                                                ],
                                                "default_message": "Host 10.162.86.67 is disconnected. Connect the host and retry.",
                                                "localized": "Host 10.162.86.67 is disconnected. Connect the host and retry.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected"
                                            },
                                            "resolution": {
                                                "args": [
                                                    "10.162.86.67"
                                                ],
                                                "default_message": "Reconnect the host '10.162.86.67' and try again.",
                                                "localized": "Reconnect the host '10.162.86.67' and try again.",
                                                "id": "com.vmware.vcIntegrity.lifecycle.host.disconnected.GenericResolution"
                                            }
                                        }
                                    ]
                                },
                                "status": "SKIPPED"
                            }
                        },
                        "key": "host-29"
                    }
                ],
                "non_compliant_hosts": [],
                "skipped_hosts": [
                    "host-17",
                    "host-23",
                    "host-29"
                ],
                "commit": "config-commit-3",
                "end_time": "2024-11-06T18:41:20.116Z",
                "compliant_hosts": [],
                "host_info": [
                    {
                        "value": {
                            "name": "10.162.82.221"
                        },
                        "key": "host-17"
                    },
                    {
                        "value": {
                            "name": "10.162.86.183"
                        },
                        "key": "host-23"
                    },
                    {
                        "value": {
                            "name": "10.162.86.67"
                        },
                        "key": "host-29"
                    }
                ],
                "software_commit": "2"
            },
            "start_time": "2024-11-06T18:41:18.246Z",
            "last_update_time": "2024-11-06T18:41:20.171Z",
            "service": "com.vmware.esx.settings.clusters.configuration",
            "progress": {
                "total": 100,
                "completed": 40,
                "message": {
                    "args": [],
                    "default_message": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "localized": "Current progress for task created by VMware vSphere Lifecycle Manager",
                    "id": "com.vmware.vcIntegrity.lifecycle.Task.Progress"
                }
            },
            "operation": "check_compliance$task",
            "user": "Administrator@VSPHERE.LOCAL",
            "notifications": {
                "warnings": [],
                "errors": [
                    {
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Failed",
                        "time": "2024-11-06T18:41:19.430Z",
                        "message": {
                            "args": [
                                "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                                "VALIDATE"
                            ],
                            "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation.",
                            "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation.",
                            "id": "com.vmware.vcIntegrity.lifecycle.plugin.Failed"
                        },
                        "type": "ERROR"
                    }
                ],
                "info": [
                    {
                        "id": "com.vmware.vcIntegrity.lifecycle.plugin.Started",
                        "time": "2024-11-06T18:41:19.326Z",
                        "message": {
                            "args": [
                                "/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre",
                                "VALIDATE"
                            ],
                            "default_message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' started 'VALIDATE' operation.",
                            "localized": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' started 'VALIDATE' operation.",
                            "id": "com.vmware.vcIntegrity.lifecycle.plugin.Started"
                        },
                        "type": "INFO"
                    }
                ]
            },
            "status": "FAILED"
        }
        ''')
        expected_drift_response = {
            "message": {
                "schema_version": "1.0",
                "id": "ca65525c-b324-49e1-9e7e-008d08dfecb4",
                "name": "config_modules_vmware.controllers.esxi.cluster_config",
                "timestamp": "2024-11-08T22:25:03.711957",
                "description": "ESXi cluster compliance check",
                "status": Status.FAILED,
                "target": {
                    "hostname": "mock-vc.eng.vmware.com",
                    "type": BaseContext.ProductEnum.VCENTER,
                    "id": "domain-c9"
                },
                "errors": [
                    {
                        "timestamp": "2024-11-08T22:25:03.711957",
                        "error": {
                            "message": "The vSphere Configuration Plugin '/storage/updatemgr/plugins/prod/com.vmware.vcIntegrity/8.0.3.24364488/network_group/network_pre' failed to perform 'VALIDATE' operation."
                        },
                        "source": {
                            "server": "mock-vc.eng.vmware.com",
                            "type": BaseContext.ProductEnum.VCENTER,
                            "endpoint": "https://mock-vc.eng.vmware.com/rest/cis/tasks/ca65525c-b324-49e1-9e7e-008d08dfecb4:com.vmware.esx.settings.clusters.configuration"
                        }
                    }
                ]
            },
            "status": ComplianceStatus.FAILED,
        }

        utils.get_current_time = MagicMock()
        utils.get_current_time.return_value = "2024-11-08T22:25:03.711957"

        drift_response = cluster_config_utils.transform_to_drift_schema(self.mock_esxi_context, self.mock_cluster_moid, self.mock_task_id, task_response, [])
        assert drift_response == expected_drift_response
