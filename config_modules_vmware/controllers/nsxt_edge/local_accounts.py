import logging
from typing import Dict, Tuple, List, Any

from config_modules_vmware.framework.auth.contexts.nsxt_edge_context import NSXTEdgeContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.nsxt import nsxt_consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils


logger = LoggerAdapter(logging.getLogger(__name__))


class LocalAccounts(BaseController):
    """Manage local user accounts with get and set methods.
    This is a common controller implementation for both nsxt manager and nsxt edge.

    | Config Id - 0000
    | Config Title - Onlyy approved local accounts should be present..

    """

    metadata = ControllerMetadata(
        name="local_accounts",  # controller name
        path_in_schema="compliance_config.nsxt_edge.local_accounts",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Only authorized local accounts must exist on each node",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[
            NSXTEdgeContext.ProductEnum.NSXT_EDGE,
        ],  # product from enum in NSXTEdgeContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["nsx_edge"],  # location where functional tests are run.
    )

    #Built-in local accounts
    
                                  
    def _get_local_nsx_accounts(self, context: NSXTEdgeContext) -> List[str]:
        """
        Get local builtin OS accounts
        :return: list of accounts
        :rtype: bool
        """

        user_list = []
        logger.info("Getting local users.")
        
        command_output = utils.run_shell_cmd("cat /etc/passwd")[0]
        for line in command_output.splitlines():
            username = line.split(':')[0]
            #filter out Ubuntu OS default accounts. Only report NSX bulitins
            if username in nsxt_consts.NSX_LOCAL_ACCOUNTS:
                user_list.append(username)
        logger.info(f"user_list: {user_list}")
        
        return user_list
        
    
    def _del_local_user_os(self, account: str) -> bool:
        """
        Delete local account
        :param account: OS account.
        :type str
        :return: True
        :rtype: bool
        """
        try:
            logger.info(f"Deleting user {account} with OS command deluser.")
            utils.run_shell_cmd(f"deluser {account}")
        except Exception as e:
            raise Exception(f"{e} output: {e.stdout}")

        return True
    
    def _del_local_user_nsxcli(self,account: str) -> bool:
        """
        Delete local account
        :param account: OS account.
        :type str
        :return: True
        :rtype: bool
        """
        try:
            logger.info(f"Deleting user {account} with NSXCLI")
            utils.run_shell_cmd(f"su -c 'del user {account}' admin", input_to_stdin="yes\n")
        except Exception as e:
            raise Exception(f"{e} output: {e.stdout}")

        return True

    def get(self, context: NSXTEdgeContext) -> Tuple[Dict, List[Any]]:
        """
        Get local NSX accounts from OS.

        | Sample get output

        .. code-block:: json

            {
              "allowed_accounts": ["root", "admin", "audit","guestuser1","guestuser2"]
            }

        :param context: NSXTEdgeContext, since this controller doesn't require product specific context.
        :type context: NSXTEdgeContext
        :return: Tuple of Dict containing local accounts and a list of error messages.
        :rtype: Tuple
        """
        logger.info("Getting local users.")
        errors = []
        try:
            local_nsx_accounts = self._get_local_nsx_accounts(context)
            logger.info(f"found local NSX accounts: {local_nsx_accounts}")
        except Exception as e:
            logger.exception(f"Exception retrieving local users - {e}")
            errors.append(str(e))
            local_nsx_accounts = []
        return {"allowed_accounts": local_nsx_accounts}, errors

    def check_compliance(self, context: NSXTEdgeContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.
        [Note: This needs to be moved as part of framework input validation once available.]

        :param context: Product context instance.
        :type context: NSXTEdgeContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """

        return super().check_compliance(context, desired_values)

    def set(self, context: NSXTEdgeContext, desired_values: Dict) -> Tuple[str, List[Any]]:
        """
        Set local account config.
        Also post set, check_compliance is run again to validate that the values are set.

        | Sample desired state for local accounts.

        .. code-block:: json

            {
              "allowed_accounts": ["root", "admin"]
            }

        :param context: Product context instance.
        :type context: NSXTEdgeContext
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

            # get list of accounts to delete
            to_del = list(set(local_nsx_accounts) - set(allowed_accounts))
            # get list of accounts to add
            to_add = list(set(allowed_accounts) - set(local_nsx_accounts))
            if len(to_add)  > 0:
                raise Exception(f"Adding local user(s) {to_add} is not supported on NSX Edge")

            #get NSX version
            product_version = nsx_utils.get_nsx_version(context)
   
            #loop through accounts to delete    
            for account in to_del: 
                if account.lower() not in nsxt_consts.NSX_LOCAL_ACCOUNTS:
                    raise Exception(f"Cannot delete non-NSX account: {account}. Only specific NSX accounts can be deleted: {nsxt_consts.NSX_DELETABLE_ACCOUNTS}")
                if account.lower() in nsxt_consts.NSX_PROTECTED_ACCOUNTS:
                    raise Exception(f"Attempt to delete {account} account.")
                
                #If NSX version is 4.x or higher use NSXCLI
                if utils.is_newer_or_same_version(product_version, "4.0.0"):    
                    self._del_local_user_nsxcli(account)             
                else:
                    self._del_local_user_os(account)
              
            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception remediating local users - {e}")
            errors.append(str(e))
            local_nsx_accounts = []
            status = RemediateStatus.FAILED

        return status, errors

    def remediate(self, context: NSXTEdgeContext, desired_values: Any) -> Dict:
        """Remediate current local account configuration drifts.

        :param context: Product context instance.
        :type context: NSXTEdgeContext
        :param desired_values: Desired values for local accounts.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        return super().remediate(context, desired_values)
