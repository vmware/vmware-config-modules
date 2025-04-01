# Copyright 2025 Broadcom. All Rights Reserved.
import logging
import re
from typing import Tuple

import urllib3

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.vcenter.vc_rest_client import VcRestClient
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

# Set up logger
logger = LoggerAdapter(logging.getLogger(__name__))


class VcInvsvcMob3Client(VcRestClient):
    """
    Class that exposes internal Mob3 client interface.
    This class is inherited from VcRestClient
    """

    def __init__(
        self, hostname: str, username: str, password: str, ssl_thumbprint: str = None, verify_ssl=True, cert_info=None
    ):
        """
        Initialize VcInvsvcMob3Client
        :param hostname: Vcenter hostname to connect to
        :type hostname: str
        :param username: username to use for the connection
        :type username: str
        :param password: password to use for the connection
        :type password: str
        :param ssl_thumbprint: ssl thumbprint to use for the connection
        :type ssl_thumbprint: str
        :param verify_ssl: Flag to enable/disable ssl verification
        :type verify_ssl: boolean
        """

        super().__init__(hostname, username, password, ssl_thumbprint, verify_ssl, cert_info, session_based=False)
        self._base_url = f"https://{hostname}/invsvc/mob3"
        self._basic_auth_header = urllib3.make_headers(basic_auth=f"{username}:{password}")

    def get_session_nonce(self, url: str) -> Tuple[str, str]:
        """Get session nonce for mob3 apis.

        :param vc_invsvc_mob3_client: vcenter inventory mob3 api client.
        :type vc_invsvc_mob3_client: VcInvsvcMob3Client
        :param url: mob3 api url.
        :type url: str
        :return: Tuple of session nonce string and session cookie string.
        :rtype: Tuple
        """

        self._basic_auth_header[consts.CONTENT_TYPE] = consts.HEADER_TYPE_WWW_FORM
        self._basic_auth_header[consts.CACHE_CONTROL] = consts.HEADER_TYPE_NO_CACHE
        # Make REST request
        response = self.get_helper(url=url, headers=self._basic_auth_header, raw_response=True)
        if response.status == 200:
            cookie_str = self._extract_cookie_str(response)
            match = re.search(
                'name="vmware-session-nonce" type="hidden" value="([^"]+)"', response.data.decode("utf-8")
            )
            if match:
                return match.group(1), cookie_str
            else:
                logger.error("No session nonce for mob3 api found.")
        logger.error(f"Failed to retrieve session nonce: {response.status}")
        raise Exception(f"Failed to retrieve session nonce: {response.status}")

    def _extract_cookie_str(self, response):
        cookie = response.headers.get("set-cookie")
        if cookie:
            cookie_str = cookie.split(";")[0]
        else:
            cookie_str = ""
        return cookie_str

    def disconnect(self):
        """
        Disconnect the Mob 3 client instance.
        :return: None
        """
        logout_url = f"{self._base_url}/logout"
        response = self.get_helper(logout_url, headers=self._basic_auth_header, raw_response=True)
        if response.status != 200:
            logger.error("Failed to logout gracefully")
