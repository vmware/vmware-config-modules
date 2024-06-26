# Copyright 2024 Broadcom. All Rights Reserved.
from mock.mock import patch

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.logging.logging_context import ControllerMetadataLoggingContext
from config_modules_vmware.framework.logging.logging_context import HostnameLoggingContext
from config_modules_vmware.framework.logging.logging_context import LoggingContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata


class TestLoggingContext:

    def setup_method(self):
        self.mock_compliance_schema = \
            {
                "type": "object",
                "properties": {
                    "compliance_config": {
                        "type": "object",
                        "properties": {
                            "test_product": {
                                "type": "object",
                                "properties": {
                                    "test_controller": {
                                        "properties": {
                                            "value": {
                                                "type": "boolean",
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

    @patch('config_modules_vmware.schemas.schema_utility.retrieve_reference_schema')
    def test_controller_metadata_logging_context(self, mock_retrieve_schema):
        mock_retrieve_schema.return_value = self.mock_compliance_schema
        test_controller_metadata = ControllerMetadata(
            name="sample_controller_name",
            path_in_schema="compliance_config.test_product.invalid_key",
            configuration_id="9999",
            title="test metadata",
            version="1.0.0",
            products=[BaseContext.ProductEnum.VCENTER],
            status=ControllerMetadata.ControllerStatus.ENABLED,
        )

        metadata_context = LoggingContext.get_controller_metadata_context()
        assert metadata_context is None

        token = LoggingContext.set_controller_metadata_context(test_controller_metadata)
        metadata_context = LoggingContext.get_controller_metadata_context()
        assert metadata_context == test_controller_metadata

        LoggingContext.reset_controller_metadata_context(token)
        metadata_context = LoggingContext.get_controller_metadata_context()
        assert metadata_context is None

    def test_hostname_logging_context(self):
        test_hostname = "test_hostname"

        hostname_context = LoggingContext.get_hostname_context()
        assert hostname_context is None

        token = LoggingContext.set_hostname_context(test_hostname)
        hostname_context = LoggingContext.get_hostname_context()
        assert hostname_context == test_hostname

        LoggingContext.reset_hostname_context(token)
        hostname_context = LoggingContext.get_hostname_context()
        assert hostname_context is None

    @patch('config_modules_vmware.schemas.schema_utility.retrieve_reference_schema')
    def test_controller_metadata_context(self, mock_retrieve_schema):
        mock_retrieve_schema.return_value = self.mock_compliance_schema
        test_controller_metadata = ControllerMetadata(
            name="sample_controller_name",
            path_in_schema="compliance_config.test_product.invalid_key",
            configuration_id="9999",
            title="test metadata",
            version="1.0.0",
            products=[BaseContext.ProductEnum.VCENTER],
            status=ControllerMetadata.ControllerStatus.ENABLED,
        )

        with ControllerMetadataLoggingContext(test_controller_metadata):
            assert LoggingContext.get_controller_metadata_context() == test_controller_metadata

        assert LoggingContext.get_controller_metadata_context() is None

    def test_hostname_context(self):
        test_hostname = "test_hostname"

        with HostnameLoggingContext(test_hostname):
            assert LoggingContext.get_hostname_context() == test_hostname

        assert LoggingContext.get_hostname_context() is None
