# Copyright 2024 Broadcom. All Rights Reserved.
from mock import MagicMock

from config_modules_vmware.controllers.esxi.password_reuse_restriction_policy import PasswordReuseRestrictionPolicy
from config_modules_vmware.controllers.esxi.password_reuse_restriction_policy import SETTINGS_NAME
from config_modules_vmware.tests.controllers.esxi.test_password_max_lifetime_policy import HelperTestEsxAdvControls


class TestPasswordReuseRestrictionPolicy:
    def setup_method(self):
        self.controller = PasswordReuseRestrictionPolicy()
        self.desired_configs = 5
        self.non_compliant_configs = 40
        self.mock_host_ref = MagicMock()
        self.mock_host_ref.name = 'host-1'
        self.option_string = SETTINGS_NAME

    def test_get_success(self):
        HelperTestEsxAdvControls.helper_test_get_success(self.controller, self.mock_host_ref,
                                                         self.option_string, self.desired_configs)

    def test_get_failed(self):
        HelperTestEsxAdvControls.helper_test_get_failed(self.controller, self.mock_host_ref,
                                                        self.option_string, self.desired_configs)

    def test_get_failed_invalid_name(self):
        HelperTestEsxAdvControls.helper_test_get_failed_invalid_name(self.controller, self.mock_host_ref,
                                                                     self.option_string, self.desired_configs)

    def test_get_failed_empty_options(self):
        HelperTestEsxAdvControls.helper_test_get_failed_empty_options(self.controller, self.mock_host_ref,
                                                                      self.option_string, self.desired_configs)

    def test_set_success(self):
        HelperTestEsxAdvControls.helper_test_set_success(self.controller, self.mock_host_ref, self.desired_configs)

    def test_set_failed(self):
        HelperTestEsxAdvControls.helper_test_set_failed(self.controller, self.mock_host_ref, self.desired_configs)

    def test_check_compliance_compliant(self):
        HelperTestEsxAdvControls.helper_test_check_compliance_compliant(self.controller, self.mock_host_ref,
                                                                        self.option_string, self.desired_configs)

    def test_check_compliance_non_compliant(self):
        HelperTestEsxAdvControls.helper_test_check_compliance_non_compliant(self.controller, self.mock_host_ref,
                                                                            self.option_string, self.desired_configs,
                                                                            self.non_compliant_configs)

    def test_remediate(self):
        HelperTestEsxAdvControls.helper_test_remediate_success(self.controller, self.mock_host_ref,
                                                               self.option_string, self.desired_configs,
                                                               self.non_compliant_configs)

    def test_remediate_with_already_compliant(self):
        HelperTestEsxAdvControls.helper_test_remediate_on_already_compliant_system(self.controller,
                                                                                     self.mock_host_ref,
                                                                                     self.option_string,
                                                                                     self.desired_configs)
