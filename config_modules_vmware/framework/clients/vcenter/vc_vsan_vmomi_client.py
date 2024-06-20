# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import ssl
from enum import Enum
from urllib.request import urlopen
from xml.dom import minidom  # nosec

from pyVmomi import SoapStubAdapter
from pyVmomi import vim
from pyVmomi import VmomiSupport
from pyVmomi.VmomiSupport import publicVersions  # pylint: disable=E0401

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.clients.vcenter.dependencies.vsan_management import vsanmgmtObjects
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VmomiClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


class VsanManagementObjectsEnum(Enum):
    """
    VSAN Management objects Enum
    """

    VSAN_DISK_MANAGEMENT_SYSTEM = "vsan-disk-management-system"
    VSAN_STRETCHED_CLUSTER_SYSTEM = "vsan-stretched-cluster-system"
    VSAN_CLUSTER_CONFIG_SYSTEM = "vsan-cluster-config-system"
    VSAN_PERFORMANCE_MANAGER = "vsan-performance-manager"
    VSAN_CLUSTER_HEALTH_SYSTEM = "vsan-cluster-health-system"
    VSAN_UPGRADE_SYSTEMEX = "vsan-upgrade-systemex"
    VSAN_CLUSTER_SPACE_REPORT_SYSTEM = "vsan-cluster-space-report-system"
    VSAN_CLUSTER_OBJECT_SYSTEM = "vsan-cluster-object-system"
    VSAN_ISCSI_TARGET_SYSTEM = "vsan-cluster-iscsi-target-system"


