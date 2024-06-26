# Copyright 2024 Broadcom. All Rights Reserved.
from typing import Callable

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.esxi.esx_cli_client import EsxCliClient


class EsxiContext(VcenterContext):
    """
    Class (derives from VcenterContext class) to be shared among ESXi controllers, i.e it is placeholder for
    connection related objects which ESX controllers would need to talk to. It supports context manager to trigger
    cleanup of any active connections during the exit of this object.
    """

    def __init__(
        self,
        vc_hostname=None,
        vc_username=None,
        vc_password=None,
        vc_ssl_thumbprint=None,
        vc_saml_token=None,
        esxi_host_names=None,
        verify_ssl=True,
    ):
        """
        Initialize context for ESX.
        :param vc_hostname: vCenter hostname
        :type vc_hostname: :class:'str'
        :param vc_username: vCenter username
        :type vc_username: :class:'str'
        :param vc_password: vCenter Password
        :type vc_password: :class:'str'
        :param vc_ssl_thumbprint: vCenter thumbprint
        :type vc_ssl_thumbprint: :class:'str'
        :param vc_saml_token: vCenter SAML token to use for authentication instead of username/password.
        :type vc_saml_token: :class:'str'
        :param esxi_host_names: List of HostSystem.name(fqdn/ip).
        :type esxi_host_names: list[str]
        :param verify_ssl: Flag to enable/disable SSL verification.
        :type verify_ssl: bool
        """
        super().__init__(
            hostname=vc_hostname,
            username=vc_username,
            password=vc_password,
            ssl_thumbprint=vc_ssl_thumbprint,
            saml_token=vc_saml_token,
            verify_ssl=verify_ssl,
        )
        self.product_category = BaseContext.ProductEnum.ESXI
        self.esxi_host_names = esxi_host_names
        self._esx_cli_client = None

    def esx_cli_client(self):
        """
        Returns the instance of a EsxCliClient
        Initializes if one does not exist.
        :return: EsxCliClient
        """
        if not self._esx_cli_client:
            self._esx_cli_client = EsxCliClient(self.hostname, self._username, self._password, self._ssl_thumbprint)
        return self._esx_cli_client


class HostContext(BaseContext):
    """
    Class to hold the HostContext to hold the individual esxi host ref and function pointers to the VC clients.
    """

    def __init__(
        self,
        host_ref=None,
        vc_rest_client_func: Callable = None,
        vc_vmomi_client_func: Callable = None,
        esx_cli_client_func: Callable = None,
        hostname=None,
    ):
        """
        :param host_ref: Host reference
        :type host_ref: class:'vim.hostSystem'
        :param vc_rest_client_func: Function pointer for vc_rest_client_func from VcContext.
        :type vc_rest_client_func: Callable
        :param vc_vmomi_client_func:Function pointer for vc_vmomi_client_func from VcContext.
        :type vc_vmomi_client_func: Callable
        :param esx_cli_client_func: Function pointer for esx_cli_client from EsxiContext.
        :type esx_cli_client_func: Callable
        :param hostname: ESXi hostname
        :type hostname: :class:'str'
        """
        super().__init__(BaseContext.ProductEnum.ESXI, hostname=hostname)
        self.host_ref = host_ref
        self._vc_rest_client_func = vc_rest_client_func
        self._vc_vmomi_client_func = vc_vmomi_client_func
        self._esx_cli_client_func = esx_cli_client_func

    def vc_rest_client(self):
        """
        Calls the Callable for vc_rest_client_func that was passed during __init__().
        Returns the  instance of a VcRestClient.
        Initializes if one does not exist.
        :return: Instance of VcRestClient.
        :rtype: VcRestClient
        """
        return self._vc_rest_client_func()

    def vc_vmomi_client(self):
        """
        Calls the Callable for vc_vmomi_client_func that was passed during __init__().
        Returns the instance of a VcVmomiClient.
        Initializes if one does not exist.
        :return: Instance of VcVmomiClient.
        :rtype: VcVmomiClient
        """
        return self._vc_vmomi_client_func()

    def esx_cli_client(self) -> EsxCliClient:
        """
        Calls the Callable for esx_cli_client_func that was passed during __init__().
        Returns the instance of a EsxCliClient.
        Initializes if one does not exist.
        :return: Instance of EsxCliClient.
        :rtype: EsxCliClient
        """
        return self._esx_cli_client_func()

    @property
    def product_version(self) -> str:
        """
        Returns ESXi version. None if not found.
        :return: version in x.y.z format
        :rtype: str
        """
        if self._product_version is None:
            if (
                hasattr(self.host_ref, "config")
                and hasattr(self.host_ref.config, "product")
                and hasattr(self.host_ref.config.product, "version")
            ):
                self._product_version = self.host_ref.config.product.version
            else:
                self._product_version = None
        return self._product_version
