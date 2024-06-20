# Copyright 2024 Broadcom. All Rights Reserved.
import inspect
import json
import logging
from functools import partial
from http import HTTPStatus
from threading import Lock

import urllib3

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.services.config import Config

BODY = "body"
HEADERS = "headers"

logger = LoggerAdapter(logging.getLogger(__name__))


def get_smart_rest_client_class(urllib3_manager):
    class BaseRestClient(urllib3_manager):
        """
        Class to provide REST API method helpers with session timeout handling.
        """

        def __init__(
            self,
            get_session_headers_func=None,
            delete_session_func=None,
            retries=None,
            ssl_version=consts.TLS_VERSION,
            ca_cert_dir=consts.SSL_VERIFY_CA_PATH,
            **kwargs,
        ):
            """
            Constructor of the class.

            1. Cert dir is taken care of being set in here instead of
               every REST call, but the default value can be overwritten.
            2. If thumbprint is provided, and cert validation is not asked,
               cert dir is not passed to the init of the base class,
               only use thumbprint for validation.
            3. If specifically asked not to validate certificate (CERT_NONE),
               the cert dir is not passed to the init of the base class,
            4. If both thumbprint and cert validation are asked,
               both will be validated.
            5. If thumbprint is not provided and specifically asked
               not to validate certificate (CERT_NONE),
               neither will be validated.

            :param get_session_headers_func:
                    A function object with a parameter "client" and a return
                    value of "dict". The return value is merged with
                    "headers" of the request.
            :type get_session_headers_func: 'function'
            :param delete_session_func: A function object
                that invalidates a session with
                a "client" parameter for rest client and
                a "session_headers" parameter for passing in
                created session headers.
            :type delete_session_func: 'function'
            :param retries: Retries setting.
            :type retries: 'urllib3.util.retry.Retry'
            """
            if not retries:
                rest_retry_config = Config.get_section("rest.retry")
                retries = urllib3.Retry(
                    total=None,
                    connect=rest_retry_config.getint("Connect"),
                    read=rest_retry_config.getint("Read"),
                    redirect=rest_retry_config.getint("Redirect"),
                    status=rest_retry_config.getint("Status"),
                    other=rest_retry_config.getint("Other"),
                    status_forcelist=(
                        [int(status) for status in rest_retry_config["StatusForceList"].split(",")]
                        if rest_retry_config["StatusForceList"]
                        else None
                    ),
                    backoff_factor=rest_retry_config.getfloat("BackoffFactor"),
                )

            cert_validation_asked = "cert_reqs" in kwargs and kwargs["cert_reqs"] == consts.CERT_REQUIRED

            if ("assert_fingerprint" in kwargs and not cert_validation_asked) or (
                "cert_reqs" in kwargs and kwargs["cert_reqs"] == consts.CERT_NONE
            ):
                # Cert dir is not used for validation
                if "cert_reqs" not in kwargs:
                    kwargs["cert_reqs"] = consts.CERT_NONE
                super(BaseRestClient, self).__init__(retries=retries, ssl_version=ssl_version, **kwargs)
            else:
                # Cert dir is used for validation
                super(BaseRestClient, self).__init__(
                    retries=retries, ssl_version=ssl_version, ca_cert_dir=ca_cert_dir, **kwargs
                )

            # Validate signature of delete_session_func
            if delete_session_func:
                if isinstance(delete_session_func, partial):
                    args = inspect.getfullargspec(delete_session_func.func).args
                    func_name = delete_session_func.func.__name__
                else:
                    args = inspect.getfullargspec(delete_session_func).args
                    func_name = delete_session_func.__name__
                if "client" not in args or "session_headers" not in args:
                    error_msg = (
                        f"Function '{func_name}' doesn't have required parameter " f"'client' or 'session_headers'"
                    )
                    logger.error(error_msg)
                    raise Exception(error_msg)

            self._get_session_headers_func = get_session_headers_func
            self._delete_session_func = delete_session_func
            self._session_headers = None
            self._session_lock = Lock()

        def head(self, url, **kwargs):
            """
            HEAD request
            :param url: URL of the request.
            :type url: 'str'
            :param kwargs: Parameters used by the request.
            :type kwargs: 'dict'
            :return: Response.
            :rtype: 'HTTPResponse'
            """
            return self.request(method="HEAD", url=url, **kwargs)

        def get(self, url, **kwargs):
            """
            GET request
            :param url: URL of the request.
            :type url: 'str'
            :param kwargs: Parameters used by the request.
            :type kwargs: 'dict'
            :return: Response.
            :rtype: 'HTTPResponse'
            """
            return self.request(method="GET", url=url, **kwargs)

        def post(self, url, **kwargs):
            """
            POST request
            :param url: URL of the request.
            :type url: 'str'
            :param kwargs: Parameters used by the request.
            :type kwargs: 'dict'
            :return: Response.
            :rtype: 'HTTPResponse'
            """
            return self.request(method="POST", url=url, **kwargs)

        def put(self, url, **kwargs):
            """
            PUT request
            :param url: URL of the request.
            :type url: 'str'
            :param kwargs: Parameters used by the request.
            :type kwargs: 'dict'
            :return: Response.
            :rtype: 'HTTPResponse'
            """
            return self.request(method="PUT", url=url, **kwargs)

        def delete(self, url, **kwargs):
            """
            DELETE request
            :param url: URL of the request.
            :type url: 'str'
            :param kwargs: Parameters used by the request.
            :type kwargs: 'dict'
            :return: Response.
            :rtype: 'HTTPResponse'
            """
            return self.request(method="DELETE", url=url, **kwargs)

        def patch(self, url, **kwargs):
            """
            PATCH request
            :param url: URL of the request.
            :type url: 'str'
            :param kwargs: Parameters used by the request.
            :type kwargs: 'dict'
            :return: Response.
            :rtype: 'HTTPResponse'
            """
            return self.request(method="PATCH", url=url, **kwargs)

        def request(self, method, url, get_session_headers_func=None, **kwargs):
            """
            A request method with session timeout handling.
            :param method: HTTP method.
            :type method: 'str'
            :param url: HTTP URL.
            :type url: 'str'
            :param get_session_headers_func: A function object with a parameter
                                             "client" that gets the session header.
            :type get_session_headers_func: 'function'
            :param kwargs: Parameters passed to the method in the parent class.
            :type kwargs: 'dict'
            :return: HTTP response
            :rtype: 'HTTPResponse'
            """
            if get_session_headers_func is None:
                get_session_headers_func = self._get_session_headers_func

            for i in range(2):
                # Creates session headers if not exist
                self._update_session_headers(get_session_headers_func, kwargs)

                data = kwargs[BODY] if BODY in kwargs else ""
                logger.info(f"Calling '{method}':'{url}'")
                logger.debug(f"Data for '{method}' request to '{url}': {data}")

                response = super(BaseRestClient, self).request(method=method, url=url, **kwargs)
                logger.info(f"Response Code of '{method}' request on '{url}': {response.status}")
                logger.debug(f"Response content of '{method}' request on '{url}': {response.data}")

                if response.status == 401 and i < 1 and get_session_headers_func:
                    logger.info("Session might have timed out. Re-establish.")
                    with self._session_lock:
                        if self._session_headers:
                            self._session_headers = None
                        else:
                            return response
                else:
                    return response

        def _update_session_headers(self, get_session_headers_func, kwargs):
            """
            Update session headers. If session headers do not exist,
            create a one.
            :param get_session_headers_func: A function object with a parameter
                "client" that invalidates a session.
            :type get_session_headers_func: 'function'
            :param kwargs: Request parameters.
            :type kwargs: 'dict'
            """
            if get_session_headers_func:
                with self._session_lock:
                    if self._session_headers is None:
                        self._session_headers = get_session_headers_func(client=super(BaseRestClient, self))
                    if self._session_headers and isinstance(self._session_headers, dict):
                        if HEADERS not in kwargs:
                            kwargs[HEADERS] = dict()
                        kwargs[HEADERS].update(self._session_headers)
                    else:
                        raise urllib3.exceptions.HTTPError("Invalid session headers")

        def delete_session(self):
            """
            Delete a session.
            """
            with self._session_lock:
                if self._session_headers is None:
                    return
                if self._delete_session_func:
                    self._delete_session_func(client=super(BaseRestClient, self), session_headers=self._session_headers)
                self._session_headers = None

        def has_session(self):
            """
            Check if a session exists.
            :return True if session exists.
            :rtype 'bool'
            """
            with self._session_lock:
                return self._session_headers is not None

        def retrieve_json(self, url, username=None, password=None):
            """
            Retrieve a json file from a URL endpoint and return a json object.

            :param url: URL endpoint.
            :type url: 'str'
            :param username: User name.
            :type username: 'str'
            :param password: Password.
            :type password: 'str'
            :raise :class:`Error`
                If REST call response has a non 200 status code
            :return: Object representing json.
            :rtype: 'dict'
            """
            basic_auth_header = dict()
            if username and password:
                basic_auth_header = urllib3.make_headers(basic_auth="{}:{}".format(username, password))

            # Make REST request
            response = self.get(url=url, headers=basic_auth_header, timeout=consts.SECS_IN_2_MINS)

            # Raise vAPI Error
            # If the HTTP request returns an unsuccessful status code
            if response.status != HTTPStatus.OK:
                error_msg = "software.http.get.json.file.failed"
                logger.error(error_msg)
                err = Exception(error_msg)
                raise err

            # Extract Json data from the response
            try:
                return BaseRestClient.extract_json_data(response)
            except Exception as err:
                error_msg = "software.http.retrieve.json.from.url.failed"
                logger.error(error_msg)
                err = Exception(error_msg)
                raise err

        @staticmethod
        def decode_data(response):
            """
            Decode response data.
            :param response: Response.
            :type response: 'Response'
            :return: decoded data.
            :rtype 'str'
            """
            try:
                return response.data.decode(BaseRestClient.get_encoding(response))
            except Exception as err:
                err_msg = f"Failed to decode response: {str(err)}"
                logger.error(err_msg)
                raise Exception(err_msg) from err

        @staticmethod
        def extract_json_data(response):
            """
            Extract JSON data if response is JSON data.
            :param response: Response.
            :type response: 'Response'
            :return: Object representing json.
            :rtype: 'dict'
            """
            response_in_json_str = BaseRestClient.decode_data(response)
            try:
                return json.loads(response_in_json_str)
            except Exception as err:
                err_msg = (
                    f"Failed to parse Json response. Invalid Json: {str(response_in_json_str)}. " f"Error: {str(err)}"
                )
                logger.error(err_msg)
                raise Exception(err_msg) from err

        @staticmethod
        def raise_for_status(response, url):
            """
            Raises :class:`HTTPError` for 400s and 500s status codes.
            """
            http_error_msg = ""
            if isinstance(response.reason, bytes):
                try:
                    reason = response.reason.decode("utf-8")
                except UnicodeDecodeError:
                    reason = response.reason.decode("iso-8859-1")
            else:
                reason = response.reason

            if 400 <= response.status < 500:
                http_error_msg = f"{response.status} Client Error: {reason} for url: {url}"

            elif 500 <= response.status < 600:
                http_error_msg = f"{response.status} Server Error: {reason} for url: {url}"

            if http_error_msg:
                raise urllib3.exceptions.HTTPError(http_error_msg)

        @staticmethod
        def get_encoding(response):
            """
            Extract encoding.
            :param response: Response.
            :type response: 'Response'
            :return: Encoding.
            :rtype: 'str'
            """
            content_type = response.headers.get("Content-Type")
            if content_type:
                parts = content_type.split(";")
                if len(parts) == 2:
                    kv = parts[1].strip()
                    parts = kv.split("=")
                    if len(parts) == 2 and parts[0].lower() == "charset":
                        return parts[1].strip('"')
            return "utf-8"

    return BaseRestClient


SmartRestClient = get_smart_rest_client_class(urllib3.PoolManager)
SmartRestClientProxy = get_smart_rest_client_class(urllib3.ProxyManager)


def get_smart_rest_client(proxy_url=None, **kwargs):
    if proxy_url:
        return SmartRestClientProxy(proxy_url=proxy_url, **kwargs)
    else:
        return SmartRestClient(**kwargs)
