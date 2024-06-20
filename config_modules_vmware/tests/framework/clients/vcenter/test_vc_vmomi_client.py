# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock
from mock import patch

from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient


class TestVcVmomiClient:

    @patch.object(VcVmomiClient, "connect")
    def test_retrieve_cluster_path(self, connect):
        # root datacenter
        root = MagicMock()
        root.name = "Datacenters"
        root.parent = None

        # datacenter
        datacenter = MagicMock()
        datacenter.name = "testDatacenter"
        datacenter.parent = root

        # folder under datacenter
        folder = MagicMock()
        folder.name = "testFolder"
        folder.parent = datacenter

        # host folder
        host_folder = MagicMock()
        host_folder.name = "host"
        host_folder.parent = folder

        # cluster
        cluster = MagicMock()
        cluster.name = "testCluster"
        cluster.parent = host_folder
        cluster._moId = "domain-1"

        with patch.object(VcVmomiClient, 'get_all_clusters', return_value=[cluster]):
            expected_cluster_path_moid_mapping = {'/testDatacenter/testFolder/testCluster': 'domain-1'}
            vc_vmomi_client = VcVmomiClient(hostname='hostname',
                                                  user='username',
                                                  pwd='password',
                                                  ssl_thumbprint='ssl_thumbprint',
                                                  saml_token='saml_token')
            cluster_path_moid_mapping = vc_vmomi_client.retrieve_cluster_path_moid_mapping()
            assert cluster_path_moid_mapping == expected_cluster_path_moid_mapping
