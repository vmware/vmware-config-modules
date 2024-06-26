# Copyright 2024 Broadcom. All Rights Reserved.
import os

import pytest
from mock import patch

from config_modules_vmware.controllers.vcenter.ntp_config import NtpConfig
from config_modules_vmware.services.mapper import mapper_utils


class TestMapperUtils:

    @patch('logging.Logger.error')
    def test_get_class_success(self, logger_error_mock):
        module_path = 'config_modules_vmware.controllers.vcenter.ntp_config.NtpConfig'
        result = mapper_utils.get_class(module_path)

        # Assert expected results
        ntp_config_obj = result()
        assert isinstance(ntp_config_obj, NtpConfig)
        logger_error_mock.assert_not_called()

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    def test_get_class_module_not_found(self, get_class_mock):
        module_path = 'non_existent_module.NonExistentClass'
        # Mock ModuleNotFoundError
        get_class_mock.side_effect = ModuleNotFoundError(
            "Could not load module from path non_existent_module.NonExistentClass")

        with pytest.raises(ModuleNotFoundError,
                           match="Could not load module from path non_existent_module.NonExistentClass"):
            mapper_utils.get_class(module_path)

        # Assert expected results
        get_class_mock.assert_called_once_with('non_existent_module.NonExistentClass')

    def test_get_mapping_template(self):
        with patch('config_modules_vmware.framework.utils.utils.read_json_file') as read_json_mock:
            read_json_mock.return_value = {
                "dummy_key": "dummy_value"
            }
            result = mapper_utils.get_mapping_template(mapper_utils.COMPLIANCE_MAPPING_FILE)

            # Assert expected results
            read_json_mock.assert_called_once_with(
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                             "services/mapper/control_config_mapping.json"))

            expected_result = {
                "dummy_key": "dummy_value"
            }
            assert result == expected_result
