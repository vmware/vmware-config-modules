from config_modules_vmware.framework.auth.contexts.base_context import BaseContext

class VidmContext(BaseContext):
    """
    Class to be shared among VIDM config-modules controllers.
    """

    def __init__(self, hostname=None, username=None, password=None, ssl_thumbprint=None, client_id=None, client_secret=None):
        """
        Initialize context for config controllers to work on.
        :param hostname: Vidm hostname
        :type hostname: :class:'str'
        """
        super().__init__(BaseContext.ProductEnum.VIDM)
        self._hostname = hostname
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._ssl_thumbprint = ssl_thumbprint
        self._vidm_rest_client = None

    @property
    def hostname(self) -> str:
        """
        Returns the hostname of the VIDM instance.
        :return: hostname
        :rtype: str
        """
        return self._hostname
