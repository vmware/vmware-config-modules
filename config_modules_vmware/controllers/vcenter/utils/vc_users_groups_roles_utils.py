# Copyright 2025 Broadcom. All Rights Reserved.
import logging
from typing import List
from urllib.parse import quote

from bs4 import BeautifulSoup

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_invsvc_mob3_client import VcInvsvcMob3Client
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

USER_NAME_ROW = 8
GROUP_ROW = 7
PROPAGATE_ROW = 9
ROLE_ID_ROW = 10


def _parse_global_permissions(perm_html: BeautifulSoup) -> List:
    """Parsing mob3 api returned global permissions in beautifulsoup format.

    :param perm_html: mob3 api returned result in beautifulsoup format.
    :type perm_html: BeautifulSoup
    :return: a list of parsed global permissions.
    :rtype: List
    """
    global_permissions = []
    li_tags = [li_tag for li_tag in perm_html.find_all("li") if li_tag.table]
    for li_tag in li_tags:
        rows = li_tag.table.find_all("tr")
        global_permission = {
            "name": rows[USER_NAME_ROW].find_all("td")[-1].text,
            "type": "GROUP" if rows[GROUP_ROW].find_all("td")[-1].text == "true" else "USER",
            "propagate": True if rows[PROPAGATE_ROW].find_all("td")[-1].text == "true" else False,
            "role_id": int(rows[ROLE_ID_ROW].li.text),
        }
        global_permissions.append(global_permission)
    logger.debug(f"Global Permissions: {global_permissions}")
    return global_permissions


def get_global_permissions(vc_invsvc_mob3_client: VcInvsvcMob3Client) -> List:
    """Get global permissions from vcenter.

    :param vc_invsvc_mob3_client: vcenter inventory mob3 api client.
    :type vc_invsvc_mob3_client: VcInvsvcMob3Client
    :return: a list of global permissions.
    :rtype: List
    """
    base_url = vc_invsvc_mob3_client.get_base_url()
    mob_url = f"{base_url}/?moid=authorizationService&method=AuthorizationService.GetGlobalAccessControlList"

    nonce, cookie_str = vc_invsvc_mob3_client.get_session_nonce(mob_url)
    logger.debug(f"Get session nonce: {nonce}")
    body = f"vmware-session-nonce={nonce}"

    headers = {consts.CONTENT_TYPE: consts.HEADER_TYPE_WWW_FORM, consts.CACHE_CONTROL: consts.HEADER_TYPE_NO_CACHE}
    if cookie_str:
        headers["Cookie"] = cookie_str

    response = vc_invsvc_mob3_client.post_helper(
        mob_url, body=body, headers=headers, raw_response=True, raise_for_status=True
    )

    if response.status == 200:
        perm_html = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
        global_permissions = _parse_global_permissions(perm_html)
        return global_permissions
    logger.error(f"Failed to get global permissions: {response.status}")
    raise Exception(f"Failed to retrieve global permissions: {response.status}")


def add_global_permission(
    vc_invsvc_mob3_client: VcInvsvcMob3Client, vc_user: str, vc_role_id: int, group: bool, propagate: bool
) -> None:
    """Add global permission.

    :param vc_invsvc_mob3_client: vcenter inventory mob3 api client.
    :type vc_invsvc_mob3_client: VcInvsvcMob3Client
    :param vc_user: user name (including domain).
    :type vc_user: str
    :param vc_role_id: role id number.
    :type vc_role_id: int
    :param group: group or member (group if True otherwise member).
    :type group: bool
    :param propagate: permission propagate flag (propagate to sub object if True otherwise only this object).
    :type propagate: bool
    :return: None
    :rtype: None
    """

    base_url = vc_invsvc_mob3_client.get_base_url()
    mob_url = f"{base_url}/?moid=authorizationService&method=AuthorizationService.AddGlobalAccessControlList"
    nonce, cookie_str = vc_invsvc_mob3_client.get_session_nonce(mob_url)

    vc_user_escaped = quote(vc_user)
    body = (
        f"vmware-session-nonce={nonce}&permissions=%3Cpermissions%3E%0D%0A"
        f"+++%3Cprincipal%3E%0D%0A++++++%3Cname%3E{vc_user_escaped}%3C%2Fname%3E%0D%0A"
        f"++++++%3Cgroup%3E{group}%3C%2Fgroup%3E%0D%0A+++%3C%2Fprincipal%3E%0D%0A"
        f"+++%3Croles%3E{vc_role_id}%3C%2Froles%3E%0D%0A"
        f"+++%3Cpropagate%3E{str(propagate).lower()}%3C%2Fpropagate%3E%0D%0A%3C%2Fpermissions%3E"
    )

    headers = {consts.CONTENT_TYPE: consts.HEADER_TYPE_WWW_FORM}
    if cookie_str:
        headers["Cookie"] = cookie_str

    response = vc_invsvc_mob3_client.post_helper(
        mob_url, body=body, headers=headers, raw_response=True, raise_for_status=True
    )
    if response.status != 200:
        logger.error(f"Failed to add global permission: {response.status}")
        raise Exception(f"Failed to add global permission: {response.status}")


def remove_global_permission(vc_invsvc_mob3_client: VcInvsvcMob3Client, vc_user: str, group: bool) -> None:
    """Remove global permission.

    :param vc_invsvc_mob3_client: vcenter inventory mob3 api client.
    :type vc_invsvc_mob3_client: VcInvsvcMob3Client
    :param vc_user: user name (including domain).
    :type vc_user: str
    :param group: group or member (group if True otherwise member).
    :type group: bool
    :return: None
    :rtype: None
    """

    base_url = vc_invsvc_mob3_client.get_base_url()
    mob_url = f"{base_url}/?moid=authorizationService&method=AuthorizationService.RemoveGlobalAccess"
    nonce, cookie_str = vc_invsvc_mob3_client.get_session_nonce(mob_url)

    vc_user_escaped = quote(vc_user)
    body = (
        f"vmware-session-nonce={nonce}&principals=%3Cprincipals%3E%0D%0A"
        f"+++%3Cname%3E{vc_user_escaped}%3C%2Fname%3E%0D%0A"
        f"+++%3Cgroup%3E{group}%3C%2Fgroup%3E%0D%0A%3C%2Fprincipals%3E"
    )

    headers = {consts.CONTENT_TYPE: consts.HEADER_TYPE_WWW_FORM}
    if cookie_str:
        headers["Cookie"] = cookie_str

    response = vc_invsvc_mob3_client.post_helper(
        mob_url, body=body, headers=headers, raw_response=True, raise_for_status=True
    )
    if response.status != 200:
        logger.error(f"Failed to remove global permission: {response.status}")
        raise Exception(f"Failed to remove global permission: {response.status}")
