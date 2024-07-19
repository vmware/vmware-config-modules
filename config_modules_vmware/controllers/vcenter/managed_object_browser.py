# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import xml.etree.ElementTree as ETree  # nosec
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from xml.dom import minidom  # nosec

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils

logger = LoggerAdapter(logging.getLogger(__name__))

MOB_KEY = "enableDebugBrowse"
SERVICE_ELEMENT = "vpxd"
SERVICE_NAME = "vmware-vpxd"
SERVICE_RESTART_COMMAND = f"service-control --restart {SERVICE_NAME}"
SERVICE_STATUS_COMMAND = f"service-control --status {SERVICE_NAME}"
VPXD_CFG_FILE_PATH = "/etc/vmware-vpx/vpxd.cfg"


class ManagedObjectBrowser(BaseController):
    """Manage vCenter managed object browser config with get and set methods.
    [Risk] Set/remediate method also restarts 'vpxd' service post settings change to reflect the changes.

    | Config Id - 0000
    | Config Title - The vCenter Server must disable the managed object browser (MOB) at all times when not required for troubleshooting or maintenance of managed objects.
    """

    metadata = ControllerMetadata(
        name="managed_object_browser",  # controller name
        path_in_schema="compliance_config.vcenter.managed_object_browser",  # path in the schema to this controller's definition.
        configuration_id="0000",  # configuration id as defined in compliance kit.
        title="The vCenter Server must disable the managed object browser (MOB) at all times when not required for troubleshooting or maintenance of managed objects",
        # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=None,  # from enum in ControllerMetadata.RemediationImpact.
        scope="",  # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
        functional_test_targets=["vcenter"],  # location where functional tests are run.
    )

    def _get_environment_variables(self) -> Dict[str, str]:
        """Helper method to return all environment variables needed."""
        environment = {
            "VMWARE_LOG_DIR": "/var/log",
            "VMWARE_PYTHON_PATH": "/usr/lib/vmware/site-packages",
            "VMWARE_DATA_DIR": "/storage",
            "VMWARE_CFG_DIR": "/etc/vmware",
            "VMWARE_RUNTIME_DATA_DIR": "/var",
            "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/vmware/bin:/opt/vmware/bin",
        }
        return environment

    @staticmethod
    def _get_managed_object_browser_config() -> bool:
        """Get managed object browser config.

        :return: Managed object Browser config (True or False)
        :rtype: bool
        """
        # Set default value as true. If the mob_element is not present in the cfg file, set it to true.
        mob_enabled_value = "true"

        tree = ETree.parse(VPXD_CFG_FILE_PATH)  # nosec
        root = tree.getroot()

        vpxd_element = root.find(SERVICE_ELEMENT)
        if vpxd_element is not None:
            mob_element = vpxd_element.find(MOB_KEY)
            if mob_element is not None:
                mob_enabled_value = mob_element.text

        if mob_enabled_value == "true":
            result = True
        elif mob_enabled_value == "false":
            result = False
        else:
            error_msg = f"Unexpected value {mob_enabled_value} for property {MOB_KEY}"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.debug(f"element is {mob_enabled_value}")
        return result

    @staticmethod
    def _apply_managed_object_browser_config(desired_values: bool) -> None:
        """Set managed object browser config.

        :param desired_values: Desired state for managed object browser config.
        :type desired_values: bool
        """
        is_mob_enabled = desired_values

        tree = ETree.parse(VPXD_CFG_FILE_PATH)  # nosec
        root = tree.getroot()

        vpxd_element = root.find(SERVICE_ELEMENT)
        if vpxd_element is None:
            vpxd_element = ETree.SubElement(root, SERVICE_ELEMENT)

        mob_element = vpxd_element.find(MOB_KEY)
        if mob_element is None:
            mob_element = ETree.SubElement(vpxd_element, MOB_KEY)

        # Set the mob element value.
        mob_element.text = "true" if is_mob_enabled else "false"

        xml_str = ETree.tostring(root, encoding="utf-8")
        parsed_xml = minidom.parseString(xml_str)  # nosec
        pretty_xml_as_string = parsed_xml.toprettyxml(indent="  ")

        lines = pretty_xml_as_string.split("\n")
        non_empty_lines = [line for line in lines if line.strip() != ""]
        pretty_xml_without_declaration = "\n".join(non_empty_lines[1:])
        logger.debug(f"{pretty_xml_without_declaration}")

        with open(VPXD_CFG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(pretty_xml_without_declaration + "\n")

    def get(self, context: VcenterContext) -> Tuple[bool, List[Any]]:
        """Get managed object browser config on vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: Tuple of bool and a list of error messages if any.
        :rtype: tuple
        """
        logger.info("Getting managed object browser config from vCenter")
        result = None
        errors = []
        try:
            result = self._get_managed_object_browser_config()
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
        return result, errors

    def set(self, context: VcenterContext, desired_values: bool) -> Tuple[str, List[Any]]:
        """Set managed object browser config on vCenter.
        Restart 'vpxd' service post changing the MOB settings to reflect the changes.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the managed object browser config.
        :type desired_values: bool
        :return: Tuple of "status" and list of error messages.
        :rtype: Tuple
        """
        logger.info("Setting managed object browser config")
        errors = []
        status = RemediateStatus.SUCCESS

        try:
            self._apply_managed_object_browser_config(desired_values)
            service_start_output, _, _ = utils.run_shell_cmd(
                command=SERVICE_RESTART_COMMAND, env=self._get_environment_variables()
            )
            logger.debug(f"Restart service output: {service_start_output}")
            service_status_output, _, _ = utils.run_shell_cmd(
                command=SERVICE_STATUS_COMMAND, env=self._get_environment_variables()
            )
            logger.debug(f"Service status command output: {service_status_output}")
            if "Running" not in service_status_output or SERVICE_NAME not in service_status_output:
                err_msg = f"Service {SERVICE_NAME} is not running post restart. Please resolve this issue."
                raise Exception(err_msg)

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            errors.append(str(e))
            status = RemediateStatus.FAILED

        return status, errors
