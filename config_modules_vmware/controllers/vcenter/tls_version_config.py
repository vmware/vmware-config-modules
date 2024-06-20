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


class TlsVersion(BaseController):
    """Class to implement get and set methods for configuring and enabling specified TLS versions.
    For 4411 it supports multiple TLS versions - TLSv1.0, TLSv1.1, TLSv1.2
    For 5x onwards only supported version is TLSv1.2

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
            "PATH": "/usr/sbin/",
        }
        return environment

    def _generate_remediate_commands(self, services_to_tls_versions: Dict = None) -> List[str]:
        """
        Return list of commands to be executed for remediation.
        :param services_to_tls_versions: Non-compliant services to tls versions data.
        :type: dict
        :return: List of remediation commands.
        :rtype: list
        """

        if not services_to_tls_versions:
            return []

        tls_to_services = {}
        for service, tls_versions in services_to_tls_versions.items():
            if NOT_RUNNING not in tls_versions:
                tls_key = tuple(sorted(tls_versions))
                if tls_key not in tls_to_services:
                    tls_to_services[tls_key] = [service]
                else:
                    tls_to_services[tls_key].append(service)

        remediation_commands = []

        # If all services require same TLS versions, use <script update -p [TLS versions]>
        if len(tls_to_services) == 1:
            tls_versions = list(tls_to_services.keys())[0]
            command = "{} {} -p {} --quiet".format(
                RECONFIGURE_VC_TLS_SCRIPT_PATH, UPDATE_COMMAND, " ".join(tls_versions)
            )
            remediation_commands.append(command)
        else:
            for tls_versions, services in sorted(tls_to_services.items()):
                # Last command so restart the services
                # Use command  <script update -s [services] -p [TLS versions] --quiet>
                if len(remediation_commands) == len(tls_to_services) - 1:
                    command = "{} {} -s {} -p {} --quiet".format(
                        RECONFIGURE_VC_TLS_SCRIPT_PATH,
                        UPDATE_COMMAND,
                        " ".join(services),
                        " ".join(tls_versions),
                    )
                else:
                    # Add '--no-restart' for all the commands except last one.
                    # Use command  <script update -s [services] -p [TLS versions] --quiet --no-restart>
                    command = "{} {} -s {} -p {} --quiet --no-restart".format(
                        RECONFIGURE_VC_TLS_SCRIPT_PATH,
                        UPDATE_COMMAND,
                        " ".join(services),
                        " ".join(tls_versions),
                    )
                remediation_commands.append(command)

        return remediation_commands

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
        [High risk remediation]: Set requires restart of the services post changing the TLS version.

        :param context: Product context instance.
        :type context: VcenterContext
        :param desired_values: Desired values with keys as services and values as TLS versions.
        :type desired_values: Dict
        :return: Dict of status (RemediateStatus.SKIPPED) and errors if any
        :rtype: Tuple
        """
        logger.info("Setting TLS versions for all the services.")
        errors = []
        try:
            services_to_tls_versions = desired_values
            remediation_commands = self._generate_remediate_commands(services_to_tls_versions)
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
        # If errors are seen during get, return "FAILED" status with errors.
        if errors:
            return {consts.STATUS: ComplianceStatus.FAILED, consts.ERRORS: errors}

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

    def remediate(self, context: VcenterContext, desired_values: Dict) -> Dict:
        """
        It is a high-risk remediation as it requires restart of services/vCenter.
        Post updating the TLS versions, services are restarted as part of the implementation.

        :param context: Product context instance.
        :param desired_values: Desired value for the tls versions for the vCenter services.
        :return: Dict of status and errors if any
        """
        logger.info("Running remediation for vCenter TLS control")
        # Call check compliance and check for current compliance status.
        compliance_response = self.check_compliance(context=context, desired_values=desired_values)

        if compliance_response.get(consts.STATUS) == ComplianceStatus.FAILED:
            # For compliance_status as "FAILED", return FAILED with errors.
            return {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: compliance_response.get(consts.ERRORS, [])}

        elif compliance_response.get(consts.STATUS) == ComplianceStatus.COMPLIANT:
            # For compliant case, return SUCCESS.
            return {consts.STATUS: RemediateStatus.SUCCESS}

        elif compliance_response.get(consts.STATUS) != ComplianceStatus.NON_COMPLIANT:
            # Raise exception for unexpected compliance status (other than FAILED, COMPLIANT, NON_COMPLIANT).
            raise Exception("Error during remediation. Unexpected compliant status found.")

        # Configs are non_compliant, call set to remediate them.
        status, errors = self.set(context=context, desired_values=compliance_response.get(consts.DESIRED))
        if not errors:
            result = {
                consts.STATUS: status,
                consts.OLD: compliance_response.get(consts.CURRENT),
                consts.NEW: compliance_response.get(consts.DESIRED),
            }
        else:
            result = {consts.STATUS: RemediateStatus.FAILED, consts.ERRORS: errors}
        return result
