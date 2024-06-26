# Copyright 2024 Broadcom. All Rights Reserved.
import os
from enum import Enum

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.sddc_manager_context import SDDCManagerContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext
from functional_tests.utils.control_util import get_ssl_thumbprint_sha1

CREDENTIAL = "v1/credentials?"
RESOURCE_TYPE = "resourceType="
CREDENTIAL_TYPE = "&credentialType="
ACCOUNT_TYPE = "&accountType="


class Credential:
    """
    Ssh Credential used to connect appliance for local control validation
    :param hostname: hostname
    :type hostname: :class:'str'
    :param username: username
    :type username: :class:'str'
    :param password: Password
    :type password: :class:'str'
    """

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        self._username = username
        self._password = password

    @property
    def hostname(self):
        """Get host name.
        :return: host name.
        :rtype: class:'str'
        """
        return self._hostname

    @property
    def username(self):
        """Get username.
        :return: username.
        :rtype: class:'str'
        """
        return self._username

    @property
    def password(self):
        """Get password.
        :return: password.
        :rtype: class:'str'
        """
        return self._password


class CredentialApiClient:
    """
    Responsible for getting the VCF appliance Credential information using SDDC Manager
    """

    def __init__(self, sddc_manager_context):
        """
        Initialized the vcf jwt token api client and setting the host to
        be the vcf host name. This api client is used for
        connecting to CredentialsApi
        """
        self.apiClient = sddc_manager_context.sddc_manager_rest_client()

    class CredentialTypeEnum(Enum):
        """
        Enum class for Credential Type.
        """

        SSO = "SSO"
        SSH = "SSH"
        API = "API"

    class ResourceTypeEnum(Enum):
        """
        Enum class for resource type.
        """

        ESXI = "ESXI"
        VCENTER = "VCENTER"
        NSXT_MANAGER = "NSXT_MANAGER"
        NSXT_EDGE = "NSXT_EDGE"
        PSC = "PSC"
        VRSLCM = "VRSLCM"

    class AccountTypeEnum(Enum):
        """
        Enum class for resource type.
        """

        USER = "USER"
        SERVICE = "SERVICE"
        SYSTEM = "SYSTEM"

    def get_credentials(
        self,
        credential_type: CredentialTypeEnum = None,
        resource_type: ResourceTypeEnum = None,
        account_type: AccountTypeEnum = None,
    ):
        """Get VCF SDDC appliance sso credentials.
        :param credential_type: resource type
        :type credential_type: ResourceEnum
        :param resource_type: resource type
        :type resource_type: ResourceEnum
        :param account_type: account type
        :type account_type: AccountEnum
        :return: Tuple of dict with key "Appliance Enum" and dictionary of credentials .
        :rtype: tuple
        """

        url = self.apiClient.get_base_url() + CREDENTIAL
        if resource_type:
            url += RESOURCE_TYPE + resource_type.name
        if credential_type:
            url += CREDENTIAL_TYPE + credential_type.name
        if account_type:
            url += ACCOUNT_TYPE + account_type.name

        errors = []
        credential_resp = {}
        try:
            credential_resp = self.apiClient.get_helper(url)

        except Exception as e:
            errors.append(str(e))
            credential_resp["elements"] = None
        return credential_resp["elements"], errors


def _get_ssh_credential(credential_api_client, resource_type, credential_type):
    ssh_credentials, errors = credential_api_client.get_credentials(
        resource_type=resource_type, credential_type=credential_type
    )
    credentials = set()
    if len(errors) == 0:
        for ssh_credential in ssh_credentials:
            if ssh_credential and ssh_credential["credentialType"] == "SSH":
                host_ip = ssh_credential["resource"]["resourceIp"]
                credentials.add(
                    Credential(
                        hostname=host_ip,
                        username=ssh_credential.get("username"),
                        password=ssh_credential.get("password"),
                    )
                )
    return credentials


