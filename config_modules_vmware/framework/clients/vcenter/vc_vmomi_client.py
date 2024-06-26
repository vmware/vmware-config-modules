#!/usr/bin/env python
# Copyright 2024 Broadcom. All Rights Reserved.
"""
Implementation of the Vc drivers to perform hostConfig
operations.
"""
import logging
import ssl
import time
from threading import Lock

from pyVim.connect import Disconnect  # pylint: disable=E0401
from pyVmomi import vim  # pylint: disable=E0401
from pyVmomi.VmomiSupport import publicVersions  # pylint: disable=E0401

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.common.vmomi_client import VmomiClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.services.config import Config

# Set up logger
logger = LoggerAdapter(logging.getLogger(__name__))


class VcVmomiClient(object):
    """
    Class that provides VC Services.
    """

    def __init__(
        self,
        hostname,
        user,
        pwd,
        port=443,
        ssl_thumbprint=None,
        version=publicVersions.GetName("vim"),
        saml_token=None,
        verify_ssl=True,
    ):
        """
        Establishes a client connection to the passed vCenter Server.

        :type hostname: :class:'str'
        :param hostname: vCenter Server hostname.
        :type user: :class:'str'
        :param user: vCenter Server admin user
        :type pwd: :class:'str'
        :param pwd: vCenter Server admin user password.
        :type port: :class:'str'
        :param port: vCenter Server HTTPs port
        :type ssl_thumbprint: :class:'str'
        :param ssl_thumbprint: vCenter Server SSL thumbprint.
        :param version: vmodl version. e.g., 'cis.license.version.version2': str
        :type version: :class:'str'
        :param saml_token: SAML token used to connect to vCenter
        :type saml_token: :class:'str'
        :param verify_ssl: Flag to enable ssl verification
        :type verify_ssl: :class:'boolean'
        :return: None
        """
        self.si = None
        self.content = None
        self.port = port
        self.vc_name = hostname
        self.user = user
        self.pwd = pwd
        self.ssl_thumbprint = ssl_thumbprint
        self.saml_token = saml_token
        self.vc_vmomi_config = Config.get_section("vcenter.vmomi")
        self.verify_ssl = verify_ssl
        self.vmomi_client = None
        self.connect(version)

    def connect(self, version):
        """
        Connect to the vCenter Server.
        :param version: vmodl version. e.g., 'cis.license.version.version2': str
        :type version: :class:'str'
        :return: None
        """
        logger.info("Connecting to the vCenter Server")
        ssl_ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
        if not self.verify_ssl:
            logger.info("Skipping SSL certificate verification")
            ssl_ctx.verify_mode = ssl.CERT_NONE
            self.ssl_thumbprint = None
        elif self.ssl_thumbprint:
            logger.info("Verifying using thumbprint")
            ssl_ctx.verify_mode = ssl.CERT_NONE
        elif self.saml_token:
            logger.info("Verifying using SAML token")
            ssl_ctx.verify_mode = ssl.CERT_NONE
        else:
            logger.info("Verifying server certificates")
            ssl_ctx.verify_mode = ssl.CERT_REQUIRED
            ssl_ctx.load_verify_locations(capath=consts.SSL_VERIFY_CA_PATH)
            self.ssl_thumbprint = None

        supportedVersion = version

        self.vmomi_client = VmomiClient(
            hostname=self.vc_name,
            port=self.port,
            thumbprint=self.ssl_thumbprint,
            ssl_context=ssl_ctx,
            get_session_obj_for_child_func=VcVmomiClient.get_session_obj,
            session_login_func=VcVmomiClient.generate_login_method(username=self.user, password=self.pwd),
            session_logout_func=VcVmomiClient.generate_logout_method(vc_name=self.vc_name),
            version=supportedVersion,
            saml_token=self.saml_token,
        )

        self.vmomi_client.connect()
        si = self.vmomi_client.get_managed_object(vim.ServiceInstance, "ServiceInstance")

        try:
            content = si.RetrieveContent()
        except Exception as e:
            logger.error(str(e))
            raise Exception(e) from e

        self.si = si
        self.content = content
        logger.debug("VC session established")

    @staticmethod
    def get_session_obj(soap_stub):
        """
        Get a dict that contains possible needed session info
        for any child VmomiClient of VcService to do login.
        :return: dict that contains VC soap_stub cookie and session
        :rtype: `dict`
        """
        vc_cookie = soap_stub.cookie
        vc_si = vim.ServiceInstance("ServiceInstance", soap_stub)
        vc_si_content = vc_si.RetrieveContent()
        vc_session = vc_si_content.sessionManager.currentSession
        vc_session_obj = {"cookie": vc_cookie, "session": vc_session}
        return vc_session_obj

    @staticmethod
    def generate_login_method(username, password):
        """
        Create a VC session login function using the supplied username
        and password.
        :param username: login username.
        :type username: :class:'str'
        :param password: login password.
        :type password: :class:'str'
        :return: _doLogin
        :rtype: 'function'
        """
        # This lock is used to protect the login function to be threadsafe
        # i.e. protect multiple threads from attempting login concurrently
        # and triggering login failures.
        login_lock = Lock()

        def _do_login(soap_stub):
            """
            Login to VC and establish a session instance.
            :param soap_stub: The communication substrate.
            :type soap_stub: :class:'SoapStubAdapter'
            :return: None
            """
            # raise six.moves.http_client.HTTPException()
            nonlocal login_lock
            with login_lock:
                logger.info("VC logging in")
                log_libcall("vim.ServiceInstance", soap_stub)
                vc_si = vim.ServiceInstance("ServiceInstance", soap_stub)

                log_libcall("vim.ServiceInstance.RetrieveContent")
                vc_content = vc_si.RetrieveContent()
                if vc_si._stub.cookie:
                    # If the session already exists, then attempt login only if the
                    # session is not valid.
                    try:
                        log_libcall("vim.ServiceInstance.RetrieveContent.rootFolder.childEntity")
                        vc_content.rootFolder.childEntity
                        return
                    except Exception as exp:
                        logger.warning("Failed to invoke VC API. Relogging in. Error: %s", exp)

                # Update vc session
                vc_session_mgr = vc_content.sessionManager
                if soap_stub.samlToken:
                    vc_session_mgr.LoginByToken()
                else:
                    vc_session_mgr.Login(username, password, None)
                logger.info("VC logged in")

        return _do_login

    @staticmethod
    def generate_logout_method(vc_name):
        """
        Create a VC session logout function.
        :param vc_name: The hostname for the VC.
        :type  vc_name: :class: `str`
        :return: _do_logout
        :rtype: `function`
        """

        def _do_logout(soap_stub):
            """
            Logout the VC session.
            :param soap_stub: The communication substrate.
            :type soap_stub: :class:'SoapStubAdapter'
            :return: None
            """
            logger.info("VC logging out")
            vc_si = vim.ServiceInstance("ServiceInstance", soap_stub)

            if vc_si:
                log_libcall("pyVim.connect.Disconnect", vc_name)
                Disconnect(vc_si)
                logger.info("VC logged out. Disconnected from VC")

        return _do_logout

    def disconnect(self):
        """
        Disconnect the VC service instance.
        :return: None
        """
        self.vmomi_client.disconnect()

    def get_objects_from_container_by_vimtype(self, container, vimtype):
        """
        Searches the container for objects of type vimtype and returns a
        list of managed object references.
        :param container: Reference to the container object
        :type container: :class: 'vmodl:ManagedObjectReference'
        :param vimtype: Managed entity type to search for
        :type vimtype: :class: 'str'
        :return: List of managed object references matching the type
        :rtype: :class: 'list'
        """
        log_libcall("vim.View.ViewManager.CreateContainerView", container, [vimtype], "True")
        container_view = self.content.viewManager.CreateContainerView(
            container=container, type=[vimtype], recursive=True
        )
        # Convert class 'pyVmomi.VmomiSupport.ManagedObject[]' to 'list'
        object_list = list(container_view.view)
        log_libcall("vim.View.ContainerView.DestroyView")
        container_view.DestroyView()
        return object_list

    def find_datacenter_for_obj(self, obj):
        """Find the datacenter to which an object belongs to.

        :param obj: vim object to find its parent data-center
        :return:
        """
        if obj is None:
            return None
        elif hasattr(obj, "parent") and obj.parent is not None:
            if isinstance(obj.parent, vim.Datacenter):
                return obj.parent
            else:
                return self.find_datacenter_for_obj(obj.parent)
        else:
            return None

    def wait_for_task(self, task, poll_interval=None, timeout=None):
        """
        Wait for vim.Task to complete.
        :param task: vim.Task to poll for completion.
        :param poll_interval: Poll interval for task.
        :param timeout: Timeout for waiting, default is 30 seconds.
        :return:
        """
        if not poll_interval:
            poll_interval = self.vc_vmomi_config.getint("TaskPollIntervalSeconds")
        if not timeout:
            timeout = self.vc_vmomi_config.getint("TaskTimeoutSeconds")
        start_time = time.time()
        while task.info.state not in [task.info.state.success, task.info.state.error]:
            if time.time() - start_time > timeout:
                logger.warning(f"Timeout ({timeout} seconds) reached while waiting for task {task.info.name}")
                raise TimeoutError(f"Timeout ({timeout} seconds) reached while waiting for task {task.info.name}")

            time.sleep(poll_interval)

        if task.info.state == task.info.state.success:
            logger.info(f"Task {task} completed successfully")
            return True

        logger.error(f"Task failed with error: {task.info.error}")
        raise Exception(f"Task failed with error: {task.info.error}")

    def get_vpxd_option_value(self, option_key):
        """
        Get the value of a VPXD option.

        :param option_key: VPXD option string.
        :type option_key: str
        :return: VPXD option's value or None if not found.
        :rtype: Any or None
        """
        try:
            vpxd_settings = self.content.setting
            advanced_options = vpxd_settings.QueryOptions() if vpxd_settings else []

            option_object = next((opt for opt in advanced_options if opt.key == option_key), None)

            if option_object:
                option_value = option_object.value
                logger.info(f"Retrieved VPXD option value for {option_key}: {option_value}")
                return option_value

            logger.info(f"VPXD option {option_key} not found.")
            return None
        except Exception as ex:
            logger.error(f"Failed to read the VPXD option for {option_key}. Error: {str(ex)}")
            return None

    def set_vpxd_option_value(self, key, value):
        """
        Set the value for a VPXD option.

        :param key: VPXD option key.
        :type key: str
        :param value: Desired value for the VPXD option.
        :type value: Any
        :return: True if the update is successful, False otherwise.
        :rtype: bool
        """
        try:
            vpxd_settings = self.content.setting

            # Create OptionValue object for the update
            option_value = vim.OptionValue(key=key, value=value)

            # Update VPXD setting value
            vpxd_settings.UpdateOptions(changedValue=[option_value])

            # Retrieve and check the updated value
            updated_option_value = self.get_vpxd_option_value(key)

            # Log and check the updated value
            if updated_option_value is not None and updated_option_value == value:
                logger.info(f"Updated VPXD {key} to {updated_option_value}")
                return True
            return False
        except Exception as ex:
            logger.error(f"Failed to update {key} with value {value}. Error: {str(ex)}")
            raise ex

    def get_objects_by_vimtype(self, vimtype):
        """
        Searches the VC for objects of type vimtype and returns the list.
        :param vimtype: Managed entity type to search for
        :type vimtype: :class: 'str'
        :return: List of objects matching the type
        :rtype: :class: 'list'
        """
        return self.get_objects_from_container_by_vimtype(container=self.content.rootFolder, vimtype=vimtype)

    def get_vm_path_in_datacenter(self, vm_ref):
        """
        Get the path of the virtual machine in the datacenter, including the datacenter name and nested folders.

        The path structure consists of the following levels of nesting:

        - Datacenter: Represents the top-level container for all objects in the datacenter.

        - Folders: Represents intermediate folders that may contain the virtual machine. These folders
          could be nested within each other. 'vm' is the base folder for all the Virtual Machine inside a datacenter.

        - Virtual Machine: Represents the virtual machine object itself.

        Example:
        If the virtual machine named 'vCenter' is located in a datacenter named 'SDDC-Datacenter' and resides within
        base folder named 'vm', which has a folder named 'Management VMs' the path would be
        'SDDC-Datacenter/vm/Management VMs/vCenter'.

        :param vm_ref: vim.VirtualMachine object representing the virtual machine
        :type vm_ref: : vim.VirtualMachine
        :return: Path of the virtual machine in the datacenter (including nested folders) with the datacenter name
        :rtype: str
        """
        vm_path = ""
        parent = vm_ref.parent
        while not isinstance(parent, vim.Datacenter):
            if isinstance(parent, vim.Folder):
                vm_path = "/" + parent.name + vm_path
            parent = parent.parent
        # Add the datacenter name to the path
        if isinstance(parent, vim.Datacenter):
            vm_path = parent.name + vm_path
        return vm_path

    def get_objects_by_vimtype_and_name(self, vimtype, name):
        """
        Searches the VC for objects of type vimtype and name.
        :param vimtype: VC object type
        :type vimtype: :class: 'str'
        :param name: Name of object
        :type name: :class: 'str'
        :return: List of object matching name and type
        :rtype: :class: 'list'
        """
        return [
            item
            for item in self.get_objects_from_container_by_vimtype(container=self.content.rootFolder, vimtype=vimtype)
            if item.name == name
        ]

    def get_object_by_vimtype_and_moid(self, vimtype, moid):
        """
        Gets the VC managed object reference of type vimtype and moid.
        :param vimtype: VC object type
        :type vimtype: class:'str'
        :param moid: moid of object
        :type moid: class:'str'
        :return: Object of type vimtype with given moid
        :rtype: 'vmodl:ManagedObjectReference'
        """
        moref = self.vmomi_client.get_managed_object(vimtype, moid)
        return moref

    def get_all_hosts_from_parent(self, container):
        """
        Get all the hosts under given parent container.

        :type  container: :class: vim.ManagedEntity
        :param container: Container from which ESX hosts should be obtained
        :rtype :class:'list(:class:'vim.HostSystem')'
        :return: List of all the hosts under given parent container.
        """
        return self.get_objects_from_container_by_vimtype(container, vim.HostSystem)

    def get_host_refs_for_moids(self, host_moids):
        """
        Return the host refs for the moids.
        :type host_moids: list(str)
        :param host_moids: List of host moids to lookup the refs for.
        :rtype :class:'list(:class:'vim.hostSystem')'
        :return: List of requested hosts managed by VC.
        """
        return [self.get_object_by_vimtype_and_moid(vim.hostSystem, host_moid) for host_moid in host_moids]

    def get_host_ref_for_moid(self, host_moid):
        """
        Return the host refs for the moids.
        :type host_moid: str
        :param host_moid: List of host moids to lookup the refs for.
        :rtype :class:'vim.hostSystem'
        :return: requested host managed by VC.
        """
        return self.get_object_by_vimtype_and_moid(vim.HostSystem, host_moid)

    def get_all_clusters(self):
        """
        Get all the clusters under this VC.

        :rtype :class:'list(:class:'vim.ClusterComputeResource')'
        :return: List of all the clusters managed by VC.
        """
        return self.get_objects_by_vimtype(vim.ClusterComputeResource)

    def get_cluster_refs_for_moids(self, cluster_moids):
        """
        Return the cluster refs for the moids.
        :type cluster_moids: list(str)
        :param cluster_moids: List of cluster moids to lookup the refs for.
        :rtype :class:'list(:class:'vim.ClusterComputeResource')'
        :return: List of requested clusters managed by VC.
        """
        return [
            self.get_object_by_vimtype_and_moid(vim.ClusterComputeResource, cluster_moid)
            for cluster_moid in cluster_moids
        ]

    def get_cluster_ref_for_moid(self, cluster_moid):
        """
        Return the cluster refs for the moids.
        :type cluster_moid: str
        :param cluster_moid: List of cluster moids to lookup the refs for.
        :rtype :class:'vim.ClusterComputeResource'
        :return: requested cluster managed by VC.
        """
        return self.get_object_by_vimtype_and_moid(vim.ClusterComputeResource, cluster_moid)

    @staticmethod
    def get_cluster_for_host(host_obj):
        """
        Returns the cluster objects for the host object.
        :param host_obj: Host Object
        :return: None if a cluster is not found else cluster object for the
                 host_obj
        :rtype: 'vim.ClusterComputeResource' or None
        """
        try:
            parent = host_obj.parent
            while parent:
                if isinstance(parent, vim.ClusterComputeResource):
                    return parent
                parent = parent.parent
        except Exception as e:
            logger.error(e)
            raise
        return None

    def get_all_standalone_esx_hosts_from_vc(self):
        """
        Get all the standalone hosts under this VC.

        :rtype :class:'list(:class:'vim.HostSystem')'
        :return: List of all the standalone hosts managed by VC.
        """
        return [
            host_obj for host_obj in self.get_objects_by_vimtype(vim.HostSystem) if self.is_standalone_host(host_obj)
        ]

    @staticmethod
    def is_standalone_host(host_obj):
        """
        Check if a host is standalone.
        :param host_obj: Host reference
        :type host_obj: vim.HostSystem
        :return: True or False
        :rtype: 'bool'
        """
        comp_ref = host_obj.parent
        return (
            type(comp_ref) == vim.ComputeResource
            and hasattr(comp_ref, "host")
            and len(comp_ref.host) == 1
            and comp_ref.host[0] == host_obj
        )

    def retrieve_cluster_path_moid_mapping(self):
        """
        Retrieves the cluster path to moid mapping.
        @return: map of cluster moid to path
        @rtype: dict
        Sample response format:
            {
               "cluster-path-1": "cluster-moid",
            }
        """
        clusters = self.get_all_clusters()
        result_dict = {}
        if clusters:
            for cluster in clusters:
                cluster_path = self._get_parent_path(cluster)
                result_dict[cluster_path] = cluster._moId
        return result_dict

    @staticmethod
    def _get_parent_path(node):
        if node is None or node.parent is None:
            return ""

        if node.name == "host":
            return VcVmomiClient._get_parent_path(node.parent)

        return VcVmomiClient._get_parent_path(node.parent) + "/" + node.name


def log_libcall(libcall, *args):
    """
    Logs the library call along with args under the component VC.
    :param libcall: Library call made.
    :type libcall: :class:'str'
    :param args: Arguments to the libcall.
    :type args: :class:'list'
    :return: None
    """
    logger.info("Calling VC libcall: api=%s, args=%s", libcall, args)
