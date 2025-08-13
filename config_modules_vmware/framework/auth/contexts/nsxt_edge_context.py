from config_modules_vmware.framework.auth.contexts.base_context import BaseContext

class NSXTEdgeContext(BaseContext):
    """
    Class to be shared among NSX config modules, i.e it is placeholder for connection related objects
    which NSX config modules would need to talk to. It supports context manager to trigger
    cleanup of any active connections during the exit of this object.
    """

    def __init__(self, hostname=None):
        """
        Initialize context for config controllers to work on.
        :param hostname: NSX Edge  hostname
        :type hostname: :class:'str'
        """
        super().__init__(BaseContext.ProductEnum.NSXT_EDGE)
        self._hostname = hostname

    @property
    def hostname(self) -> str:
        """
        Returns the hostname of the NSX Edge instance.
        :return: hostname
        :rtype: str
        """
        return self._hostname
