# Copyright 2024 Broadcom. All Rights Reserved.
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_rest_client import SDDCManagerRestClient


class SDDCManagerContext(BaseContext):
    """
    Class to be shared among SDDC manager config modules, i.e it is placeholder for connection related objects
    which SDDC Manager config modules would need to talk to. It supports context manager to trigger
    cleanup of any active connections during the exit of this object.
    """

    def __init__(self, hostname=None, username=None, password=None, ssl_thumbprint=None, verify_ssl=True):
        """
        Initialize context for SDDCManager config functionalities to work on.
        :param hostname: sddc-manager hostname
        :type hostname: :class:'str'
        :param username: sddc-manager username
        :type username: :class:'str'
        :param password: sddc-manager Password
        :type password: :class:'str'
        :param verify_ssl: Flag to enable/disable SSL verification
        :type verify_ssl: :class:'boolean'
        """
        super().__init__(product_category=BaseContext.ProductEnum.SDDC_MANAGER, hostname=hostname)
        self._username = username
        self._password = password
        self._ssl_thumbprint = ssl_thumbprint
        self._verify_ssl = verify_ssl
        self._sddc_manager_rest_client = None

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
        if self._sddc_manager_rest_client:
            del self._sddc_manager_rest_client
            self._sddc_manager_rest_client = None

    def sddc_manager_rest_client(self):
        """
        Returns the instance of a SddcManagerRestClient
        Initializes if one does not exist.
        """
        if not self._sddc_manager_rest_client:
            self._sddc_manager_rest_client = SDDCManagerRestClient(
                self._hostname, self._username, self._password, self._ssl_thumbprint, self._verify_ssl
            )
        return self._sddc_manager_rest_client

    @property
    def hostname(self):
        """Get host name.
        :return: host name.
        :rtype: class:'str'
        """
        return self._hostname

    @property
    def username(self):
        """Get user name.
        :return: user name.
        :rtype: class:'str'
        """
        return self._username

    @property
    def password(self):
        """Get password.
        :return: password.
        :rtype: class:'str'
        """
        return self._password

    @property
    def product_version(self) -> str:
        """
        Returns sddc-manager product version, None if not found.
        :return: version
        :rtype: class:'str'
        """
        if self._product_version is None:
            url = self.sddc_manager_rest_client().get_base_url() + sddc_manager_consts.SDDC_MANAGER_URL
            sddc_managers = self.sddc_manager_rest_client().get_helper(url, json_result=True)
            sddc_manager_list = sddc_managers.get("elements", None)
            if sddc_manager_list:
                self._product_version = sddc_manager_list[0].get("version", None)
        return self._product_version
