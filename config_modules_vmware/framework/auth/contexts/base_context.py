# Copyright 2024 Broadcom. All Rights Reserved.
from enum import Enum


class BaseContext:
    """
    Class provides baseclass to be extended by context classes for each product category
    (e.g) VcenterContext. Context objects should be placeholder for the various data
    needed for config objects to work on to deliver the config management functionalities.

    Respective child context classes extending this class should define the structure
    needed to hold various data/objects for the corresponding config module to work on.
    and common objects or methods should be defined here in the parent class.
    """

    class ProductEnum(str, Enum):
        """
        Enum class for product.
        """

        ESXI = "esxi"
        VCENTER = "vcenter"
        SDDC_MANAGER = "sddc_manager"
        NSXT_MANAGER = "nsxt_manager"
        NSXT_EDGE = "nsxt_edge"
        VRSLCM = "vrslcm"
        VIDM = "vidm"
        VRO = "vro"
        VRA = "vra"
        VRLI = "vrli"

    def __init__(self, product_category: ProductEnum, product_version=None, hostname=None):
        """
        Initialize base Context with the product category.

        :param product_category: The product type.
        :type product_category: Product type
        :param product_version: vCenter version in <major>.<minor>.<revision> format
        :type product_version: str
        :param hostname: Hostname for context
        :type hostname: str
        """
        self._product_category = product_category
        self._product_version = product_version
        self._hostname = hostname

    @property
    def product_category(self):
        return self._product_category

    @product_category.setter
    def product_category(self, product_category):
        self._product_category = product_category

    @property
    def product_version(self):
        return self._product_version

    @product_version.setter
    def product_version(self, product_version):
        self._product_version = product_version

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        self._hostname = hostname

    def __enter__(self):
        """
        Called when the consumer starts the 'with context:' block
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when the consumer's 'with context:' block ends.
        Can be used to disconnect from any instantiated clients.
        """
        pass  # pylint: disable=unnecessary-pass
