# Copyright 2023-2024 VMware, Inc.  All rights reserved. -- VMware Confidential

from functools import partial
from http import HTTPStatus
import logging
import json
import requests
from base64 import b64encode

from config_modules_vmware.framework.clients.common.consts import JSON_REQUEST_HEADERS
from config_modules_vmware.framework.clients.nsxt import nsxt_consts
from config_modules_vmware.framework.clients.common import consts


# Set up logger
logger = logging.getLogger(__name__)


class NSXTManagerRestClient(object):
    """
    Class that exposes NSXT Manager REST APIs to handle API requests.
    """
    

    def nsxt_manager_request(self, url, method, **kwargs):
        """
        Invokes NSXT Manager API request
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
            headers = {**kwargs["headers"], **JSON_REQUEST_HEADERS }
        else:
            headers = JSON_REQUEST_HEADERS.copy()
        logger.debug(f"request kwargs: {kwargs}")
        return requests.request(method=method, url=url, **kwargs)


    def _handle_response(self, url, response, **kwargs):
        """
        Handle http response according to given kwargs
        :param url:
        :param response:
        :param kwargs:
            raise_for_status: True if want to raise exception when
                response status code is not 200, False otherwise.
        :return: HTTPResponse
        """
        if response.status_code == HTTPStatus.NO_CONTENT:
            logger.info(f"{url}: 204 No Content")
            return None
        raise_for_status = kwargs["raise_for_status"] if "raise_for_status" in kwargs else True
        if raise_for_status:
            response.raise_for_status()
        return response.json()

    def get(self, url, **kwargs):
        """
        Make a HTTP GET request.
        :param url: Target http url
        :return: HTTPResponse.
        """
        response = self.nsxt_manager_request(url, method="GET", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def delete(self, url, **kwargs):
        """
        Make a HTTP DELETE request.
        :param url: Target http url
        :return: HTTPResponse.
        """
        response = self.nsxt_manager_request(url, method="DELETE", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def post(self, url, **kwargs):
        """
        Make a HTTP POST request.
        :param url: Target http url
        :return: HTTPResponse
        """
        response = self.nsxt_manager_request(url, method="POST", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def put(self, url, **kwargs):
        """
        Make a HTTP PUT request.
        :param url: Target http url
        :return: HTTPResponse
        """
        response = self.nsxt_manager_request(url, method="PUT", **kwargs)
        return self._handle_response(url, response, **kwargs)

    def patch(self, url, **kwargs):
        """
        Make a HTTP PATCH request.
        :param url: Target http url
        :return: HTTPResponse,
        """

        response = self.nsxt_manager_request(url, method="PATCH", **kwargs)
        return self._handle_response(url, response, **kwargs)

   