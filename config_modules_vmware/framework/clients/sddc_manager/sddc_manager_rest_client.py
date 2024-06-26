# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging
import time
from enum import Enum
from functools import partial
from http import HTTPStatus

import urllib3

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.common.consts import JSON_REQUEST_HEADERS
from config_modules_vmware.framework.clients.common.rest_client import get_smart_rest_client
from config_modules_vmware.framework.clients.common.rest_client import SmartRestClient
from config_modules_vmware.framework.clients.sddc_manager import sddc_manager_consts
from config_modules_vmware.framework.clients.sddc_manager.sddc_manager_consts import TASK_BY_ID
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.services.config import Config

# Set up logger
logger = LoggerAdapter(logging.getLogger(__name__))


class TaskStatusEnum(Enum):
    """
    Enum class for SDDC Manager task status.
    """

    SUCCESSFUL = "SUCCESSFUL"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN PROGRESS"


class SDDCManagerRestClient(object):
    """
    Class that exposes SDDCManager REST APIs to handle API requests.
    """

    def __init__(self, hostname: str, username: str, password: str, ssl_thumbprint: str = None, verify_ssl=True):
        """
        Initialize SddcManagerRestClient
        :param hostname: SDDCManager hostname to connect to
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
        self._base_url = sddc_manager_consts.SDDC_MANAGER_API_BASE.format(hostname)

        # Set up REST client
        get_sddc_manager_token = partial(
            SDDCManagerRestClient._get_sddc_manager_token, hostname=hostname, username=username, password=password
        )

        if not verify_ssl:
            self._rest_client_session = get_smart_rest_client(
                cert_reqs=consts.CERT_NONE,
                get_session_headers_func=get_sddc_manager_token,
            )
        elif ssl_thumbprint:
            self._rest_client_session = get_smart_rest_client(
                assert_fingerprint=ssl_thumbprint, get_session_headers_func=get_sddc_manager_token
            )
        else:
            self._rest_client_session = get_smart_rest_client(
                cert_reqs=consts.CERT_REQUIRED, get_session_headers_func=get_sddc_manager_token
            )

        self.sddc_manager_rest_config = Config.get_section("sddc_manager.rest")

    @staticmethod
    def _get_sddc_manager_token(client, hostname, username, password):
        """
        Make REST call to get SDDC Manager token
        :param client: Rest client.
        :type client: 'urllib3.poolmanager.PoolManager'
        :param hostname: Host name
        :type hostname: 'str'
        :param username: Username
        :type username: 'str'
        :param password: Password
        :type password: 'str'
        :raise :class:`urllib3.exceptions.HTTPError`
            If REST call response has a non HTTPStatus.OK status code.
        """
        logger.info("Creating vmware api session")

        url = sddc_manager_consts.SDDC_MANAGER_TOKEN_URL.format(hostname)
        # basic_auth_header = urllib3.make_headers(
        #     basic_auth="{}:{}".format(username, password))
        headers = {"Content-Type": "application/json"}
        payload = {"username": username, "password": password}
        # Make REST request
        response = client.request(method="POST", url=url, headers=headers, body=json.dumps(payload))

        # Raise urllib3.exceptions.HTTPError
        # If the HTTP request returns an unsuccessful status code
        SmartRestClient.raise_for_status(response, url)

        # Parse response for vmware api session id.
        content_dict = SmartRestClient.extract_json_data(response)
        sddc_manager_access_token = content_dict["accessToken"]
        headers["Authorization"] = "Bearer " + sddc_manager_access_token
        logger.info("Successfully created SDDC Manager API headers")
        return headers

    def sddc_manager_request(self, url, method, **kwargs):
        """
        Invokes SDDC Manager API request
        :param url: URL of the request.
        :type url: 'str'
        :param method: Request type
        :type method: 'str'
        :param kwargs: Parameters used by the request.
        :type kwargs: 'dict'
        :return: http response
        :rtype: 'HTTPResponse'
        """

        body = json.dumps(kwargs["body"]) if "body" in kwargs else None
        if "headers" in kwargs:
            headers = {**kwargs["headers"], **JSON_REQUEST_HEADERS}
        else:
            headers = JSON_REQUEST_HEADERS.copy()
        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
        else:
            timeout = urllib3.Timeout(total=self.sddc_manager_rest_config.getint("APITimeoutSeconds"))
        return self._rest_client_session.request(url=url, method=method, body=body, headers=headers, timeout=timeout)

    @staticmethod
    def _get_str_from_response(response):
        """
        Parse and get string result from http response.
        :param response: Existed http response.
        :return: Result as string.
        """
        result = str(SmartRestClient.decode_data(response))
        return result[1:-1]

    def _handle_response(self, url, response, **kwargs):
        """
        Handle http response according to given kwargs
        :param url:
        :param response:
        :param kwargs:
            raw_response: True if want to return response object,
                False otherwise.
            json_result: True if want to parse json result and return as dict,
                False will return result as string.
            raise_for_status: True if want to raise exception when
                response status code is not 200, False otherwise.
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        if response.status == HTTPStatus.NO_CONTENT:
            logger.info(f"{url}: 204 No Content")
            return None
        raise_for_status = kwargs["raise_for_status"] if "raise_for_status" in kwargs else True
        raw_response = kwargs["raw_response"] if "raw_response" in kwargs else False
        json_result = kwargs["json_result"] if "json_result" in kwargs else True
        if raise_for_status:
            SmartRestClient.raise_for_status(response, url)
        if raw_response:
            return response
        elif json_result:
            return SmartRestClient.extract_json_data(response)
        else:
            return self._get_str_from_response(response)

    def get_helper(self, url, **kwargs):
        """
        Make a HTTP GET request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.sddc_manager_request(url, method="GET", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def delete_helper(self, url, **kwargs):
        """
        Make a HTTP DELETE request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.sddc_manager_request(url, method="DELETE", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def post_helper(self, url, **kwargs):
        """
        Make a HTTP POST request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.sddc_manager_request(url, method="POST", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def put_helper(self, url, **kwargs):
        """
        Make a HTTP PUT request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.sddc_manager_request(url, method="PUT", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def patch_helper(self, url, **kwargs):
        """
        Make a HTTP PATCH request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """

        response = self.sddc_manager_request(url, method="PATCH", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def get_base_url(self):
        return self._base_url

    def monitor_task(self, task_id, timeout_sec=None, poll_interval=None):
        """
        Monitor a given taskId for a given time
        :return: true if task succeeded
                false if task fails
        """
        if not timeout_sec:
            timeout_sec = self.sddc_manager_rest_config.getint("TaskTimeoutSeconds")
        if not poll_interval:
            poll_interval = self.sddc_manager_rest_config.getint("TaskPollIntervalSeconds")
        try:
            end_time = time.time() + timeout_sec
            while time.time() < end_time:
                logger.debug(f"Getting status of task {task_id}")
                url = self._base_url + TASK_BY_ID.format(task_id)
                task_info = self.get_helper(url)
                logger.info(f"Task info {task_info}")
                if task_info:
                    status = task_info["status"]
                    logger.info(f"Task {task_id} status {status}")
                    if status.upper() == TaskStatusEnum.SUCCESSFUL.value:
                        return True
                    if status.upper() == TaskStatusEnum.CANCELLED.value:
                        return False
                    if status.upper() == TaskStatusEnum.FAILED.value:
                        return False
                logger.info(f"Sleeping for {poll_interval} seconds for {task_id}, before retrieving task info")
                time.sleep(poll_interval)
        except Exception as ex:
            logger.error(f"Exception thrown when getting task info : {ex}")
        logger.error(f"Task {task_id} did not finish within %s seconds {timeout_sec}")
        return False
