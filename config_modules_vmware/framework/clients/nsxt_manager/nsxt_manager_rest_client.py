# Copyright 2023-2024 VMware, Inc.  All rights reserved. -- VMware Confidential

from functools import partial
from http import HTTPStatus
import logging
import urllib3
import json
import time

from config_modules_vmware.framework.clients.common.consts import JSON_REQUEST_HEADERS
from config_modules_vmware.framework.clients.nsxt_manager import nsxt_consts
from config_modules_vmware.framework.clients.common.rest_client import get_smart_rest_client, SmartRestClient
from config_modules_vmware.framework.clients.common import consts
#from config_modules_vmware.framework.clients.nsxt_manager.nsxt_manager_consts import TASK_BY_ID
from enum import Enum

# Set up logger
logger = logging.getLogger(__name__)


class TaskStatusEnum(Enum):
    """
    Enum class for SDDC Manager task status.
    """

    SUCCESSFUL = "SUCCESSFUL"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN PROGRESS"


class NSXTManagerRestClient(object):
    """
    Class that exposes NSXT Manager REST APIs to handle API requests.
    """

    def __init__(self, hostname: str, username: str, password: str):
        """
        Initialize NSXT ManagerRestClient
        @param hostname: NSXT Manager hostname to connect to
        @type hostname: str
        @param username: username to use for the connection
        @type username: str
        @param password: password to use for the connection
        @type password: str
        """
        #self._base_url = nsxt_manager_consts.NSXT_MANAGER_API_BASE.format(hostname)

        self._rest_client_session = get_smart_rest_client(
                cert_reqs=consts.CERT_NONE, get_session_headers_func=None, verify=False
            )


    def nsxt_manager_request(self, url, method, **kwargs):
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
            timeout = urllib3.Timeout(total=nsxt_manager_consts.NSXT_MANAGER_REST_API_TIMEOUT_VALUE)
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
        response = self.nsxt_manager_request(url, method="GET", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def delete_helper(self, url, **kwargs):
        """
        Make a HTTP DELETE request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.nsxt_manager_request(url, method="DELETE", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def post_helper(self, url, **kwargs):
        """
        Make a HTTP POST request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.nsxt_manager_request(url, method="POST", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def put_helper(self, url, **kwargs):
        """
        Make a HTTP PUT request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.nsxt_manager_request(url, method="PUT", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def patch_helper(self, url, **kwargs):
        """
        Make a HTTP PATCH request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """

        response = self.nsxt_manager_request(url, method="PATCH", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def get_base_url(self):
        return self._base_url

    def monitor_task(self, task_id, timeout_sec=300, poll_interval=30):
        """
        Monitor a given taskId for a given time
        :return: true if task succeeded
                false if task fails
        """
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
