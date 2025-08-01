from config_modules_vmware.framework.auth.contexts.base_context import BaseContext


class VrliContext(BaseContext):
    """
    Class to be shared among Log Insight config modules, i.e it is placeholder for connection related objects
    which Log Insight config modules would need to talk to. It supports context manager to trigger
    cleanup of any active connections during the exit of this object.
    """

    def __init__(self, hostname=None, username=None, password=None, ssl_thumbprint=None):
        """
        Initialize context for LogInsight config functionalities to work on.
        :param hostname: log-insight hostname
        :type hostname: :class:'str'
        :param username: log-insight username
        :type username: :class:'str'
        :param password: log-insight Password
        :type password: :class:'str'
        :param ssl_thumbprint: log-insight thumbprint
        :type ssl_thumbprint: :class:'str'
        """
        super().__init__(BaseContext.ProductEnum.VRLI)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._ssl_thumbprint = ssl_thumbprint

    def __enter__(self):
        """
        Called when the consumer starts the 'with context:' block
        """
        return self

    @property
    def hostname(self):
        """Get host name.
        :return: host name.
        :rtype: class:'str'
        """
        return self._hostname
