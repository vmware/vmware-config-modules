import logging
from typing import Dict, Tuple, List, Any

import requests, json

from config_modules_vmware.framework.auth.contexts.nsxt_manager_context import NSXTManagerContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.controllers.nsxt_manager.utils import nsx_utils
from config_modules_vmware.framework.utils.comparator import Comparator


logger = LoggerAdapter(logging.getLogger(__name__))


class RolesMapping(BaseController):
    """Manage NSX vidm configuration.
    This is a controller implementation for nsxt manager.

    | Config Id - 0000
    | Config Title - NSX Manager must connect to vIDM using TLS 1.2

    """

    metadata = ControllerMetadata(
        name="secure_vidm",  # controller name
        path_in_schema="compliance_config.nsxt_manager.roles_mapping",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="Validate the role mapping in vIDM on NSX Manager.",  # controller title as defined in compliance kit.
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

    def _validate_input(self, input):

        error = None    
        key = "name"
        seen = set()
        for dictionary in input:
            if key in dictionary:
                value = dictionary[key]
                if value in seen:
                    error = f"duplicate role binding name in input: {value}"
                    return error, False
                seen.add(value)
        return error, True

    def _nsx_rest_call(self,method,url,headers=None,data=None,auth=None,verify=False,timeout=60):

        error = None
        result_body = None

        if not headers:
            headers = {}

        try:
            if method.upper() == 'GET':
                result = requests.get(url, headers=headers, auth=auth, verify=verify, timeout=timeout)
            elif method.upper() == 'PUT':
                result = requests.put(url, headers=headers, data=data, auth=auth, verify=verify, timeout=timeout)
            elif method.upper() == 'POST':
                result = requests.post(url, headers=headers, data=data, auth=auth, verify=verify, timeout=timeout)
            elif method.upper() == 'DELETE':
                result = requests.delete(url, headers=headers, data=data, auth=auth, verify=verify, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method {method}")
        
            result.raise_for_status()
            if result.content:
                result_body = result.json()

        except requests.exceptions.HTTPError as http_err:
            error = f"HTTP Error: {http_err} response: {result.text}"
        except requests.exceptions.RequestException as err:
            error = f"Other error occurred: {err}"
        except Exception as e:
            error = f"An unexpected error occurred: {e}"
        
        logger.debug(f"NSX API query response body: {result_body}")
        logger.debug(f"error: {error}")

        if error:
            raise Exception(error)
        
        return result_body

    def _get_role_bindings(self,context: NSXTManagerContext) -> dict:
        """
        Get NSX Manager role bindings.

        :return: role binding list
        :rtype: dict
        """   

        nsx_request_body = self._nsx_rest_call("GET",
            f"https://localhost/api/v1/aaa/role-bindings",
            headers=self.http_headers,
            auth=(context._username, context._password),
        )
        
        return nsx_request_body
    
    def _update_role_binding(self,context: NSXTManagerContext,role_binding_id, role_binding) -> dict:
        """
        Update a role binding.

        :return: update response
        :rtype: dict
        """

        
        payload = {}
        payload['name'] = role_binding['name']
        payload['identity_source_type'] = role_binding['source']
        if role_binding['type'] == 'GROUP':
             payload['type'] = "remote_group"
        elif binding_type == 'USER':
             binding_type = "remote_user"

        payload['roles'] = []
        for role in role_binding['roles']:
            payload['roles'].append({"role": role})

        nsx_request_body = self._nsx_rest_call("PUT",
            f"https://localhost/api/v1/aaa/role-bindings/{role_binding_id}",
            headers=self.http_headers,
            data=json.dumps(payload),
            auth=(context._username, context._password),

        )

        logger.debug(f"NSX API query response body: {nsx_request_body}")
        return nsx_request_body
    
    def _del_role_binding(self,context: NSXTManagerContext, role_binding_id) -> dict:
        """
        Delete role binding.

        :return: vidm key length
        :rtype: int
        """
    
        logger.info(f"deleting role /api/v1/aaa/role-bindings/{role_binding_id} with id {role_binding_id} ")
        nsx_request_body = self._nsx_rest_call("DELETE",
            f"https://localhost/api/v1/aaa/role-bindings/{role_binding_id}",
            headers=self.http_headers,
            auth=(context._username, context._password),
        )

        return nsx_request_body
    
    def _add_role_binding(self,context: NSXTManagerContext, role_binding) -> dict:
        """
        add role binding.

        :return: request response
        :rtype: dict
        """

        payload = {}
        payload['name'] = role_binding['name']
        payload['identity_source_type'] = role_binding['source']
        if role_binding['type'] == 'GROUP':
             payload['type'] = "remote_group"
        elif binding_type == 'USER':
             binding_type = "remote_user"

        payload['roles'] = []
        for role in role_binding['roles']:
            payload['roles'].append({"role": role})

        logger.debug(f"adding role /api/v1/aaa/role-bindings/ with payload: {payload} ")
        
        nsx_request_body = self._nsx_rest_call("POST",
            f"https://localhost/api/v1/aaa/role-bindings",
            headers=self.http_headers,
            data=json.dumps(payload),
            auth=(context._username, context._password),
        )
        return nsx_request_body
    
  
    def get(self, context: NSXTManagerContext) -> Tuple[List[Dict[str, str]], List[Any]]:
        """
        Get current role bindings.

        | Sample get output

        .. code-block:: json

            {
              "name": "group_name",
              "type": "GROUP",
              "roles": ["network_engineer"],
              "source": VIDM
            }

        :param context: NSXTManagerContext, since this controller doesn't require product specific context.
        :type context: NSXTManagerContext
        :return: Tuple of Dict containing role bindings  and a list of error messages.
        :rtype: Tuple
        """
        logger.debug("Getting vidm role bindings.")
        errors = []
        role_bindings  = None
        current_bindings = []

        try:
            role_bindings = self._get_role_bindings(context)
            logger.debug(f"role bindings: {role_bindings}")  

            #parse results
            for binding in role_bindings.get("results",[]):          
                #skip over the system owned default local users    
                if binding['_system_owned'] == True or binding['type'] == 'principal_identity' or binding['type'] == 'local_user':
                    continue

                #build dict of releveant values
                name = binding['name']                
                if 'identity_source_type' in binding:
                    source = binding['identity_source_type']
                else:
                    raise Exception(f"No identity_source_type attribute for user {name}. Cannot continue.")
                roles = []

                for role in binding['roles']:
                    roles.append(role['role'])
                binding_type = binding['type']
                if binding_type == 'remote_group':
                    binding_type = "GROUP"
                elif binding_type == 'remote_user':
                    binding_type = "USER"
                current_bindings.append({"name": name, "type": binding_type, "roles": roles, "source": source})
                                                    
        except Exception as e:
            logger.exception(f"Exception retrieving current config - {e}")
            errors.append(str(e))          
        
        return current_bindings, errors
    
    def set(self, context: NSXTManagerContext, desired_values) -> Tuple[RemediateStatus, List[str]]:
        errors =[]
        current_bindings = []
        role_binding_map = {}

        try:
            role_bindings = self._get_role_bindings(context)
            diff = []
            for binding in role_bindings.get("results",[]):
                role_binding_map[binding['name']] = binding['id']
                if binding['_system_owned'] == True or binding['type'] == 'principal_identity' or binding['type'] == 'local_user':
                    logger.info(f"skipping system owned user/group {binding['name']}")
                    continue
                name = binding['name']
                if 'identity_source_type' in binding:
                    source = binding['identity_source_type']
                else:
                    raise Exception(f"No identity_source_type attribute for user {name}. Cannot continue.")
                roles = []
                for role in binding['roles']:
                    roles.append(role['role'])
                binding_type = binding['type']

                if binding_type == 'remote_group':
                    binding_type = "GROUP"
                elif binding_type == 'remote_user':
                    binding_type = "USER"

                current_bindings.append({"name": name, "type": binding_type, "roles": roles, "source": source})


            #get lists of role bindings to add, update, or delete
            #unchanged = []    
            to_add = []
            to_update = []
            to_del = []
            
            optional_values = desired_values.get("optional",[])
            desired_values = desired_values.get("required",[])
            logging.debug(f"desired_values:  {desired_values}")

            #get role bindings that are changed or to be added
            for item1 in desired_values:                
                found_match = False
                for item2 in current_bindings:
                    if item1['name'] == item2['name']:
                        found_match = True
                        #matched name, check if attributes are same
                        if item1 == item2:
                            #matched desired value, unchanged. skip
                            break
                        else:
                            #existing role binding but one or more attributes has changed. update
                            to_update.append(item1)
                            break
                if not found_match:
                    #not found. add role binding
                    to_add.append(item1)

            #get role bindings to delete
            for item1 in current_bindings:
                #skip any current bindings that match optional
                if item1 in optional_values:
                    continue
                found_match = False
                for item2 in desired_values:
                    if item1['name'] == item2['name']:
                        found_match = True
                        break
                if not found_match:
                    to_del.append(item1)



            logging.debug(f"Role binding map:  {role_binding_map}")
            logging.debug(f"to_add: {to_add}")
            logging.debug(f"to_update: {to_update}")
            logging.debug(f"to_del: {to_del}")
            
            #Perform remediation
            for item in to_add:
                self._add_role_binding(context,item)
            for item in to_del:
                self._del_role_binding(context,role_binding_map[item['name']])
            for item in to_update:
                self._update_role_binding(context,role_binding_map[item['name']],item)
            status = RemediateStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Exception setting role mapping - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors
        


    def check_compliance(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Check compliance of current configuration against provided desired values.
        [Note: This needs to be moved as part of framework input validation once available.]

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """

        
        #check if node is leader(host VIP) in the NSX Manager cluster. If not, skip
        errors = []
        if not nsx_utils.isLeader(context):
            errors = [nsx_utils.ERROR_MSG_NOT_VIP]
            return {consts.STATUS: ComplianceStatus.SKIPPED, consts.ERRORS: errors}
        
        logger.debug("checking compliance")
        logger.info(f"desired_values: {desired_values}")
        
        #Currently we only care about required role mappings. Optional roles will be skipped for drift comparison
        #until dynamic overrides can be implemented
        optional_values = desired_values.get("optional", [])
        desired_values = desired_values.get("required")
        logger.info(f"desired_values after: {desired_values}")

        errors, isValid =  self._validate_input(desired_values)
        if not isValid:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        current_value, errors = self.get(context=context)

        #remove the optional roles from current values to skip their removal if remediation ix run.
        for role_map in current_value:
            if role_map in optional_values:
                current_value.remove(role_map)

        if errors:
            if len(errors) == 1 and errors[0] == consts.SKIPPED:
                return {consts.STATUS: ComplianceStatus.SKIPPED}
            # If errors are seen during get, return "FAILED" status with errors.
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_non_compliant_configs, desired_non_compliant_configs = Comparator.get_non_compliant_configs(
            current_value, desired_values, comparator_option=self.comparator_option, instance_key=self.instance_key
        )
        if current_non_compliant_configs or desired_non_compliant_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_non_compliant_configs,
                consts.DESIRED: desired_non_compliant_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
                          

    def remediate(self, context: NSXTManagerContext, desired_values: Any) -> Dict:
        """Remediate current vidm key length configuration drifts.

        :param context: Product context instance.
        :type context: NSXTManagerContext
        :param desired_values: Desired values for vidm key length.
        :type desired_values: Any
        :return: Dict of status and old/new values(for success) or errors (for failure).
        :rtype: dict
        """
        return super().remediate(context, desired_values)
    
      
    
