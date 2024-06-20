#!/usr/bin/env python
# Copyright 2024 Broadcom. All Rights Reserved.
"""
Implementation of the Vc drivers to perform sso operations.
"""
import logging
import ssl

from config_modules_vmware.framework.clients.common.consts import SSL_VERIFY_CA_PATH
from config_modules_vmware.framework.clients.common.consts import SSO_PATH
from config_modules_vmware.framework.clients.common.consts import SSO_SERVICE_INSTANCE
from config_modules_vmware.framework.clients.common.consts import SSO_TLS_VERSION
from config_modules_vmware.framework.clients.common.consts import STS_PATH
from config_modules_vmware.framework.clients.vcenter.dependencies.pyVim import sso as sts
from config_modules_vmware.framework.clients.vcenter.dependencies.pyVmomi import SoapStubAdapter
from config_modules_vmware.framework.clients.vcenter.dependencies.pyVmomi import sso
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.services.config import Config

# The query limit of 32767 is picked from previous implementation in VMC. We are in process of getting sign off from
# product team on this.
USER_QUERY_LIMIT = 32767

# Set up logger
logger = LoggerAdapter(logging.getLogger(__name__))


class VcVmomiSSOClient(object):
    """
    Class that provides VC SSO services.
    """

    def __init__(
        self, hostname, user, pwd, port=443, ssl_thumbprint=None, version="sso.version.version3_2", verify_ssl=True
    ):
        """
        Connects to the Vc SSO service

        :param hostname: Vcenter hostname.
        :param user: Admin username.
        :param pwd: Password for the SSO admin.
        :param port: Port number.
        :param ssl_thumbprint: SHA 256 thumbprint.
        :param version: Requires the 3.2 version for the GetAuthnPolicy APIs.
        :param domain: domain or identity source in which user has to be
                       created such as 'vmc.local'.
        :param verify_ssl: Flag to enable/disable SSL verification.
        """
        self.content = None
        self._stub = None
        self.vc_name = hostname
        self.user = user
        self.pwd = pwd
        self.port = port
        self.ssl_thumbprint = ssl_thumbprint
        self.version = version
        self.verify_ssl = verify_ssl
        self.domain = user.split("@")[-1]
        self.vc_vmomi_sso_config = Config.get_section("vcenter.vmomi.sso")
        self.connect()

    def connect(self):
        """
        Connect to the vCenter Server STS endpoint.
        :return: None
        """
        sts_url = STS_PATH.format(self.vc_name, self.domain)
        auth = sts.SsoAuthenticator(sts_url)
        ssl_ctx = ssl.SSLContext(protocol=SSO_TLS_VERSION)
        if not self.verify_ssl:
            logger.info("Skipping SSL certificate verification")
            ssl_ctx.verify_mode = ssl.CERT_NONE
            self.ssl_thumbprint = None
        elif self.ssl_thumbprint:
            logger.info("Verifying using thumbprint")
            ssl_ctx.verify_mode = ssl.CERT_NONE
        else:
            logger.info("Verifying server certificates")
            ssl_ctx.verify_mode = ssl.CERT_REQUIRED
            ssl_ctx.load_verify_locations(capath=SSL_VERIFY_CA_PATH)
        sso_path = SSO_PATH.format(self.domain)

        logger.info(
            "pyVmomi.SoapStubAdapter host=%s port=%d path=%s sslContext=%s version=%s",
            self.vc_name,
            self.port,
            sso_path,
            ssl_ctx,
            self.version,
        )
        token = auth.get_bearer_saml_assertion(
            self.user,
            self.pwd,
            token_duration=self.vc_vmomi_sso_config.getint("SAMLTokenDurationSeconds"),
            ssl_context=ssl_ctx,
        )
        self._stub = SoapStubAdapter(
            host=self.vc_name,
            port=self.port,
            path=sso_path,
            thumbprint=self.ssl_thumbprint,
            sslContext=ssl_ctx,
            samlToken=token,
            version=self.version,
        )
        sso_admin = sso.admin.ServiceInstance(SSO_SERVICE_INSTANCE, self._stub)
        self.content = sso_admin.RetrieveServiceContent()

    def disconnect(self):
        """
        Disconnect the SSO service instance.
        :return: None
        """
        if self._stub:
            self._stub.DropConnections()
        logger.info("Disconnected from SSO")
        self._stub = None

    def set_password_lifetime_days(self, days=None):
        """
        Set the global password policy.
        :type days: 'int'
        :param days: Password validity in days. None implies infinite time.
        :return: None
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        policy.passwordLifetimeDays = days
        logger.info("vim.sso.admin.passwordPolicyService.UpdateLocalPasswordPolicy policy=%s", policy)
        self.content.passwordPolicyService.UpdateLocalPasswordPolicy(policy)

    def get_password_lifetime_days(self):
        """
        Get the global password policy.
        :return: Get value of policy.passwordLifetimeDays
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        return policy.passwordLifetimeDays

    def get_password_reuse_restriction(self):
        """
        Get the global passwordApolicy.
        :return: Get value of policy.passwordLifetimeDays
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        return policy.prohibitedPreviousPasswordsCount

    def set_password_reuse_restriction(self, restrict_count=None):
        """
        Set the global password policy.
        :type days: 'int'
        :param days: Password validity in days. None implies infinite time.
        :return: None
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        policy.prohibitedPreviousPasswordsCount = restrict_count
        logger.info("vim.sso.admin.passwordPolicyService.UpdateLocalPasswordPolicy policy=%s", policy)
        self.content.passwordPolicyService.UpdateLocalPasswordPolicy(policy)

    def _get_group(self, groupname, domain):
        """
        Return the group info object.

        :type groupname: 'str'
        :param groupname: Name of group
        :type domain: 'str'
        :param domain: Domain name
        :return: Group info attribute.
        """
        pid = sso.PrincipalId(name=groupname, domain=domain)
        logger.info(f"vim.sso.admin.principalDiscoveryService.FindGroup. pID: '{pid}'")
        group_info = self.content.principalDiscoveryService.FindGroup(pid)
        return group_info

    def get_a_group_id(self, name, domain):
        """
        Creates a user group.

        :type name: 'str'
        :param name: Name of group such as 'CloudAdminGroup'
        :type desc: 'str'
        :param desc: Description
        :type domain: 'str'
        :param domain: Domain name such as 'vmc.local'
        :return: Group Id of the created group.
        """
        groups = self._get_group(name, domain)
        if groups and groups.id:
            return groups.id

    def enforce_minimum_password_length(self, length=None):
        """
        Set the global password policy.
        :type length: 'int'
        :param length: Minimum length of password.
        :return: None
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        policy.passwordFormat.lengthRestriction.minLength = length
        logger.info("vim.sso.admin.passwordPolicyService.UpdateLocalPasswordPolicy policy=%s", policy)
        self.content.passwordPolicyService.UpdateLocalPasswordPolicy(policy)

    def get_minimum_password_length(self):
        """
        Get the global password policy.
        :return: Value of policy.passwordFormat.lengthRestriction.minLength
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        return policy.passwordFormat.lengthRestriction.minLength

    def get_max_failed_login_attempts(self):
        """
        Set the global lockout policy.
        :return: Value of policy.maxFailedAttempts
        """
        logger.info("vim.sso.admin.lockoutPolicyService.GetLockoutPolicy")
        policy = self.content.lockoutPolicyService.GetLockoutPolicy()
        return policy.maxFailedAttempts

    def set_max_failed_login_attempts(self, attempts=None):
        """
        Set the global lockout policy.
        :type attempts: 'int'
        :param attempts: Max failed login attempts. None implies infinite time.
        :return: None
        """
        logger.info("vim.sso.admin.lockoutPolicyService.GetLockoutPolicy")
        policy = self.content.lockoutPolicyService.GetLockoutPolicy()
        policy.maxFailedAttempts = attempts
        logger.info("vim.sso.admin.lockoutPolicyService.UpdateLockoutPolicy policy=%s", policy)
        self.content.lockoutPolicyService.UpdateLockoutPolicy(policy)

    def set_interval_between_login_failures(self, interval=None):
        """
        Set the global lockout policy.
        :type interval: 'int'
        :param interval: Permitted time between login failures.
        :return: None
        """
        logger.info("vim.sso.admin.lockoutPolicyService.GetLockoutPolicy")
        policy = self.content.lockoutPolicyService.GetLockoutPolicy()
        policy.failedAttemptIntervalSec = interval
        logger.info("vim.sso.admin.lockoutPolicyService.UpdateLockoutPolicy policy=%s", policy)
        self.content.lockoutPolicyService.UpdateLockoutPolicy(policy)

    def get_interval_between_login_failures(self):
        """
        Get the global lockout policy.
        :return: Value of policy.failedAttemptIntervalSec
        """
        logger.info("vim.sso.admin.lockoutPolicyService.GetLockoutPolicy")
        policy = self.content.lockoutPolicyService.GetLockoutPolicy()
        return policy.failedAttemptIntervalSec

    def set_auto_unlock_interval(self, interval=None):
        """
        Set the global lockout policy.
        :type interval: 'int'
        :param interval: Interval after which auto-unlock would happen.
        :return: None
        """
        logger.info("vim.sso.admin.lockoutPolicyService.GetLockoutPolicy")
        policy = self.content.lockoutPolicyService.GetLockoutPolicy()
        policy.autoUnlockIntervalSec = interval
        logger.info("vim.sso.admin.lockoutPolicyService.UpdateLockoutPolicy policy=%s", policy)
        self.content.lockoutPolicyService.UpdateLockoutPolicy(policy)

    def get_auto_unlock_interval(self):
        """
        Get the global lockout policy.
        :return: Value of policy.autoUnlockIntervalSec
        """
        logger.info("vim.sso.admin.lockoutPolicyService.GetLockoutPolicy")
        policy = self.content.lockoutPolicyService.GetLockoutPolicy()
        return policy.autoUnlockIntervalSec

    def enforce_minimum_number_of_special_characters(self, num=None):
        """
        Set the global password policy.
        :type num: 'int'
        :param num: Minimum number of special characters in a password.
        :return: None
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        policy.passwordFormat.minSpecialCharCount = num
        logger.info("vim.sso.admin.passwordPolicyService.UpdateLocalPasswordPolicy policy=%s", policy)
        self.content.passwordPolicyService.UpdateLocalPasswordPolicy(policy)

    def get_minimum_number_of_special_characters(self):
        """
        Get the global password policy.
        :return: Value of policy.passwordFormat.minSpecialCharCount
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        return policy.passwordFormat.minSpecialCharCount

    def enforce_min_number_of_numeric_characters(self, num=None):
        """
        Set the global password policy.
        :type num: 'int'
        :param num: Minimum number of numeric characters in a password.
        :return: None
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        policy.passwordFormat.minNumericCount = num
        logger.info("vim.sso.admin.passwordPolicyService.UpdateLocalPasswordPolicy policy=%s", policy)
        self.content.passwordPolicyService.UpdateLocalPasswordPolicy(policy)

    def get_min_number_of_numeric_characters(self):
        """
        Get the global password policy.
        :return: Value of policy.passwordFormat.minNumericCount
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        return policy.passwordFormat.minNumericCount

    def enforce_min_number_of_lower_characters(self, num=None):
        """
        Set the global password policy.
        :type num: 'int'
        :param num: Minimum number of numeric characters in a password.
        :return: None
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        policy.passwordFormat.alphabeticRestriction.minLowercaseCount = num
        logger.info("vim.sso.admin.passwordPolicyService.UpdateLocalPasswordPolicy policy=%s", policy)
        self.content.passwordPolicyService.UpdateLocalPasswordPolicy(policy)

    def get_min_number_of_lower_characters(self):
        """
        Get the global password policy.
        :return: Value of policy.passwordFormat.minNumericCount
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        return policy.passwordFormat.alphabeticRestriction.minLowercaseCount

    def enforce_min_number_of_upper_characters(self, num=None):
        """
        Set the global password policy.
        :type num: 'int'
        :param num: Minimum number of numeric characters in a password.
        :return: None
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        policy.passwordFormat.alphabeticRestriction.minUppercaseCount = num
        logger.info("vim.sso.admin.passwordPolicyService.UpdateLocalPasswordPolicy policy=%s", policy)
        self.content.passwordPolicyService.UpdateLocalPasswordPolicy(policy)

    def get_min_number_of_upper_characters(self):
        """
        Get the global password policy.
        :return: Value of policy.passwordFormat.minNumericCount
        """
        logger.info("vim.sso.admin.passwordPolicyService.GetLocalPasswordPolicy")
        policy = self.content.passwordPolicyService.GetLocalPasswordPolicy()
        return policy.passwordFormat.alphabeticRestriction.minUppercaseCount

    def get_all_domains(self):
        """
        Gets all domains from DomainManagementService.
        :return: Domains
        """
        logger.info("Retrieving SSO domains - vim.sso.admin.DomainManagementService.getDomains")
        domains = self.content.domainManagementService.GetDomains()
        return domains

    def get_system_domain(self):
        """
        Gets systemDomain name from DomainManagementService.
        :return: Domain
        """
        logger.info("Retrieving SSO system domain - vim.sso.admin.DomainManagementService.getSystemDomainName")
        system_domain = self.content.domainManagementService.GetSystemDomainName()
        return system_domain

    def find_users_in_group(self, group_id):
        """Finds users of a group using PrincipalDiscoveryService.

        :param group_id: Group principalId.
        :return: List of Users.
        """
        logger.info("vim.sso.admin.PrincipalDiscoveryService.findUsersInGroup")
        users = self.content.principalDiscoveryService.FindUsersInGroup(
            groupId=group_id, searchString="", limit=USER_QUERY_LIMIT
        )
        return users

    def find_groups_in_group(self, group_id):
        """Finds groups in a group using PrincipalDiscoveryService.

        :param group_id: Group principalId.
        :return: List of Users.
        """
        logger.info("vim.sso.admin.PrincipalDiscoveryService.FindGroupsInGroup")
        groups = self.content.principalDiscoveryService.FindGroupsInGroup(
            groupId=group_id, searchString="", limit=USER_QUERY_LIMIT
        )
        return groups
