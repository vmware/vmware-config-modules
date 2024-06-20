# Copyright 2024 Broadcom. All Rights Reserved.
import yaml

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.schemas.schema_utility import retrieve_reference_schema
from config_modules_vmware.services.mapper.mapper_utils import COMPLIANCE_MAPPING_FILE
from config_modules_vmware.services.mapper.mapper_utils import get_class
from config_modules_vmware.services.mapper.mapper_utils import get_mapping_template
from functional_tests.utils.constants import AUTH_CONTEXT
from functional_tests.utils.constants import COMPLIANCE_VALUES
from functional_tests.utils.constants import CONTROL
from functional_tests.utils.constants import DRIFT_VALUES
from functional_tests.utils.constants import HOST_NAME
from functional_tests.utils.constants import PRODUCT
from functional_tests.utils.constants import REMEDIATION
from functional_tests.utils.constants import ROLLBACK
from functional_tests.utils.constants import SSH_CREDENTIAL
from functional_tests.utils.constants import TEST_TARGET
from functional_tests.utils.control_util import render_template
from functional_tests.utils.file_util import read_file


class InputOptions:
    def __init__(
        self,
        control_include_dict=None,
        control_exclude_dict=None,
        compliance_values_file=None,
        drift_values_file=None,
        context_dict=None,
        ssh_credential_dict=None,
        rollback=False,
    ):
        self.control_include_dict = control_include_dict
        self.control_exclude_dict = control_exclude_dict
        self.compliance_values_file = compliance_values_file
        self.drift_values_file = drift_values_file
        self.context_dict = context_dict
        self.ssh_credential_dict = ssh_credential_dict
        self.rollback = rollback