class VcVsanVmomiClient:
    """
    Class that provides vSAN Mob related methods.
    """

    def __init__(
        self,
        hostname,
        user,
        pwd,
        port=443,
        ssl_thumbprint=None,
        saml_token=None,
        version=publicVersions.GetName("vim"),
        verify_ssl=True,
    ):
        """
        Initializes a client connection to the vCenter Server.

        :param hostname: vCenter Server hostname.
        :param user: vCenter Server admin user.
        :param pwd: vCenter Server admin user password.
        :param port: vCenter Server HTTPs port.
        :param ssl_thumbprint: vCenter Server SSL thumbprint.
        :param saml_token: SAML token used to connect to vCenter.
        :param version: vmodl version.
        :param verify_ssl: Flag to enable/disable SSL verification.
        """
        self.port = port
        self.vc_name = hostname
        self.user = user
        self.pwd = pwd
        self.ssl_thumbprint = ssl_thumbprint
        self.saml_token = saml_token
        self.version = version
        self.verify_ssl = verify_ssl
        # vSAN bindings, using it this way so pre-commit doesn't complain of un-used vsanmgmtObjects import
        self.vsan_mgmt_obj = vsanmgmtObjects
        self.si = None
        self.content = None
        self.stub = None
        self.ssl_ctx = None
        self.vmomi_client = None
        self.vc_rest_client = None
        self.set_ssl_context()
        self.connect(version)

    def set_ssl_context(self):
        """
        Set SSL context based on SSL thumbprint or SAML token.
        """
        self.ssl_ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
        if not self.verify_ssl:
            logger.info("Skipping SSL certificate verification")
            self.ssl_ctx.verify_mode = ssl.CERT_NONE
            self.ssl_thumbprint = None
        elif self.ssl_thumbprint or self.saml_token:
            logger.info("Verifying without server certificates")
            self.ssl_ctx.verify_mode = ssl.CERT_NONE
        else:
            logger.info("Verifying server certificates")
            self.ssl_ctx.verify_mode = ssl.CERT_REQUIRED
            self.ssl_ctx.load_verify_locations(capath=consts.SSL_VERIFY_CA_PATH)

    def connect(self, version):
        """
        Connects to the vCenter Server.

        :param version: vmodl version.
        """
        logger.info("Connecting to the vCenter Server")
        self.vmomi_client = VmomiClient(
            hostname=self.vc_name,
            port=self.port,
            ssl_context=self.ssl_ctx,
            get_session_obj_for_child_func=VcVmomiClient.get_session_obj,
            session_login_func=VcVmomiClient.generate_login_method(username=self.user, password=self.pwd),
            session_logout_func=VcVmomiClient.generate_logout_method(vc_name=self.vc_name),
            version=version,
            saml_token=self.saml_token,
            thumbprint=self.ssl_thumbprint,
        )
        self.vmomi_client.connect()
        self.si = self.vmomi_client.get_managed_object(vim.ServiceInstance, "ServiceInstance")
        try:
            self.content = self.si.RetrieveContent()
        except Exception as e:
            logger.error(str(e))
            raise Exception("Failed to connect to VC server") from e

        self.stub = self.si._stub
        logger.info("VC session established")

    def disconnect(self):
        """
        Disconnect the VC service instance.
        :return: None
        """
        self.vmomi_client.disconnect()

    def get_vsan_vc_stub(self):
        """
        Constructs a stub for vSAN API access using vCenter sessions from existing stubs.

        :return: vSAN API stub.
        """
        # Connect to vSAN service endpoint
        logger.info("Connecting to the vSAN service endpoint")
        vsan_stub = SoapStubAdapter(
            host=self.vc_name,
            path=vc_consts.VSAN_API_VC_SERVICE_ENDPOINT,
            version=self.get_latest_vsan_vmodl_version(),
            sslContext=self.ssl_ctx,
        )
        # Set cookie
        vsan_stub.cookie = self.stub.soapStub.cookie
        return vsan_stub

    def get_all_vsan_enabled_clusters(self):
        """
            Get all vSAN enabled clusters in Datacenter
        :return:
        """
        # get view manager
        view_manager = self.content.viewManager
        # Root folder
        root_folder = self.content.rootFolder

        # Create a view with all clusters
        cluster_view = view_manager.CreateContainerView(root_folder, [vim.ClusterComputeResource], True).view

        # Filter vSAN enabled clusters and store their MORefs
        vsan_enabled_clusters = [
            cluster
            for cluster in cluster_view
            if hasattr(cluster.configurationEx, "vsanConfigInfo") and cluster.configurationEx.vsanConfigInfo.enabled
        ]

        return vsan_enabled_clusters

    def get_first_vsan_enabled_cluster(self):
        """
        Gets the first cluster in the Datacenter.

        :return: First cluster.
        """
        # Get view manager
        view_manager = self.content.viewManager
        # Create a view for ClusterComputeResource type
        clusters = view_manager.CreateContainerView(self.content.rootFolder, [vim.ClusterComputeResource], True).view
        # return first vSAN enabled cluster
        vsan_enabled_cluster = next(
            (
                cluster
                for cluster in clusters
                if hasattr(cluster.configurationEx, "vsanConfigInfo") and cluster.configurationEx.vsanConfigInfo.enabled
            ),
            None,
        )

        return vsan_enabled_cluster if vsan_enabled_cluster else None

    def get_vsan_vc_mos_by_type(self, vsan_object_enum):
        """
        Gets VSAN VC managed object by type.

        :param vsan_object_enum: Enum value representing the VSAN object type.
        :return: VSAN VC managed object.
        """
        # get vsan VC stub
        vsan_stub = self.get_vsan_vc_stub()
        # Enum object mapping for vSAN system
        vsan_object_mapping = {
            VsanManagementObjectsEnum.VSAN_DISK_MANAGEMENT_SYSTEM: vim.cluster.VsanVcDiskManagementSystem,
            VsanManagementObjectsEnum.VSAN_STRETCHED_CLUSTER_SYSTEM: vim.cluster.VsanVcStretchedClusterSystem,
            VsanManagementObjectsEnum.VSAN_CLUSTER_CONFIG_SYSTEM: vim.cluster.VsanVcClusterConfigSystem,
            VsanManagementObjectsEnum.VSAN_PERFORMANCE_MANAGER: vim.cluster.VsanPerformanceManager,
            VsanManagementObjectsEnum.VSAN_CLUSTER_HEALTH_SYSTEM: vim.cluster.VsanVcClusterHealthSystem,
            VsanManagementObjectsEnum.VSAN_UPGRADE_SYSTEMEX: vim.VsanUpgradeSystemEx,
            VsanManagementObjectsEnum.VSAN_CLUSTER_SPACE_REPORT_SYSTEM: vim.cluster.VsanSpaceReportSystem,
            VsanManagementObjectsEnum.VSAN_CLUSTER_OBJECT_SYSTEM: vim.cluster.VsanObjectSystem,
            VsanManagementObjectsEnum.VSAN_ISCSI_TARGET_SYSTEM: vim.cluster.VsanIscsiTargetSystem,
        }
        # get vSAN object class from mapping
        vsan_object_class = vsan_object_mapping.get(vsan_object_enum)
        if vsan_object_class:
            return vsan_object_class(vsan_object_enum.value, vsan_stub)
        else:
            raise ValueError(f"Unsupported VSAN object: {vsan_object_enum}")

    def get_latest_vsan_vmodl_version(self):
        """
        Gets the VMODL version by checking the existence of vSAN namespace.
        :return: VMODL version.
        """
        try:
            logger.info("Getting vSAN VMODL version")
            vsan_vmodl_url = vc_consts.VSAN_VMODL_URL.format(self.vc_name)
            # Adding ssl context
            if hasattr(ssl, "_create_unverified_context") and hasattr(ssl, "_create_default_https_context"):
                ssl._create_default_https_context = ssl._create_unverified_context
            xml_doc = minidom.parse(urlopen(vsan_vmodl_url, timeout=30))  # nosec
            for element in xml_doc.getElementsByTagName("name"):
                if element.firstChild.nodeValue == "urn:vsan":
                    return VmomiSupport.newestVersions.Get("vsan")
            return VmomiSupport.newestVersions.Get("vim")
        except Exception as e:
            logger.error(str(e))
            return VmomiSupport.newestVersions.Get("vim")

    def get_vsan_cluster_health_config_for_cluster(self, cluster_ref):
        """
        Gets vSAN cluster health configuration for the first cluster.
        :return: vSAN cluster health configuration.
        """
        logger.info(f"Retrieving vSAN cluster health config for {cluster_ref.name}")
        # Get vSAN cluster health system
        vsan_health_system = self.get_vsan_vc_mos_by_type(VsanManagementObjectsEnum.VSAN_CLUSTER_HEALTH_SYSTEM)
        # Query vSAN Cluster health config for cluster
        vsan_health_config = vsan_health_system.QueryVsanClusterHealthConfig(cluster_ref)
        return vsan_health_config

    def get_vsan_proxy_config_for_cluster(self, cluster_ref):
        """
        Gets vSAN telemetry proxy configuration.
        :return: vSAN telemetry proxy configuration.
        """
        logger.info(f"Retrieving vSAN telemetry proxy config for {cluster_ref.name}")
        # Get vSAN Cluster health config for cluster
        vsan_cluster_health_config = self.get_vsan_cluster_health_config_for_cluster(cluster_ref)
        telemetry_proxy_config = None

        if hasattr(vsan_cluster_health_config, "vsanTelemetryProxy"):
            # Get vSAN telemetry proxy config
            proxy_config = vsan_cluster_health_config.vsanTelemetryProxy
            telemetry_proxy_config = {"host": proxy_config.host, "port": proxy_config.port, "user": proxy_config.user}
            # get internet access enablement config
            internet_access_config = self.get_vsan_config_by_key_for_cluster("enableinternetaccess", cluster_ref)
            if not internet_access_config:
                raise Exception("Unable to get vSAN internet access enablement config")
            telemetry_proxy_config["internet_access_enabled"] = (
                True if internet_access_config.value == "true" else False
            )
        return telemetry_proxy_config

    def get_vsan_config_by_key_for_cluster(self, key, cluster_ref):
        """
        Gets vSAN configuration by key for the given cluster.
        :param cluster_ref:
        :param key: Configuration key.
        :return: vSAN health configuration.
        """
        logger.info(f"Retrieving vSAN config {key} for cluster {cluster_ref.name}")
        # Get vSAN Cluster health config
        vsan_cluster_health_config = self.get_vsan_cluster_health_config_for_cluster(cluster_ref)

        # Get all key:value configurations for vSAN cluster health system
        if hasattr(vsan_cluster_health_config, "configs"):
            vsan_cluster_health_configs = vsan_cluster_health_config.configs
            # return config_obj if key exists
            for config_obj in vsan_cluster_health_configs:
                if config_obj.key == key:
                    return config_obj
        logger.info(f"Unable to get vSAN config {key}")

    def get_vsan_health_system(self):
        """
        Get vSAN health system.
        :return:
        """
        logger.info("Retrieving vSAN health system")
        vsan_health_system = self.get_vsan_vc_mos_by_type(VsanManagementObjectsEnum.VSAN_CLUSTER_HEALTH_SYSTEM)
        return vsan_health_system

    def get_vsan_cluster_config_system(self):
        """Gets vSAN cluster configuration system.

        :return: vSAN cluster config system.
        """
        vsan_cluster_config_system = self.get_vsan_vc_mos_by_type(VsanManagementObjectsEnum.VSAN_CLUSTER_CONFIG_SYSTEM)
        logger.info(f"Retrieved vSAN cluster config system {vsan_cluster_config_system}")
        return vsan_cluster_config_system

    def convert_vsan_to_vc_task(self, vsan_task):
        """Convert a vSAN Task to a Task MO binding to vCenter service.

        :param vsan_task:
        :return: vc_task
        """
        vc_task = vim.Task(vsan_task._GetMoId(), self.stub)
        logger.info(f"Converted vSAN task to VC task {vc_task}")
        return vc_task

    def get_vsan_iscsi_targets_for_cluster(self):
        """
        Gets vSAN cluster iscsi targets for the cluster.
        :return: vSAN cluster iscsi targets object.
        """
        # Get vSAN cluster iscsi targets
        return self.get_vsan_vc_mos_by_type(VsanManagementObjectsEnum.VSAN_ISCSI_TARGET_SYSTEM)

    def get_vsan_iscsi_targets_config_for_cluster(self, cluster_ref):
        """
        Gets vSAN cluster iscsi targets configuration for the cluster.
        :return: vSAN cluster iscsi targets configuration.
        """
        # Get vSAN cluster iscsi targets service config from vsan cluster config
        vsan_cluster_config_system = self.get_vsan_vc_mos_by_type(VsanManagementObjectsEnum.VSAN_CLUSTER_CONFIG_SYSTEM)
        return vsan_cluster_config_system.VsanClusterGetConfig(cluster_ref).iscsiConfig

    def get_vsan_iscsi_targets_auth_type_for_cluster(self, cluster_ref):
        """
        Gets vSAN cluster iscsi targets auth type configuration for the cluster.
        :return: vSAN cluster iscsi targets auth type.
        """
        # Get vSAN cluster iscsi targets configuration
        vsan_iscsi_targets_config = self.get_vsan_iscsi_targets_config_for_cluster(cluster_ref)
        default_config = vsan_iscsi_targets_config.defaultConfig
        if default_config:
            return default_config.iscsiTargetAuthSpec.authType
        return None

    def is_vsan_iscsi_targets_enabled_for_cluster(self, cluster_ref):
        """
        Gets vSAN cluster iscsi targets auth type configuration for the cluster.
        :return: vSAN cluster iscsi targets auth type.
        """
        # Get vSAN cluster iscsi targets configuration
        vsan_iscsi_targets_config = self.get_vsan_iscsi_targets_config_for_cluster(cluster_ref)
        return vsan_iscsi_targets_config.enabled
