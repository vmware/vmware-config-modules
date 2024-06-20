# Copyright 2024 Broadcom. All Rights Reserved.
import os
from pathlib import Path

from config_modules_vmware.services.config import Config


class TestConfig:

    def setup_method(self):
        Config._conf = None
        os.environ.pop('OVERRIDES_PATH', None)

    def test_default_config(self):
        vcenter_rest_config = Config().get_section("vcenter.rest")
        assert vcenter_rest_config.getint('APITimeoutSeconds') == 30
        assert vcenter_rest_config.getint('TaskTimeoutSeconds') == 300
        vcenter_rest_config = Config().get_section("sddc_manager.rest")
        assert vcenter_rest_config.getint('APITimeoutSeconds') == 30

    def test_default_config_with_overrides_path(self):
        os.environ['OVERRIDES_PATH'] = "overrides_path"
        vcenter_rest_config = Config().get_section("vcenter.rest")
        assert vcenter_rest_config.getint('APITimeoutSeconds') == 30
        assert vcenter_rest_config.getint('TaskTimeoutSeconds') == 300
        vcenter_rest_config = Config().get_section("sddc_manager.rest")
        assert vcenter_rest_config.getint('APITimeoutSeconds') == 30

    def test_override_config(self):
        os.environ['OVERRIDES_PATH'] = os.getcwd()
        override_file_path = Path(os.getcwd()) / "config-overrides.ini"
        try:
            with open(override_file_path, "w") as fp:
                fp.write(
                    """
                    [vcenter.rest]
                    APITimeoutSeconds=10
    
                    [sddc_manager.rest]
                    APITimeoutSeconds=20
                    """
                )
            vcenter_rest_config = Config().get_section("vcenter.rest")
            assert vcenter_rest_config.getint('APITimeoutSeconds') == 10
            assert vcenter_rest_config.getint('TaskTimeoutSeconds') == 300
            vcenter_rest_config = Config().get_section("sddc_manager.rest")
            assert vcenter_rest_config.getint('APITimeoutSeconds') == 20
        finally:
            os.remove(override_file_path)
