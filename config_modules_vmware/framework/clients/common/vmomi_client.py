# Copyright 2024 Broadcom. All Rights Reserved.
import ssl
from functools import partial

from pyVmomi import SessionOrientedStub  # pylint: disable=E0401
from pyVmomi import SoapStubAdapter  # pylint: disable=E0401
from pyVmomi import vim  # pylint: disable=E0401
from pyVmomi import vmodl  # pylint: disable=E0401


class VmomiClient(object):
    """
    A VMOMI client class.
    Creates a SessionOrientedStub for connecting
    """

    def __init__(
        self,
        hostname="localhost",
        port=443,
        url=None,
        protocol="https",
        thumbprint=None,
        ssl_context=None,
        parent_client=None,
        get_session_obj_for_child_func=None,
        session_login_func=None,
        session_logout_func=None,
        path="/sdk",
        version="vim.version.version11",
        pool_size=5,
        saml_token=None,
    ):
        """
        Class constructor.

        :param hostname: target ip
        :type hostname: :class:'str'
        :param port: target port. Any valid positive TCP port
        :type port: :class:'int'
        :param url: URL (overrides host, port, path if set)
        :type url: :class:'str'
        :param protocol: RPC protocol. e.g., "https"
        :type protocol: :class:'str'
        :param thumbprint: thumbprint of server cert
        :type thumbprint: :class:'str'
        :param ssl_context: ssl context. default is no cert validation
        :type ssl_context: :class:'SSLContext'
        :param parent_client: the vmomi client of the service that
            current vmmomi client depends on.
        :type parent_client: :class:'VmomiClient'
        :param session_login_func: login function for session: function name
        :type session_login_func: function
        :param session_logout_func: logout function for session: function name
        :type session_logout_func: function
        :param path: vmomi path. e.g., "/ls/sdk": str
        :type path: :class:'str'
        :param version: vmodl version. e.g., 'cis.license.version.version2': str
        :type version: :class:'str'
        :param saml_token: SAML token used to connect to vCenter
        :type saml_token: :class:'str'
        """
        self._hostname = hostname
        self._port = port
        self._url = url
        self._protocol = protocol
        self._thumbprint = thumbprint
        self._ssl_context = ssl_context
        self._session_login_func = session_login_func
        self._session_logout_func = session_logout_func

        self._path = path
        self._version = version
        self._pool_size = pool_size

        self.child_clients = list()
        self._stub = None
        self.parent_client = None
        self._saml_token = saml_token

        if parent_client:
            # For child client (vum, sms, pbm; vsan, eam)
            self.parent_client = parent_client
            self.parent_client.child_clients.append(self)

            self._update_session_func = session_login_func
            self._session_login_func = partial(VmomiClient._child_login_method, client=self)
        else:
            # For parent client (vc) or non-session client
            self._session_login_func = partial(
                VmomiClient._parent_login_method,
                client=self,
                login_method=session_login_func,
                get_session_obj_for_child_func=get_session_obj_for_child_func,
            )

    @staticmethod
    def _child_login_method(soap_stub, client):  # pylint: disable=W0613
        """
        The soap_stub passed in will be a child client's soapStub.
        But it will not be used as we are calling parent client's
        login method which uses parent client's _stub

        :param soap_stub: The communication substrate for the client
            which is supposed to have a parent client.
        :type soap_stub: 'SoapStubAdapter'
        :param client: The client who is trying to create login method.
        :type client: :class:'VmomiClient'
        """
        client.parent_client._session_login_func(client.parent_client.get_soap_stub())

    @staticmethod
    def _parent_login_method(soap_stub, client, login_method, get_session_obj_for_child_func):
        """
        The soap_stub passed in will be a parent client's soapStub.
        But it will not be used as we are calling parent client's
        login method which uses parent client's _stub

        :param soap_stub: The communication substrate for the client.
        :type soap_stub: 'SoapStubAdapter'
        :param client: The client who is trying to create login method.
        :type client: :class:'VmomiClient'
        :param login_method: The login method to call when session timed out.
        :type login_method: :class:'function'
        """
        if not login_method:
            # For non-session client, directly return
            return

        # Login for parent(vc) session
        login_method(soap_stub)

        parent_session_obj = None
        if get_session_obj_for_child_func:
            parent_session_obj = get_session_obj_for_child_func(soap_stub)

        # Update cookie/session of services (vum, sms, pbm; vsan, eam)
        # that depends on parent(vc)'s session
        for child_client in client.child_clients:
            child_client.update_child_session(parent_session_obj)

    def update_child_session(self, parent_session_obj):
        """
        Suppose to be used by child client (vum, sms, pbm; vsan, eam)
        for updating its session based on parent client session (vc)
        """
        if self.parent_client:
            if self._update_session_func:
                # For child client like vum, sms, pbm
                self._update_session_func(parent_session_obj, self.get_soap_stub())
            else:
                # For child client like vsan, eam
                self._stub.soapStub.cookie = parent_session_obj["cookie"]

    def _create_stub(self):
        """
        Create a soap stub
        :return: soap stub
        :rtype: 'SoapStubAdapter'
        """
        if not self._ssl_context:
            ssl_context = ssl._create_unverified_context()  # nosec
        else:
            ssl_context = self._ssl_context

        # SoapStubAdapter treats negative port number as a "HTTP" connection
        # and positive port number as a "HTTPS" connection. VmomiClient treats
        # all TCP ports to be positive and use "_protocol" parameter
        # to distinguish protocols.
        _port_number = -int(self._port) if self._protocol == "http" else int(self._port)

        stub = SoapStubAdapter(
            host=self._hostname,
            port=_port_number,
            url=self._url,
            version=self._version,
            thumbprint=self._thumbprint,
            sslContext=ssl_context,
            poolSize=self._pool_size,
            samlToken=self._saml_token,
            connectionPoolTimeout=5,
        )
        return stub

    def connect(self):
        """
        Connect to a vmomi service with a SessionOrientedStub.
        :return: None
        """
        _soap_stub = self._create_stub()

        if self._session_login_func:
            self._stub = SessionOrientedStub(_soap_stub, self._session_login_func)
            self._stub.SESSION_EXCEPTIONS = (
                vim.fault.NotAuthenticated,  # The exception when VC timed out
                vmodl.fault.SecurityError,  # The exception when VUM timed out
            )
        else:
            # Should never come here though
            self._stub = _soap_stub

    def disconnect(self):
        """
        disconnect the service
        :return: None
        """
        if self._session_logout_func:
            self._session_logout_func(self.get_soap_stub())

    def get_soap_stub(self):
        """
        Get the original SoapStubAdapter from SessionOrientedStub.
        """
        if isinstance(self._stub, SessionOrientedStub):
            return self._stub.soapStub
        else:
            return self._stub

    def get_managed_object(self, managed_object, managed_object_name):
        """
        Get a VMOMI managed object as specified by the object type and name.
        :param managed_object: a managed object class,
                e.g., Cis.license.SessionManagementService
        :type managed_object: A VMOMI object type
        :param managed_object_name: a reference id,
                e.g., 'cis.license.SessionManagementService'
        :type managed_object_name: :class:'str'
        :return: managed object
        :rtype: VMOMI object
        """
        if self._stub:
            return managed_object(managed_object_name, self._stub)
