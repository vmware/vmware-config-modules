# Copyright 2023 VMware, Inc.  All rights reserved. -- VMware Confidential
import json
import logging

import requests

from config_modules_vmware.framework.auth.contexts.vidm_context import VidmContext
from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.clients.aria_suite import vidm_consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.clients.common import consts
from typing import Dict, Tuple, List, Any
from config_modules_vmware.framework.clients.common.consts import STATUS
from config_modules_vmware.framework.clients.aria_suite import aria_auth
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))
ID = "id"
NAME = "name"
ELEMENTS = "elements"
TYPE = "type"
ROLE = "role"
USERS_GROUPS_ROLES_INFO = "users_groups_roles_info"


class UsersGroupsRolesConfig(BaseController):
    """Class for UsersGroupsRolesSettings config with get and set methods.
    | ConfigId - 1605
    | ConfigTitle - Assign least privileges to users and service accounts in VIDM.
    """

    metadata = ControllerMetadata(
        name="users_groups_roles",  # controller name
        path_in_schema="compliance_config.vidm.users_groups_roles",  # path in the schema to this controller's definition.
        configuration_id="1605",  # configuration id as defined in compliance kit.
        title="Assign least privileges to users and service accounts in SDDC Manager.",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[VidmContext.ProductEnum.VIDM],  # product from enum in VidmContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
    )

    @staticmethod
    def _get_vidm_token(self, url, username, password, client_id, client_secret):
        """
        Make REST call to get Log Insight token
        :param url: url
        :type url: 'str'
        :param username: Username
        :type username: 'str'
        :param password: Password
        :type password: 'str'
        :param client_id:  client id to use for auth
        :type client_id: 'str'
        :param client_secret: client secret to use for auth
        :type client_secret: 'str'
        :raise :class:`urllib3.exceptions.HTTPError`
            If REST call response has a non HTTPStatus.OK status code.
        """
        logger.info("Creating vmware api session")

        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}

        if "@" in username:
            domain = username.split("@")[1]
            username = username.split("@")[0]
        else: 
            domain = ""

        payload = f"&grant_type=password&client_id={client_id}&client_secret={client_secret}&username={username}&password={password}&scope=admin{domain}"

        logger.info(f"url: '{url}'")

        get_token_response = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload,
            verify=False,
            timeout=60,
        )

        get_token_response.raise_for_status()
        get_token_response_body = get_token_response.json()

        # Parse response for vmware api session id.
        vidm_access_token = get_token_response_body["access_token"]
        return vidm_access_token

    def _call_vidm_api(self, headers: dict, url: str, http_method: str, request_body: str = "") -> dict:
        """
        Call DNS API.

        :param headers: headers to be used in REST call
        :type headers: dictionary
        :param url: URL to be used for REST call
        :type url: str
        :param http_method: the http operation (GET/POST/DELETE).
        :type http_method: str
        :param request_body: request body if applicable
        :type request_body: str
        :return: response body
        :rtype: dict
        """

        logger.info(f"_call_vidm_api: begin...")

        if (http_method == "GET"):
            request_body = ""

        vidm_query_response = requests.request(
            method=http_method,
            url=url,
            headers=headers,
            data=json.dumps(request_body),
            verify=False,
            timeout=60,
        )

        logger.info(f"Successfully called: {url}")
        logger.info(f"vidm_query_response query response body: {vidm_query_response}")
        vidm_query_response.raise_for_status()
        try:
            vidm_query_response_json = vidm_query_response.json()
        except Exception as e: 
            logger.info(f'vidm_query_response.status: {vidm_query_response.status_code}')
            vidm_query_response_json = {}

        logger.info(f"vidm_query_response_json query response body: {vidm_query_response_json}")

        return vidm_query_response_json

    def _get_ruleset_association_href(self, ruleset_response: dict, name: str) -> str:
        """get ruleset association href.

        :param ruleset_response: ruleset response
        :type ruleset_response: dict
        :param name: name
        :type name: str
        :return: ruleset association href
        :rtype: str
        """

        guid_href = ""
        for ruleset in ruleset_response['items']:
            if ruleset["name"] == name:
                guid_href = ruleset['_links']['associations']['href']
                break

        return guid_href

    def _get_entity_id(self, context: VidmContext, entity_type: str, group_name: str, headers: dict) -> str:
        """get entity id

        :param context: VIDM product context instance.
        :type context: VidmContext
        :param entity_type: the entity type to perform the get action for
        :type entity_type: str
        :param group_name: entity name
        :type group_name: str
        :param headers: headers required to make the api call
        :type headers: dict
        :return: string value of entity id
        :rtype: str
        """

        if entity_type == "GROUP":
            pre_url = vidm_consts.SCIM_GROUPS_URL.format(context.hostname) 
            entity_url = pre_url + "?filter=displayName%20eq%20%22" + group_name + "%22"
        elif entity_type == "USER":
            pre_url = vidm_consts.SCIM_USERS_URL.format(context.hostname) 
            entity_url = pre_url + "?filter=userPrincipalName%20eq%20%22" + group_name + "%22"

        entity_response = self._call_vidm_api(headers, entity_url, "GET") 
        entity_id = entity_response["Resources"][0]["id"]

        return entity_id

    def _get_admin_role_id(self, context: VidmContext, headers: dict) -> str:
        """get entity id

        :param context: VIDM product context instance.
        :type context: VidmContext
        :param entity_type: the entity type to perform the get action for
        :type entity_type: str
        :param group_name: entity name
        :type group_name: str
        :param headers: headers required to make the api call
        :type headers: dict
        :return: string value of entity id
        :rtype: str
        """

        url = vidm_consts.ROLE_URL.format(context.hostname)

        entity_response = self._call_vidm_api(headers, url, "GET") 
        resources = entity_response["Resources"]
        for resource in resources:
            if resource['displayName'] == 'Administrator':
                logger.info(f"Administrator role found with id: {resource['id']}")
                id = resource['id']
                break

        return id

    def _update_admin_role_with_group(self, context: VidmContext, headers: dict, admin_role_id: str, group_id: str) -> str:
        """get entity id

        :param context: VIDM product context instance.
        :type context: VidmContext
        :param entity_type: the entity type to perform the get action for
        :type entity_type: str
        :param group_name: entity name
        :type group_name: str
        :param headers: headers required to make the api call
        :type headers: dict
        :return: string value of entity id
        :rtype: str
        """

        pre_url = vidm_consts.ROLE_URL.format(context.hostname)
        url = pre_url + admin_role_id

        request_body = {"schemas": ["urn:scim:schemas:core:1.0"],"members": [{"value": group_id, "type": "Group"}]}
        logger.info (f"_update_admin_role_with_group: url: {url}")
        logger.info (f"_update_admin_role_with_group: request_body: {request_body}")
        headers["Content-Type"] = "application/json"
        entity_response = self._call_vidm_api(headers, url, "PATCH", request_body) 
        logger.info(f"_update_admin_role_with_group: entity_response: {entity_response}")
        
        return entity_response

    def _add_group_role_mapping(self, context: VidmContext, desired_value: dict, headers: dict, ruleset_response: dict):
        """add group role mapping.

        :param context: VIDM product context instance.
        :type context: VidmContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: dict
        :param headers: headers required to make the api call.
        :type headers: dict
        :param ruleset_response: ruleset_response
        :type ruleset_response: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """

        role_name = desired_value["role"]
        group_name = desired_value["name"]
        entity_type = desired_value["type"]

        #get role href
        ruleset_association_href = vidm_consts.VIDM_API_BASE.format(context.hostname) + self._get_ruleset_association_href(ruleset_response, role_name)

        #get group id
        #get entity id

        entity_id = self._get_entity_id(context, entity_type, group_name, headers)

        request_body = {
            "operations": [
                {
                    "users": [],
                    "groups": [
                    ],
                    "associationMethodTO": "POST"
                },
                {
                    "users": [],
                    "groups": [],
                    "associationMethodTO": "DELETE"
                }
            ]
        }

        if entity_type == "GROUP":
            request_body["operations"][0]["groups"].append(entity_id)
            group_id = entity_id
        elif entity_type == "USER":
            request_body["operations"][0]["users"].append(entity_id)

        logger.info(f"adding configuration based on url: {ruleset_association_href}")
        logger.info(f"adding configuration based on body: {request_body}")
        headers["Content-Type"] = "application/vnd.vmware.vidm.accesscontrol.ruleset.associations.bulk.request+json"

        post_response = self._call_vidm_api(headers, ruleset_association_href, "POST", request_body) 

        #get admin role
        admin_role_id = self._get_admin_role_id(context, headers)
        post_response = self._update_admin_role_with_group(context, headers, admin_role_id, entity_id)

        return True

    def _remove_group_role_mapping(self, context: VidmContext, desired_value: dict, headers: dict, ruleset_response: dict):
        """remove group role mapping.

        :param context: VIDM product context instance.
        :type context: VidmContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: dict
        :param headers: headers required to make the api call.
        :type headers: dict
        :param ruleset_response: ruleset_response
        :type ruleset_response: dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        role_name = desired_value["role"]
        group_name = desired_value["name"]
        entity_type = desired_value["type"]

        #get role href
        ruleset_association_href = vidm_consts.VIDM_API_BASE.format(context.hostname) + self._get_ruleset_association_href(ruleset_response, role_name)

        #get entity id

        entity_id = self._get_entity_id(context, entity_type, group_name, headers)

        request_body = {
            "operations": [
                {
                    "users": [],
                    "groups": [
                    ],
                    "associationMethodTO": "POST"
                },
                {
                    "users": [],
                    "groups": [
                    ],
                    "associationMethodTO": "DELETE"
                }
            ]
        }

        if entity_type == "GROUP":
            request_body["operations"][1]["groups"].append(entity_id)
            group_id = entity_id
        elif entity_type == "USER":
            request_body["operations"][1]["users"].append(entity_id)
        
        logger.info(f"removing configuration based on url: {ruleset_association_href}")
        logger.info(f"removing configuration based on body: {request_body}")
        headers["Content-Type"] = "application/vnd.vmware.vidm.accesscontrol.ruleset.associations.bulk.request+json"

        post_response = self._call_vidm_api(headers, ruleset_association_href, "POST", request_body) 

        return True
        


    def get(self, context: VidmContext) -> Tuple[Dict, List[Any]]:
        """
        Get UsersGroupsRolesSettings config for audit control.

        :param context: VidmContext.
        :type context: VidmContext
        :return: Tuple of dict with key "users_groups_roles_info" and list of error messages.
        :rtype: tuple
        """
        logger.debug("Getting UsersGroupsRolesSettings control config for audit.")
        

        errors = []
        users_groups_roles = {}
        try:
            logger.info(f"get function...")

            hostname = context._hostname
            username = context._username
            password = context._password
            client_id = context._client_id
            client_secret = context._client_secret

            get_token_url = vidm_consts.VIDM_TOKEN_URL.format(hostname)
            vidm_access_token = self._get_vidm_token(self, get_token_url, username, password, client_id, client_secret)

            headers = {"Content-Type": "application/json"}
            headers["Authorization"] = "Bearer " + vidm_access_token
            logger.info("Successfully created VIDM API headers")      
                 
            ruleset_url = vidm_consts.RULESETS_URL.format(hostname)     
            ruleset_response = self._call_vidm_api(headers, ruleset_url, "GET") 
            logger.info("Successfully retrieved rulesets") 

            users_groups_roles = {
                "users_groups_roles_info": [
                ]
            }

            for ruleset in ruleset_response['items']:
                role_name = ruleset["name"]
                guid_href = ruleset['_links']['associations']['href']
                guid_url = vidm_consts.VIDM_API_BASE.format(hostname) + guid_href
                guid_response = self._call_vidm_api(headers, guid_url, "GET") 

                #GROUPS
                logger.info(f"getting mapped groups for: {role_name}")
                for group in guid_response.get("groups"):
                    group_url = vidm_consts.SCIM_GROUPS_URL.format(hostname) + group
                    try:
                        group_response = self._call_vidm_api(headers, group_url, "GET") 
                        display_name = group_response["displayName"]

                        role_group_mapping = {
                                NAME: display_name,
                                ROLE: role_name,
                                TYPE: "GROUP"
                                
                            }

                        logger.info(f"role_group_mapping: {role_group_mapping}")
                        users_groups_roles["users_groups_roles_info"].append(role_group_mapping)
                        logger.info(f"users_groups_roles: {users_groups_roles}")
                    except Exception as e:
                        logger.info(f"group not found: {group}")

                #USERS
                logger.info(f"getting mapped users for: {role_name}")
                for user in guid_response.get("users"):
                    user_url = vidm_consts.SCIM_USERS_URL.format(hostname) + user
                    try:
                        user_response = self._call_vidm_api(headers, user_url, "GET") 

                        user_name = user_response["userName"]
                        logger.info(f"username: {user_name}")

                        if user_name not in ["admin", "configuser", "sshuser"]:
                            display_name = user_response["urn:scim:schemas:extension:workspace:1.0"]["userPrincipalName"]

                            role_group_mapping = {
                                    NAME: display_name,
                                    ROLE: role_name,
                                    TYPE: "USER"
                                }

                            logger.info(f"role_group_mapping: {role_group_mapping}")
                            users_groups_roles["users_groups_roles_info"].append(role_group_mapping)
                            logger.info(f"users_groups_roles: {users_groups_roles}")
                    except Exception as e:
                        logger.info(f"user not found: {user}")

        except Exception as e:
            errors.append(e)
            users_groups_roles = {}

        return users_groups_roles, errors

 

    def set(self, context: VidmContext, desired_values: Dict) -> Tuple:
        """set the configuration based on the desired values .

        :param context: VIDM product context instance.
        :type context: VidmContext
        :param desired_values: Desired values for the specified configuration.
        :type desired_values: Any
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: dict
        """
        try:

            hostname = context._hostname
            username = context._username
            password = context._password
            client_id = context._client_id
            client_secret = context._client_secret

            get_token_url = vidm_consts.VIDM_TOKEN_URL.format(hostname)
            vidm_access_token = self._get_vidm_token(self, get_token_url, username, password, client_id, client_secret)

            headers = {"Content-Type": "application/json"}
            headers["Authorization"] = "Bearer " + vidm_access_token
            logger.info("Successfully created VIDM API headers")    

            #get current values:
            current_values, errors = self.get(context=context)
            logger.info(f"current_values in set function: {current_values}")
            current_mappings = current_values["users_groups_roles_info"]
            role_info_desired_values = desired_values["users_groups_roles_info"]
            logger.info(f"role_info_desired_values in set function: {role_info_desired_values}")

            ruleset_url = vidm_consts.RULESETS_URL.format(hostname)     
            ruleset_response = self._call_vidm_api(headers, ruleset_url, "GET") 
            logger.info("Successfully retrieved rulesets") 


            #add ones that do not exist.
                #for each desired value
                #if desired value not in actual values, add
            for desired_value in role_info_desired_values:
                if desired_value not in current_mappings:
                    #add mappings
                    logger.info(f"adding desired_value: {desired_value}")
                    self._add_group_role_mapping(context, desired_value, headers, ruleset_response)


            #remove ones that should not be there.
                #for each actual value
                #if actual value not in desired values, delete
            for current_mapping in current_mappings:
                if current_mapping not in role_info_desired_values:
                    logger.info(f"removing current_mapping: {current_mapping}")
                    self._remove_group_role_mapping(context, current_mapping, headers, ruleset_response)

        #check_compliance again
            if self.check_compliance(context, desired_values).get(STATUS) != ComplianceStatus.COMPLIANT:
                raise Exception("Post Remediation check - Failed to update ROLE Mapping.")

            status = RemediateStatus.SUCCESS

        except Exception as e:
            logger.exception(f"Exception setting syslog value - {e}")
            status = RemediateStatus.FAILED
            errors.append(str(e))
        return status, errors


