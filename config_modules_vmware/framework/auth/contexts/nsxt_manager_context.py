from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.clients.nsxt.nsxt_manager_rest_client import NSXTManagerRestClient


class NSXTManagerContext(BaseContext):
    """
    Class to be shared among NSX config modules, i.e it is placeholder for connection related objects
    which NSX config modules would need to talk to. It supports context manager to trigger
    cleanup of any active connections during the exit of this object.
    """

    def __init__(self, hostname=None, username=None, password=None):
        """
        Initialize context for NSXManager config functionalities to work on.
        :param hostname: NSX appliance hostname
        :type hostname: :class:'str'
        :param username: NSX appliance username
        :type username: :class:'str'
        :param password: NSX appliance Password
        :type password: :class:'str'
        """
        super().__init__(BaseContext.ProductEnum.NSXT_MANAGER)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._nsxt_manager_rest_client = None
        
        

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
        if self._nsxt_manager_rest_client:
            del self._nsxt_manager_rest_client
            self._nsxt_manager_rest_client = None

    def nsxt_manager_rest_client(self):
        """
        Returns the instance of a NSXManagerRestClient
        Initializes if one does not exist.
        """
        if not self._nsxt_manager_rest_client:
            self._nsxt_manager_rest_client = NSXTManagerRestClient()
        return self._nsxt_manager_rest_client

    @property
    def hostname(self):
        """Get host name.
        :return: host name.
        :rtype: class:'str'
        """
        return self._hostname
