import logging
from typing import Dict, Tuple, List, Any
import requests
import json

from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.nsxt import nsxt_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class LocalAccounts(BaseController):
    """Manage local user accounts with get and set methods.
    This is a  controller implementation for both nsxt manager

    | Config Id - 0000
    | Config Title - Only approved local accounts should be present..

    """

    metadata = ControllerMetadata(
        name="local_accounts",  # controller name
        path_in_schema="compliance_config.nsxt_manager.local_accounts",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Only authorized local accounts must exist on each node",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[
            NSXTManagerContext.ProductEnum.NSXT_MANAGER
        ],  # product from enum in NSXTManagerContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsx_manager"],  # location where functional tests are run.
    )
    
    http_headers = {'Content-Type': 'application/json'}
    
    def _get_local_users_api(self, context: NSXTManagerContext) -> List[str]:
        """
        Get local users from NSX-T API.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :return: list of dicts containing each username and userid
        :rtype: list of dicts
        """
        local_accounts = []
        nsx_request = requests.get(
            f"https://localhost/api/v1/node/users",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")

        for user in nsx_request_body["results"]:
           local_accounts.append({"name": user["username"], "uid": user["userid"]})
        return local_accounts

    def _get_local_users_cli(self, context: NSXTManagerContext) -> List[str]:
        """
        Get local users from OS /etc/passwd file.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :return: list of dicts containing each username and userid
        :rtype: list of dicts
        """
        local_accounts = []
        command_output = utils.run_shell_cmd("cat /etc/passwd")[0]
        for line in command_output.splitlines():
            fields = line.split(':')
            username = fields[0]
            uid = fields[2]
            #filter out Ubuntu OS default accounts. Only report NSX bulitins
            if username in nsxt_consts.NSX_LOCAL_ACCOUNTS:
                local_accounts.append({"name": username, "uid": uid})
        return local_accounts

    def _get_local_nsx_accounts(self, context: NSXTManagerContext) -> List[str]:
        """
        Get local builtin OS accounts using API or OS commands depending on NSX verison
        :return: list of accounts
        :rtype: dict
        """

        user_list = []
        logger.info("Getting local users.")
        
        product_version = nsx_utils.get_nsx_version(context)
        #If NSX version is 4.x or higher use API
        if utils.is_newer_or_same_version(product_version, "4.0.0"):
            user_list = self._get_local_users_api(context)
        else:
            user_list = self._get_local_users_cli(context)

        logger.error(f"user_list: {user_list}")
        return user_list
    
    
    def _del_local_account(self, context, account: str, uid: int) -> bool:
        """
        Delete local account on NSX
        :return: list of accounts
        :rtype: dict
        """

        if account.lower() not in nsxt_consts.NSX_LOCAL_ACCOUNTS:
            raise Exception(f"Cannot delete non-NSX account: {account}. Only specific NSX accounts can be deleted: {nsxt_consts.NSX_DELETABLE_ACCOUNTS}")
        if account.lower() in nsxt_consts.NSX_PROTECTED_ACCOUNTS:
            raise Exception(f"Attempt to delete protected account {account} account.")
    
        product_version = nsx_utils.get_nsx_version(context)
        #If NSX version is 4.x or higher use API
        if utils.is_newer_or_same_version(product_version, "4.0.0"):
            self._del_local_user_api(context, account, uid)
        else:
            self._del_local_user_cli(account)
        
        
    
    def _del_local_user_api(self,  context: NSXTManagerContext, account: str, uid: int) -> bool:
        """
        Delete local account using NSX API.

        :return: response body
        :rtype: dict
        """         

        logger.info(f"deleting user {account} with userid {uid} via API ")

        #get user by uid
        nsx_request = requests.get(
            f"https://localhost/api/v1/node/users/{uid}",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")

        #Check username vs uid from API
        username_from_api = nsx_request_body["username"]
        if username_from_api != account:
            raise Exception(f"ERROR: Requested deleteion of user {account} and uid {uid} but provided uid[{uid}] matches username {username_from_api}. Cannot proceeed with deletion ")

        logger.info(f"Deleting user {account}")
    
        #del user by uid
        logging.info(f"Calling DELTE on user {account} with uid {uid}")
        nsx_request = requests.delete(
            f"https://localhost/api/v1/node/users/{uid}",
            headers=self.http_headers,
            auth=(context._username, context._password),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        logger.debug(f"NSX API reposne: {nsx_request.status_code}")

        return True

    def _del_local_user_cli(self, account: str) -> bool:
        """
        Delete local account using OS deluser command
        :param account: OS account.
        :type str
        :return: True
        :rtype: bool
        """

        logger.info("deleting user {account} via NSX CLI ")
        utils.run_shell_cmd(f"deluser {account}")
        return True
    
    def _add_local_user_api(self,  context: NSXTManagerContext, account: str) -> bool:
        """
        Call NSX-T Manager API to get current config.

        :return: response body
        :rtype: dict
        """         

        logger.info(f"adding user {account} with userid via API ")

        base_user_create_url = "https://localhost/api/v1/node/users"

        if(account == "audit"):
            action = "?action=create_audit_user"
        else:
            action = "?action=create_user"
        
        url = base_user_create_url + action

        payload = {"full_name": account, 
                   "username": account
                }
        
        #add user
        nsx_request = requests.post(
            url,
            headers=self.http_headers,
            auth=(context._username, context._password),
            data=json.dumps(payload),
            verify=False,
            timeout=60,
        )
        nsx_request.raise_for_status()
        nsx_request_body = nsx_request.json()
        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return True

    def get(self, context: NSXTManagerContext) -> Tuple[Dict, List[Any]]:
        """
        Get local NSX accounts

        | Sample get output

        .. code-block:: json

            {
              "allowed_accounts": ["root", "admin", "audit","guestuser1","guestuser2"]
            }

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing local accounts and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting local users.")
        errors = []
        try:
            local_nsx_accounts = self._get_local_nsx_accounts(context)
            
            #get just usernames form list of [username, uids]
            local_usernames = []
            for user_data in local_nsx_accounts:
                logger.error(f"user_data: {user_data}")
                local_usernames.append(user_data["name"])
            logger.error(f"found local NSX accounts: {local_usernames}")
        except Exception as e:
            logger.exception(f"Exception retrieving local users - {e}")
            errors.append(str(e))
            local_usernames = []
        return {"allowed_accounts": local_usernames}, errors

    def check_compliance(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.
    
        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """

        #if NSX version >= 4.x check if node is cluster leader. 
        #API only needs to be called on leader. Changes will be synced to the other two nodes
        product_version = nsx_utils.get_nsx_version(context)
        if utils.is_newer_or_same_version(product_version, "4.0.0"):         
            #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
            errors = []
            if not nsx_utils.isLeader(context):
                errors = [nsx_utils.ERROR_MSG_NOT_VIP]
                return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
        
        return super().check_compliance(context, desired_values)

    def set(self, context: NSXTManagerContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set local account config.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for local accounts.

        .. code-block:: json

            {
              "allowed_accounts": ["root", "admin"]
            }

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired value for the local accounts.
        :type desired_values: dict
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        errors = []
        try:
            allowed_accounts = desired_values.get("allowed_accounts", [])
            
            #allowed accounts cannot be empty
            if not allowed_accounts:
                raise Exception("ERROR: Allowed accounts is empty!")
            
            local_nsx_accounts = self._get_local_nsx_accounts(context)
            
            #create map of username to uid
            uid_map = {}
            for user_data in local_nsx_accounts:
                uid_map[user_data["name"]] = user_data["uid"]
            
            #get list of just usernames
            local_usernames = []
            for user_data in local_nsx_accounts:
                 local_usernames.append(user_data["name"])
           
            # get list of accounts to delete
            to_del = list(set(local_usernames) - set(allowed_accounts))
            # get list of accounts to add
            to_add = list(set(allowed_accounts) - set(local_usernames))
            logger.info(f"to_del: {to_del}")
            logger.info(f"to_add: {to_add}")

            product_version = nsx_utils.get_nsx_version(context)
            if not utils.is_newer_or_same_version(product_version, "4.0.0") and len(to_add)  > 0:
                raise Exception(f"Adding local user(s) {to_add} is not supported in NSX {product_version}")
            
            for account in to_del: 
                #If NSX version is 4.x or higher use API
                if utils.is_newer_or_same_version(product_version, "4.0.0"):                   
                    self._del_local_user_api(context,account, uid_map[account])
                else:
                    self._del_local_user_cli(account)

            for account in to_add: 
                #If NSX version is 4.x or higher use API
                if utils.is_newer_or_same_version(product_version, "4.0.0"):                   
                    self._add_local_user_api(context,account)
                else:
                    raise Exception(f"Adding local user(s) {to_add} is not supported in NSX {product_version}")

            status = RemediateStatus.SUCCESS

        except Exception as e:
            logger.exception(f"Exception remediating local users - {e}")
            errors.append(str(e))
            local_nsx_accounts = []
            status = RemediateStatus.FAILED

        return status, errors

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current local account configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for local accounts.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        return super().remediate(context, desired_values)
