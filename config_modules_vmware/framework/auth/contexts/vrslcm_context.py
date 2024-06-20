# Copyright 2024 Broadcom. All Rights Reserved.
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext


class VrslcmContext(BaseContext):
    """
    Class to be shared among vRealize suite LCM config-modules controllers.
    """

    def __init__(self, hostname=None):
        """
        Initialize context for config controllers to work on.
        :param hostname: Vrslcm hostname
        :type hostname: :class:'str'
        """
        super().__init__(BaseContext.ProductEnum.VRSLCM, hostname=hostname)
