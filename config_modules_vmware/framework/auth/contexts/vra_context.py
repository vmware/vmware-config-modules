from config_modules_vmware.framework.auth.contexts.base_context import BaseContext

class VraContext(BaseContext):
    """
    Class to be shared among vRealize suite VRA config-modules controllers.
    """

    def __init__(self, hostname=None):
        """
        Initialize context for config controllers to work on.
        :param hostname: VRA hostname
        :type hostname: :class:'str'
        """
        super().__init__(BaseContext.ProductEnum.VRA)
        self._hostname = hostname

    @property
    def hostname(self) -> str:
        """
        Returns the hostname of the VRA instance.
        :return: hostname
        :rtype: str
        """
        return self._hostname
