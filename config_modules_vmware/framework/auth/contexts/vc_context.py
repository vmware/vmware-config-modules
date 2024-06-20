# Copyright 2024 Broadcom. All Rights Reserved.
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.vcenter.vc_rest_client import VcRestClient
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_client import VcVmomiClient
from config_modules_vmware.framework.clients.vcenter.vc_vmomi_sso_client import VcVmomiSSOClient
from config_modules_vmware.framework.clients.vcenter.vc_vsan_vmomi_client import VcVsanVmomiClient


class VcenterContext(BaseContext):
    """
    Class to be shared among Vcenter config modules, i.e it is placeholder for connection related objects
    which Vcenter config modules would need to talk to. It supports context manager to trigger
    cleanup of any active connections during the exit of this object.
    """

    def __init__(
        self,
        hostname=None,
        username=None,
        password=None,
        ssl_thumbprint=None,
        saml_token=None,
        verify_ssl=True,
    ):
        """
        Initialize context for Vcenter config functionalities to work on.
        :param hostname: vCenter hostname
        :type hostname: :class:'str'
        :param username: vCenter username
        :type username: :class:'str'
        :param password: vCenter Password
        :type password: :class:'str'
        :param ssl_thumbprint: vCenter thumbprint
        :type ssl_thumbprint: :class:'str'
        :param saml_token: vCenter SAML token to use for authentication instead of username/password
        :type saml_token: :class:'str'
        :param verify_ssl: Flag to enable/disable SSL verification
        :type verify_ssl: :class:'boolean'
        """
        super().__init__(BaseContext.ProductEnum.VCENTER, hostname=hostname)
        self._username = username
        self._password = password
        self._ssl_thumbprint = ssl_thumbprint
        self._saml_token = saml_token
        self._verify_ssl = verify_ssl
        self._vc_vmomi_client = None
        self._vc_rest_client = None
        self._vc_vmomi_sso_client = None
        self._vc_vsan_vmomi_client = None

    def __enter__(self):
        """
        Called when the consumer starts the 'with context:' block
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when the consumer's 'with context:' block ends.
        Disconnects from any instantiated clients.
        """
        if self._vc_vmomi_client:
            self._vc_vmomi_client.disconnect()
        if self._vc_rest_client:
            del self._vc_rest_client
            self._vc_rest_client = None
        if self._vc_vmomi_sso_client:
            self._vc_vmomi_sso_client.disconnect()
        if self._vc_vsan_vmomi_client:
            self._vc_vsan_vmomi_client.disconnect()

    def vc_vmomi_client(self):
        """
        Returns the instance of a VcVmomiClient
        Initializes if one does not exist.
        """
        if not self._vc_vmomi_client:
            self._vc_vmomi_client = VcVmomiClient(
                self._hostname,
                self._username,
                self._password,
                ssl_thumbprint=self._ssl_thumbprint,
                saml_token=self._saml_token,
                verify_ssl=self._verify_ssl,
            )
        return self._vc_vmomi_client

    def vc_rest_client(self):
        """
        Returns the  instance of a VcRestClient
        Initializes if one does not exist.
        """
        if not self._vc_rest_client:
            self._vc_rest_client = VcRestClient(
                self._hostname, self._username, self._password, self._ssl_thumbprint, self._verify_ssl
            )
        return self._vc_rest_client

    def vc_vmomi_sso_client(self):
        """
        Returns the instance of a VcVmomiSSOClient
        Initializes if one does not exist.
        """
        if not self._vc_vmomi_sso_client:
            self._vc_vmomi_sso_client = VcVmomiSSOClient(
                hostname=self._hostname,
                user=self._username,
                pwd=self._password,
                ssl_thumbprint=self._ssl_thumbprint,
                verify_ssl=self._verify_ssl,
            )
        return self._vc_vmomi_sso_client

    def vc_vsan_vmomi_client(self):
        """
        Returns the instance of a VcVsanVmomiClient
        Initializes if one does not exist.
        """
        if not self._vc_vsan_vmomi_client:
            self._vc_vsan_vmomi_client = VcVsanVmomiClient(
                hostname=self._hostname,
                user=self._username,
                pwd=self._password,
                ssl_thumbprint=self._ssl_thumbprint,
                verify_ssl=self._verify_ssl,
            )
        return self._vc_vsan_vmomi_client

    @property
    def product_version(self) -> str:
        """
        Returns product version in <major>.<minor>.<revision> format.
        :return: version in x.y.z format
        :rtype: str
        """
        if self._product_version is None:
            version_arr = self.vc_rest_client().get_vcsa_version().split(".")
            self._product_version = "{}.{}.{}".format(
                version_arr[0],
                version_arr[1] if len(version_arr) > 1 else 0,
                version_arr[2] if len(version_arr) > 2 else 0,
            )
        return self._product_version
