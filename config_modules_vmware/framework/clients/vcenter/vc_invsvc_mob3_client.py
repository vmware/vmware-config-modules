# Copyright 2025 Broadcom. All Rights Reserved.
import logging
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

# Set up logger
logger = LoggerAdapter(logging.getLogger(__name__))

USER_NAME_ROW = 8
GROUP_ROW = 7
PROPAGATE_ROW = 9
ROLE_ID_ROW = 10


class VcInvsvcMob3Client(object):
    def __init__(self, hostname, username, password, ssl_thumbprint=None, verify_ssl=False):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssl_thumbprint = ssl_thumbprint
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.base_url = f"https://{hostname}/invsvc/mob3"

    def _get_session_nonce(self, url):
        response = self.session.get(url, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        if response.status_code == 200:
            import re

            match = re.search('name="vmware-session-nonce" type="hidden" value="([^"]+)"', response.text)
            if match:
                return match.group(1)
        raise Exception("Failed to retrieve session nonce")

    def add_global_permission(self, vc_user, vc_role_id, group, propagate):
        mob_url = f"{self.base_url}/?moid=authorizationService&method=AuthorizationService.AddGlobalAccessControlList"
        nonce = self._get_session_nonce(mob_url)

        vc_user_escaped = quote(vc_user)
        body = (
            f"vmware-session-nonce={nonce}&permissions=%3Cpermissions%3E%0D%0A"
            f"+++%3Cprincipal%3E%0D%0A++++++%3Cname%3E{vc_user_escaped}%3C%2Fname%3E%0D%0A"
            f"++++++%3Cgroup%3E{group}%3C%2Fgroup%3E%0D%0A+++%3C%2Fprincipal%3E%0D%0A"
            f"+++%3Croles%3E{vc_role_id}%3C%2Froles%3E%0D%0A"
            f"+++%3Cpropagate%3E{str(propagate).lower()}%3C%2Fpropagate%3E%0D%0A%3C%2Fpermissions%3E"
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.session.post(
            mob_url, auth=HTTPBasicAuth(self.username, self.password), data=body, headers=headers, verify=False
        )
        if response.status_code != 200:
            raise Exception(f"Failed to add global permission: {response.text}")

    def remove_global_permission(self, vc_user, group):
        mob_url = f"{self.base_url}/?moid=authorizationService&method=AuthorizationService.RemoveGlobalAccess"
        nonce = self._get_session_nonce(mob_url)

        vc_user_escaped = quote(vc_user)
        body = (
            f"vmware-session-nonce={nonce}&principals=%3Cprincipals%3E%0D%0A"
            f"+++%3Cname%3E{vc_user_escaped}%3C%2Fname%3E%0D%0A"
            f"+++%3Cgroup%3E{group}%3C%2Fgroup%3E%0D%0A%3C%2Fprincipals%3E"
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.session.post(
            mob_url, auth=HTTPBasicAuth(self.username, self.password), data=body, headers=headers, verify=False
        )
        if response.status_code != 200:
            raise Exception(f"Failed to remove global permission: {response.text}")

    def _parse_global_permissions(self, perm_html):
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

    def get_global_permissions(self):
        mob_url = f"{self.base_url}/?moid=authorizationService&method=AuthorizationService.GetGlobalAccessControlList"
        nonce = self._get_session_nonce(mob_url)

        body = f"vmware-session-nonce={nonce}"

        headers = {"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"}

        response = self.session.post(
            mob_url, auth=HTTPBasicAuth(self.username, self.password), data=body, headers=headers, verify=False
        )
        if response.status_code == 200:
            perm_html = BeautifulSoup(response.content, "html.parser")
            global_permissions = self._parse_global_permissions(perm_html)
            return global_permissions
        raise Exception(f"Failed to retrieve roles: {response.text}")

    def disconnect(self):
        logout_url = f"{self.base_url}/logout"
        response = self.session.get(logout_url, verify=False)
        if response.status_code != 200:
            logger.error("Failed to logout gracefully")
