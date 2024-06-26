# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from base64 import b64encode

import requests

from config_modules_vmware.framework.clients.aria_suite.aria_consts import GET_PASSWORD_LOCAL_URL
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

# Set up logger
logger = LoggerAdapter(logging.getLogger(__name__))


def get_http_headers() -> dict:
    """
    Retrieves http headers to be used in the controllers. This retrieves the credentials of aria LCM appliance using a local API.
    :return: Dictionary of http headers
    :rtype: dict
    :raise: Exception
    """
    try:
        logger.debug("Making call to get http headers.")
        response = requests.get(GET_PASSWORD_LOCAL_URL, timeout=60)
        response.raise_for_status()
        get_response = response.json()
        username = get_response["username"]
        password = get_response["password"]
        logger.debug(f"Retrieved username: {username}")

        encoded_token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        rest_headers = {
            "Authorization": "Basic " + str(encoded_token),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        return rest_headers
    except Exception as e:
        logger.exception(f"Exception getting http headers - {e}")
        raise e