def get_ssh_credentials(sddc_manager_context):
    ssh_credential_dict = {}
    credential_api_client = CredentialApiClient(sddc_manager_context)
    prod_enum = BaseContext.ProductEnum
    ssh_credential_dict[prod_enum.VCENTER] = _get_ssh_credential(
        credential_api_client, CredentialApiClient.ResourceTypeEnum.VCENTER, CredentialApiClient.CredentialTypeEnum.SSH
    )
    ssh_credential_dict[prod_enum.NSXT_MANAGER] = _get_ssh_credential(
        credential_api_client,
        CredentialApiClient.ResourceTypeEnum.NSXT_MANAGER,
        CredentialApiClient.CredentialTypeEnum.SSH,
    )
    ssh_credential_dict[prod_enum.NSXT_EDGE] = _get_ssh_credential(
        credential_api_client,
        CredentialApiClient.ResourceTypeEnum.NSXT_EDGE,
        CredentialApiClient.CredentialTypeEnum.SSH,
    )
    ssh_credential_dict[prod_enum.VRSLCM] = _get_ssh_credential(
        credential_api_client, CredentialApiClient.ResourceTypeEnum.VRSLCM, CredentialApiClient.CredentialTypeEnum.SSH
    )
    return ssh_credential_dict


def get_sddc_manager_context():
    return SDDCManagerContext(
        hostname=os.getenv("SM_HOST"),
        username=os.getenv("SM_USERNAME"),
        password=os.getenv("SM_PASSWORD"),
        ssl_thumbprint=get_ssl_thumbprint_sha1(os.getenv("SM_HOST")),
    )


def get_vrslcm_contexts(credential_api_client):
    vrslcm_api_credentials, errors = credential_api_client.get_credentials(
        resource_type=CredentialApiClient.ResourceTypeEnum.VRSLCM,
        credential_type=CredentialApiClient.CredentialTypeEnum.SSH,
    )
    # Create Nsx manager contexts
    vrslcm_contexts = {}
    if len(errors) == 0:
        for vrslcm_api_credential in vrslcm_api_credentials:
            if vrslcm_api_credential:
                vrslcm_ip = vrslcm_api_credential["resource"]["resourceIp"]
                vrslcm_contexts[vrslcm_ip] = VrslcmContext(hostname=vrslcm_ip)
    return vrslcm_contexts


def get_vc_contexts(credential_api_client):
    vc_sso_credentials, errors = credential_api_client.get_credentials(
        resource_type=CredentialApiClient.ResourceTypeEnum.PSC,
        credential_type=CredentialApiClient.CredentialTypeEnum.SSO,
    )
    # Create vcenter contexts
    vc_contexts = {}
    if len(errors) == 0:
        for vc_sso_credential in vc_sso_credentials:
            if vc_sso_credential:
                vc_ip = vc_sso_credential["resource"]["resourceIp"]
                vc_contexts[vc_ip] = VcenterContext(
                    hostname=vc_ip,
                    username=vc_sso_credential.get("username"),
                    password=vc_sso_credential["password"],
                    ssl_thumbprint=get_ssl_thumbprint_sha1(vc_ip),
                )
    return vc_contexts


context_func_dict = {
    BaseContext.ProductEnum.SDDC_MANAGER: get_sddc_manager_context,
    BaseContext.ProductEnum.VCENTER: get_vc_contexts,
    BaseContext.ProductEnum.VRSLCM: get_vrslcm_contexts,
}


def get_contexts():
    sddc_manager_context = get_sddc_manager_context()
    context_dict = {BaseContext.ProductEnum.SDDC_MANAGER: {sddc_manager_context.hostname: sddc_manager_context}}
    credential_api_client = CredentialApiClient(sddc_manager_context)
    context_dict[BaseContext.ProductEnum.VCENTER] = get_vc_contexts(credential_api_client)
    context_dict[BaseContext.ProductEnum.VRSLCM] = get_vrslcm_contexts(credential_api_client)
    context_dict[BaseContext.ProductEnum.NSXT_MANAGER] = BaseContext(BaseContext.ProductEnum.NSXT_MANAGER)
    context_dict[BaseContext.ProductEnum.NSXT_EDGE] = BaseContext(BaseContext.ProductEnum.NSXT_EDGE)
    return context_dict


def get_context(product: BaseContext.ProductEnum, hostname):
    if product == BaseContext.ProductEnum.SDDC_MANAGER:
        return context_func_dict[product]()
    else:
        sddc_manager_context = context_func_dict[BaseContext.ProductEnum.SDDC_MANAGER]()
        credential_api_client = CredentialApiClient(sddc_manager_context)
        contexts = context_func_dict[product](credential_api_client)
        if hostname in contexts:
            return contexts[hostname]

        for key in contexts:
            return contexts[key]
