# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from config_modules_vmware.controllers.base_controller import BaseController
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.framework.utils.comparator import Comparator
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList

logger = LoggerAdapter(logging.getLogger(__name__))

RECONFIGURE_VC_TLS_SCRIPT_PATH = "/usr/lib/vmware-TlsReconfigurator/VcTlsReconfigurator/reconfigureVc"
SCAN_COMMAND = "scan"
UPDATE_COMMAND = "update"
REGEX_PATTERN = r"\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
NOT_RUNNING = "NOT RUNNING"
SERVICES_TO_BE_IGNORED = ["VC Storage Clients"]


class TlsVersion(BaseController):
    """Class to implement get and set methods for configuring and enabling specified TLS versions.
    For vcenter versions 8.0.2 and above, control is not applicable.

    | Config Id - 1204
    | Config Title - The vCenter Server must enable TLS 1.2 exclusively.

    """

    metadata = ControllerMetadata(
        name="tls_version",  # controller name
        path_in_schema="compliance_config.vcenter.tls_version",
        # path in the schema to this controller's definition.
        configuration_id="1204",  # configuration id as defined in compliance kit.
        title="The vCenter Server must enable TLS 1.2 exclusively.",  # controller title as defined in compliance kit.
        tags=[],  # controller tags for future querying and filtering
        version="1.0.0",  # version of the controller implementation.
        since="",  # version when the controller was first introduced in the compliance kit.
        products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
        components=[],  # subcomponent within the product if applicable.
        status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
        impact=ControllerMetadata.RemediationImpact.RESTART_REQUIRED,  # from enum in ControllerMetadata.RemediationImpact.
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
            "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/vmware/bin",
        }
        return environment

    def get(self, context: VcenterContext) -> Tuple[Dict[str, List[str]], List[str]]:
        """Get TLS versions for the services on vCenter.

        :param context: Product context instance.
        :type context: VcenterContext
        :return: A tuple containing a dictionary where keys are service names and values are list of TLS versions and
            a list of error messages if any.
        :rtype: Tuple
        """
        logger.info("Getting TLS versions for all the services.")

        errors = []
        tls_versions = {}

        # Check product version, if product version is >= 8.0.2.x, this control is not applicable.
        if utils.is_newer_or_same_version(context.product_version, "8.0.2"):
            errors.append(consts.SKIPPED)
            return tls_versions, errors

        try:
            command = "{} {}".format(RECONFIGURE_VC_TLS_SCRIPT_PATH, SCAN_COMMAND)
            _, tls_output_data, _ = utils.run_shell_cmd(command=f"{command}", env=self._get_environment_variables())
            # Currently,the required data is captured in std.error.
            matches = re.findall(REGEX_PATTERN, tls_output_data)
            matches = matches[1:]
            for match in matches:
                service_name = match[0].strip()
                tls_version = match[2].strip()
                if tls_version and tls_version != NOT_RUNNING:
                    tls_versions[service_name] = [v.strip() for v in tls_version.split()]
                else:
                    tls_versions[service_name] = [tls_version]
        except Exception as e:
            errors.append(str(e))
        return tls_versions, errors

    def set(self, context: VcenterContext, desired_values) -> Tuple[str, List[Any]]:
        """
        It is a high-risk remediation as it requires restart of services/vCenter.
        Post updating the TLS versions, services are restarted as part of the implementation.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values with keys as services and values as TLS versions.
        :type desired_values: Dict
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        :rtype: Tuple
        """
        logger.info("Setting TLS versions for all the services.")
        errors = []

        # Check product version, if product version is >= 8.0.2.x, this control is not applicable.
        if utils.is_newer_or_same_version(context.product_version, "8.0.2"):
            errors.append(consts.SKIPPED)
            return RemediateStatus.SKIPPED, errors

        try:
            remediation_commands = []
            if consts.GLOBAL in desired_values:
                command = "{} {} -p {} --quiet".format(
                    RECONFIGURE_VC_TLS_SCRIPT_PATH, UPDATE_COMMAND, " ".join(desired_values[consts.GLOBAL])
                )
                remediation_commands.append(command)
            for service_key, tls_versions in desired_values.items():
                if service_key == consts.GLOBAL:
                    continue
                command = "{} {} -s {} -p {} --quiet".format(
                    RECONFIGURE_VC_TLS_SCRIPT_PATH,
                    UPDATE_COMMAND,
                    service_key,
                    " ".join(tls_versions),
                )
                remediation_commands.append(command)

            total_commands = len(remediation_commands)
            for idx in range(total_commands - 1):
                remediation_commands[idx] = remediation_commands[idx] + " --no-restart"

            logger.debug(f"remediation commands {remediation_commands}")
            for command in remediation_commands:
                _, tls_output_data, _ = utils.run_shell_cmd(command=f"{command}", env=self._get_environment_variables())
                logger.debug(f"Captured output post update: {tls_output_data}")
            status = RemediateStatus.SUCCESS
        except Exception as e:
            errors.append(str(e))
            status = RemediateStatus.FAILED
        return status, errors

    def check_compliance(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """Check compliance of current configuration against provided desired values.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values for the TLS versions on vCenter(and services).
        :type desired_values: Dict
        :return: Dict of status and current/desired value(for non_compliant) or errors (for failure).
        :rtype: Dict
        """
        logger.info("Running check compliance for vCenter TLS control")

        current, errors = self.get(context=context)
        if errors:
            if len(errors) == 1 and errors[0] == consts.SKIPPED:
                return {
                    consts.STATUS: ComplianceStatus.SKIPPED,
                    consts.ERRORS: [consts.CONTROL_NOT_APPLICABLE],
                }
            # If errors are seen during get, return "FAILED" status with errors.
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # If services from ignore_service_list are present in desired spec, fail the operation and report back.
        not_supported_keys = [key for key in desired_values.keys() if key in SERVICES_TO_BE_IGNORED]
        if not_supported_keys:
            errors = []
            for key in not_supported_keys:
                errors.append(f"Can not override service '{key}' in desired spec. Desired spec needs to be fixed.")
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # If unknown services are present in desired spec, fail the operation and report back.
        missing_keys = [key for key in desired_values.keys() if key != consts.GLOBAL and key not in current]
        if missing_keys:
            errors = []
            for missing_key in missing_keys:
                errors.append(f"Service not found. Failed to get the TLS version for service '{missing_key}'.")
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

        # Recreate desired values by expanding global, overrides for all the services present in current.
        desired = {}
        global_versions = desired_values.get(consts.GLOBAL, [])
        for service, versions in current.items():
            if versions == [NOT_RUNNING]:
                desired[service] = desired_values[service] if service in desired_values else versions
            elif service in desired_values:
                desired[service] = desired_values[service]
            else:
                desired[service] = global_versions if consts.GLOBAL in desired_values else versions

        # If no errors seen, compare the current and desired value. If not same, return "NON_COMPLIANT" with values.
        # Otherwise, return "COMPLIANT".
        current_non_compliant_configs, desired_configs = Comparator.get_non_compliant_configs(
            current, desired, comparator_option=ComparatorOptionForList.COMPARE_AFTER_SORT
        )
        if current_non_compliant_configs or desired_configs:
            result = {
                consts.STATUS: ComplianceStatus.NON_COMPLIANT,
                consts.CURRENT: current_non_compliant_configs,
                consts.DESIRED: desired_configs,
            }
        else:
            result = {consts.STATUS: ComplianceStatus.COMPLIANT}
        return result
