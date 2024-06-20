# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging
import math
import time
from functools import partial
from http import HTTPStatus

import urllib3

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.common.consts import JSON_REQUEST_HEADERS
from config_modules_vmware.framework.clients.common.rest_client import get_smart_rest_client
from config_modules_vmware.framework.clients.common.rest_client import SmartRestClient
from config_modules_vmware.framework.clients.vcenter import vc_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.services.config import Config

# Set up logger
logger = LoggerAdapter(logging.getLogger(__name__))


class VcRestClient(object):
    """
    Class that exposes vCenter REST APIs to handle session. This may be used
    as the base class for other vCenter REST API client classes.
    """

    def __init__(self, hostname, username, password, ssl_thumbprint=None, verify_ssl=True):
        """
        Initialize VcRestClient.
        :param hostname: vCenter hostname
        :type hostname: :class:'str'
        :param username: vCenter username
        :type username: :class:'str'
        :param password: vCenter Password
        :type password: :class:'str'
        :param ssl_thumbprint: vCenter thumbprint
        :type ssl_thumbprint: :class:'str'
        :param verify_ssl: Flag to enable/disable ssl verification
        :type verify_ssl: :class:'boolean'
        """
        self._base_url = vc_consts.VC_API_BASE.format(hostname)
        self._vcsa_version = None
        self.vc_rest_config = Config.get_section("vcenter.rest")

        # Set up REST client
        get_session_headers = partial(
            VcRestClient._create_vmware_api_session_id, hostname=hostname, username=username, password=password
        )
        delete_session = partial(VcRestClient._delete_session_by_hostname, hostname=hostname)
        if not verify_ssl:
            self._rest_client_session = get_smart_rest_client(
                cert_reqs=consts.CERT_NONE,
                get_session_headers_func=get_session_headers,
                delete_session_func=delete_session,
            )
        elif ssl_thumbprint:
            self._rest_client_session = get_smart_rest_client(
                assert_fingerprint=ssl_thumbprint,
                get_session_headers_func=get_session_headers,
                delete_session_func=delete_session,
            )
        else:
            self._rest_client_session = get_smart_rest_client(
                cert_reqs=consts.CERT_REQUIRED,
                get_session_headers_func=get_session_headers,
                delete_session_func=delete_session,
            )

        self.set_vcsa_version()

    @staticmethod
    def _create_vmware_api_session_id(client, hostname, username, password):
        """
        Make REST call to create vmware api session id.
        Vmware api session id is used for authentication.
        :param client: Rest client.
        :type client: 'urllib3.poolmanager.PoolManager'
        :param hostname: Host name
        :type hostname: 'str'
        :param username: User name
        :type username: 'str'
        :param password: Password
        :type password: 'str'
        :raise :class:`urllib3.exceptions.HTTPError`
            If REST call response has a non HTTPStatus.OK status code.
        """
        logger.info("Creating vmware api session")

        url = vc_consts.SESSION_ID_URL % hostname
        basic_auth_header = urllib3.make_headers(basic_auth="{}:{}".format(username, password))

        # Make REST request
        response = client.request(method="POST", url=url, headers=basic_auth_header)

        # Raise urllib3.exceptions.HTTPError
        # If the HTTP request returns an unsuccessful status code
        SmartRestClient.raise_for_status(response, url)

        # Parse response for vmware api session id.
        content_dict = SmartRestClient.extract_json_data(response)
        vmware_api_session_id = content_dict["value"]
        headers = {vc_consts.VMWARE_API_SESSION_ID: vmware_api_session_id}

        logger.info("Successfully created vmware api session")
        return headers

    @staticmethod
    def _delete_session_by_hostname(client, hostname, session_headers):
        """
        Delete a session
        :param client: Rest client.
        :type client: 'urllib3.PoolManager'
        :param hostname: Host.
        :type hostname: 'str'
        :param session_headers: Rest call header of the to be deleted
            VMware API session ID
        :type session_headers: 'dict'
        """
        logger.info("Deleting vmware api session id")
        url = vc_consts.SESSION_ID_URL % hostname
        response = client.request(method="DELETE", url=url, headers=session_headers)
        logger.info(f"Response Code of 'DELETE' request on '{url}': {response.status}")
        logger.debug(f"Response content of 'DELETE' request on '{url}': {response.data}")
        if response.status == HTTPStatus.OK:
            logger.info(f"Delete vmware api session id succeeded. {str(session_headers)}")
        else:
            logger.warning(
                f"Failed to delete vmware api session id. "
                f"Session might have already expired. {str(session_headers)}"
            )

    def delete_vmware_api_session_id(self):
        """
        Make REST call to delete the vmware api session id.
        Vmware api session id is used for authentication.
        :raise :class:`urllib3.exceptions.RequestException`
            If REST call response reports failed.
        """
        self._rest_client_session.delete_session()

    def vcsa_request(self, url, method, **kwargs):
        """
        Invokes VCSA API request
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
            timeout = urllib3.Timeout(total=self.vc_rest_config.getint("APITimeoutSeconds"))

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
            logger.info("%s: 204 No Content", url)
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
        response = self.vcsa_request(url, method="GET", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def delete_helper(self, url, **kwargs):
        """
        Make a HTTP DELETE request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.vcsa_request(url, method="DELETE", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def post_helper(self, url, **kwargs):
        """
        Make a HTTP POST request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.vcsa_request(url, method="POST", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def put_helper(self, url, **kwargs):
        """
        Make a HTTP PUT request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """
        response = self.vcsa_request(url, method="PUT", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def patch_helper(self, url, **kwargs):
        """
        Make a HTTP PATCH request.
        :param url: Target http url
        :return: HTTPResponse, dict or str depends on kwargs.
        """

        response = self.vcsa_request(url, method="PATCH", **kwargs)
        return self._handle_response(url, response, **kwargs)

    @staticmethod
    def validate_cis_task_response(task_id: str, task_response: dict) -> dict:
        """
        Validate that the CIS task response and return CIS task value.
        :param task_id: CIS Task ID.
        :param task_response: CIS task response.
        :return: CIS task's value if valid, otherwise raise exception.
        """
        # Missing "value"
        if vc_consts.CIS_TASK_KEY_VALUE not in task_response:
            err_msg = (
                f"Key {vc_consts.CIS_TASK_KEY_VALUE} not found in CIS task response,"
                f"CIS task: {task_id} returned unexpected response"
            )
            raise err_msg
        value = task_response["value"]

        # Missing "status"
        if vc_consts.CIS_TASK_KEY_STATUS not in value:
            err_msg = (
                f"Key {vc_consts.CIS_TASK_KEY_STATUS} not found in CIS task response,"
                f"CIS task: {task_id} returned unexpected response"
            )
            raise err_msg

        return value

    def get_cis_task_info(self, task_id: str) -> dict:
        """
        Fetch the CIS task info for the given task_id
        :param task_id: Identifier of the task
        :return: Task info
        """
        url = self._base_url + vc_consts.CIS_TASKS_URL.format(task_id)
        return self.get_helper(url)

    def wait_for_cis_task_completion(self, task_id, timeout=None, retry_wait_time=None):
        """
        Wait for a timeout duration for the task to change to a terminal state.
        :type task_id: :class:'vim.task-id'
        :param task_id: task_id to wait.
        :type timeout: :class:'integer'
        :param timeout: wait timeout.
        :type retry_wait_time: :class:'integer'
        :param retry_wait_time: Time to wait between each retry
        :return: None
        """
        if not timeout:
            timeout = self.vc_rest_config.getint("TaskTimeoutSeconds")
        if not retry_wait_time:
            retry_wait_time = self.vc_rest_config.getint("TaskPollIntervalSeconds")
        retry_count = math.ceil(timeout / retry_wait_time) + 1
        for retry in range(retry_count):
            json_response = self.get_cis_task_info(task_id)
            value = self.validate_cis_task_response(task_id, json_response)
            status = value[vc_consts.CIS_TASK_KEY_STATUS]
            if status in vc_consts.CIS_TASK_TERMINAL_STATUS:
                return value
            elif status in vc_consts.CIS_TASK_ACTIVE_STATUS:
                if retry < retry_count - 1:
                    time.sleep(retry_wait_time)
                    logger.info(
                        f"Waiting for cis task completion for "
                        f"task_id:{task_id} Retry: {retry + 1}/{retry_count - 1}"
                    )
                else:
                    raise Exception(f"Task[{task_id}] timed out. Timeout duration [{timeout}s]")
            else:
                raise Exception(f"Task[{task_id}] returned an invalid status {status}")

    def set_vcsa_version(self):
        """
        Set VCSA version.

        return: None
        """
        self._vcsa_version = self.get_vcsa_version()
        logger.info(f"Setting the VCSA version to {self._vcsa_version} in the vc rest client")

    def get_vcsa_version(self):
        """
        Make REST call to get the version of vCenter,
        return version of the vCenter.

        :rtype :class:`str`
        :return: The version of the vCenter.
        :raise :class:`urllib3.exceptions`
            If REST call response reports failed.
        """
        if self._vcsa_version:
            return self._vcsa_version

        url = self._base_url + vc_consts.VC_SYSTEM_VERSION_URL

        # Make REST request
        response = self.get_helper(url)
        return response["version"]

    def get_base_url(self):
        return self._base_url

    def get_filtered_hosts_info(self, esxi_host_names=None):
        """
        Check on the vCenter and get the host info (name:moid map) for the context.host_names.
        :param esxi_host_names: List of esxi hostSystem.names
        :type esxi_host_names: list
        :return: Dict host_info with key as id(name) and value as host_moid.
        :rtype: dict
        :raises: Exception if VC API response is incorrect or if there are duplicate fqdn/names.
        """
        url = self.get_base_url() + vc_consts.LIST_HOSTS_URL
        try:
            response_list = self.get_helper(url)
        except Exception as e:
            logger.error(f"Error during retrieving list of hosts from vCenter {e}.")
            raise

        name_to_moids = {}
        error_names = []
        result_host_name_to_moid = {}

        # Iterate over all the items in the response list for the vcenter and build
        # dictionary of name to list of moids, host name to single moid, and error_names(occurrence with more than).
        for item in response_list:
            name = item.get("name")
            moid = item.get("host")
            if name is None or moid is None:
                raise Exception("Error fetching host name and moid.")
            if name in name_to_moids:
                name_to_moids[name].append(moid)
                error_names.append(name)
            else:
                name_to_moids[name] = [moid]
                result_host_name_to_moid[name] = moid

        # If ids is None, target is all the hosts in vCenter. Return result_host_name_to_moid if no error_names.
        # Else recreate the result_host_name_to_moid and error_names based on the input ids list.
        if esxi_host_names is not None:
            result_host_name_to_moid = {}
            error_names = []
            # Iterate over all input ids(names) and create a dict with key as name and value as host_moid
            for name in esxi_host_names:
                moids = name_to_moids.get(name, None)
                if moids and len(moids) > 1:
                    error_names.append(name)
                elif moids:
                    result_host_name_to_moid[name] = moids[0]
                else:
                    result_host_name_to_moid[name] = None

        if error_names:
            raise Exception(
                f"Multiple hosts with names {error_names} found in vCenter. Aborting operation. "
                f"Please resolve this before proceeding."
            )
        return result_host_name_to_moid
