# Copyright 2024 Broadcom. All Rights Reserved.
import logging

import salt.exceptions

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.esxi_context import EsxiContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import (
    SDDCManagerContext,
)
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext
from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext
from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.framework.auth.contexts.nsxt_edge_context import NSXTEdgeContext
from config_modules_vmware.framework.auth.contexts.vidm_context import VidmContext
from config_modules_vmware.framework.auth.contexts.vro_context import VroContext
from config_modules_vmware.framework.auth.contexts.vra_context import VraContext
from config_modules_vmware.framework.auth.contexts.vrli_context import VrliContext

logger = logging.getLogger(__name__)


def _create_vcenter_context(conf, fqdn):
    return VcenterContext(
        hostname=fqdn,
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
        verify_ssl=conf.get("verify_ssl", True),
    )


def _create_sddc_manager_context(conf, fqdn):
    return SDDCManagerContext(
        hostname=fqdn,
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
        verify_ssl=conf.get("verify_ssl", True),
    )


def _create_esxi_context(vcenter_conf, fqdn=None, ids=None):
    return EsxiContext(
        vc_hostname=fqdn,
        vc_username=vcenter_conf["user"],
        vc_password=vcenter_conf["password"],
        vc_ssl_thumbprint=vcenter_conf.get("ssl_thumbprint", None),
        vc_saml_token=vcenter_conf.get("saml_token", None),
        esxi_host_names=ids,
        verify_ssl=vcenter_conf.get("verify_ssl", True),
    )

def _create_nsxtmanager_context(conf):
    return NSXTManagerContext(
        hostname=conf["host"],
        username=conf["user"],
        password=conf["password"],
     )

def _create_nsxtedge_context(conf):
    return NSXTEdgeContext(
        hostname=conf["host"]
     )

def _create_log_insight_context(conf):
    return VrliContext(
        hostname=conf["host"],
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
    )

def _create_vidm_context(conf):
    return VidmContext(
        hostname=conf["host"],
        username=conf["user"],
        password=conf["password"],        
        client_id=conf["client_id"],
        client_secret=conf["client_secret"],

        ssl_thumbprint=conf.get("ssl_thumbprint", None),
    )


def _get_conf(config, product):
    if product == BaseContext.ProductEnum.ESXI.value:
        # for esxi get parent product (vcenter) conf
        product = BaseContext.ProductEnum.VCENTER.value

    return (
        config.get("saltext.vmware")
        or config.get("grains", {}).get("saltext.vmware")
        or config.get("pillar", {}).get("saltext.vmware")
        or config.get(product)
        or config.get("pillar", {}).get(product)
        or config.get("grains", {}).get(product)
        or {}
    )


def _create_product_context(config, product, ids=None):
    conf = _get_conf(config, product)
    # Fetch fqdn from grains if available
    fqdn = config.get("grains", {}).get("fqdn")
    if not fqdn:
        fqdn = conf.get("host")
    if product == BaseContext.ProductEnum.VCENTER.value:
        return _create_vcenter_context(conf, fqdn)
    elif product == BaseContext.ProductEnum.SDDC_MANAGER.value:
        return _create_sddc_manager_context(conf, fqdn)
    elif product == BaseContext.ProductEnum.NSXT_MANAGER.value:
        return _create_nsxtmanager_context(conf)
    elif product == BaseContext.ProductEnum.NSXT_EDGE.value:
        return _create_nsxtedge_context(conf)
    elif product == BaseContext.ProductEnum.ESXI.value:
        return _create_esxi_context(vcenter_conf=conf, fqdn=fqdn, ids=ids)
    elif product == BaseContext.ProductEnum.VRSLCM.value:
        return VrslcmContext(fqdn)
    elif product == BaseContext.ProductEnum.VIDM.value:
        return _create_vidm_context(conf)
    elif product == BaseContext.ProductEnum.VRO.value:
        return VroContext(conf["host"])
    elif product == BaseContext.ProductEnum.VRA.value:
        return VraContext(conf["host"])
    elif product == BaseContext.ProductEnum.VRLI.value:
        return _create_log_insight_context(conf)
    else:
        raise salt.exceptions.VMwareApiError({f"Unsupported product {product}"})


def create_auth_context(config, product, ids=None):
    logger.debug(f"Creating auth context for product {product}")
    return _create_product_context(config=config, product=product, ids=ids)