class ComplianceTemplate:
    schema = retrieve_reference_schema("compliance")
    config_mapping_template = get_mapping_template(COMPLIANCE_MAPPING_FILE)
    compliance_variable_values = {}
    drift_variable_values = {}

    @classmethod
    def _append_path(cls, path, key):
        if key not in ["properties", "metadata"]:
            new_path = path.copy()
            new_path.append(key)
            return new_path
        else:
            return path

    @classmethod
    def _generate_template_test_data(cls, json_path, input_options, product_control_ctx_lst, test_ids):
        product_name, control_name, control_class, product_template_variable = cls._get_control_name_template_variable(
            json_path
        )
        context_dict = input_options.context_dict
        ssh_credential_dict = input_options.ssh_credential_dict

        compliance_values = None
        drift_values = None
        if (
            cls._is_control_included(product_name, control_name, input_options)
            and product_name in [*BaseContext.ProductEnum]
            and (product_name in context_dict or product_name in ssh_credential_dict)
        ):
            template_content = cls._generate_control_template(json_path, control_name, product_template_variable)
            product_enum = BaseContext.ProductEnum(product_name)
            contexts = context_dict[product_enum] if product_enum in context_dict else {}
            credentials = ssh_credential_dict[product_enum] if product_enum in ssh_credential_dict else {}
            if compliance_values is None:
                compliance_values = render_template(
                    template_content,
                    cls.compliance_variable_values,
                    control_name + " compliance values",
                    product_template_variable,
                )
            if drift_values is None:
                drift_values = render_template(
                    template_content,
                    cls.drift_variable_values,
                    control_name + " drift values",
                    product_template_variable,
                )
            print(f"control class {control_class}")
            control_call_ref = get_class(control_class)
            if control_call_ref.metadata.impact == ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED:
                remediation = False
            else:
                remediation = True

            if control_call_ref.metadata.status != ControllerMetadata.ControllerStatus.ENABLED:
                print(f"product control - {product_name}:{control_name} is disabled")
            elif compliance_values is not None and drift_values is not None:
                if hasattr(control_call_ref, "metadata"):
                    if (
                        hasattr(control_call_ref.metadata, "functional_test_targets")
                        and len(control_call_ref.metadata.functional_test_targets) != 0
                        and "remote" not in control_call_ref.metadata.functional_test_targets
                    ):
                        # Product and target name are the same. control has only one target.
                        test_target = product_name
                        for credential in credentials:
                            product_control_ctx_lst.append(
                                {
                                    PRODUCT: product_name,
                                    CONTROL: control_name,
                                    AUTH_CONTEXT: {},
                                    COMPLIANCE_VALUES: compliance_values,
                                    DRIFT_VALUES: drift_values,
                                    ROLLBACK: input_options.rollback,
                                    TEST_TARGET: test_target,
                                    REMEDIATION: remediation,
                                    SSH_CREDENTIAL: credential,
                                    HOST_NAME: credential.hostname,
                                }
                            )
                            test_ids.append(f"{product_name}_{control_name}_{credential.hostname}")
                    else:
                        test_target = ""
                        for hostname in contexts:
                            product_control_ctx_lst.append(
                                {
                                    PRODUCT: product_name,
                                    CONTROL: control_name,
                                    AUTH_CONTEXT: contexts[hostname],
                                    COMPLIANCE_VALUES: compliance_values,
                                    DRIFT_VALUES: drift_values,
                                    ROLLBACK: input_options.rollback,
                                    TEST_TARGET: test_target,
                                    REMEDIATION: remediation,
                                    HOST_NAME: hostname,
                                    SSH_CREDENTIAL: {},
                                }
                            )
                            test_ids.append(f"{product_name}_{control_name}_{hostname}")

    @classmethod
    def _get_control_name_template_variable(cls, json_path):
        # find the control's product list from config_mapping_template using json path
        product_dict = cls.config_mapping_template

        template_variable = None
        control_name = None
        product = None
        for item in json_path:
            if isinstance(product_dict, dict) and item in product_dict.keys():
                product_dict = product_dict[item]
                # Template variable is created by concatenating all keys on the json path with "_" among them.
                if item != "compliance_config":
                    template_variable = item if template_variable is None else template_variable + "_" + item
                    control_name = item
                    if product is None:
                        product = item
            else:
                print(f"Control {json_path} is not configured in control_config_mapping.json\n")
        return product, control_name, product_dict, template_variable

    @classmethod
    def _generate_control_template(cls, json_path, control_name, template_variable):
        configure_id = 00000
        metadata = (
            '"metadata": {"configuration_id": ' + f'"{configure_id}", ' + f'"configuration_title": '
            f'"{control_name} configurations"' + "}"
        )
        template_content = "{" + f"{metadata}, " + '"value": {{' + f"{template_variable} | tojson" + " }} }"
        json_path.reverse()
        for item in json_path:
            template_content = f'"{item}": ' + template_content
            template_content = "{ " + template_content + " }"
        json_path.reverse()
        return template_content

    @classmethod
    def _is_control_included(cls, product_name, control_name, input_options):
        if (
            product_name in input_options.control_exclude_dict.keys()
            and control_name in input_options.control_exclude_dict[product_name]
        ):
            return False
        elif (
            product_name in input_options.control_include_dict.keys()
            and (
                control_name in input_options.control_include_dict[product_name]
                or len(input_options.control_include_dict[product_name]) == 0
            )
        ) or len(input_options.control_include_dict.keys()) == 0:
            return True
        else:
            return False

    @classmethod
    def _find_value_generate_templates_generate_test_data(
        cls, path, obj, target_key, input_options, product_control_ctx_lst, test_ids
    ):
        try:
            if isinstance(obj, dict):
                for key, value in obj.items():  # dict?
                    if key == target_key:
                        cls._generate_template_test_data(path, input_options, product_control_ctx_lst, test_ids)
                    elif isinstance(value, dict) and key != "definitions":
                        cls._find_value_generate_templates_generate_test_data(
                            cls._append_path(path, key),
                            value,
                            target_key,
                            input_options,
                            product_control_ctx_lst,
                            test_ids,
                        )

        except AttributeError as e:
            print(f"Exception {e}")

    @classmethod
    def generate_compliance_templates_test_data(cls, input_options):
        """
        Generate all compliance templates based on compliance schema
        :param input_options: pytest input options.
        :type: InputOptions
        :return: List of product_control or errors (for failure).
        :rtype: Dict
        """
        # list of test data: product, control, context, compliance  values, drift values
        product_control_ctx_lst = []
        # List of test ids
        test_ids = []

        cls.compliance_variable_values = yaml.safe_load(read_file(input_options.compliance_values_file))
        cls.drift_variable_values = yaml.safe_load(read_file(input_options.drift_values_file))
        cls._find_value_generate_templates_generate_test_data(
            [], cls.schema, "value", input_options, product_control_ctx_lst, test_ids
        )
        return product_control_ctx_lst, test_ids
