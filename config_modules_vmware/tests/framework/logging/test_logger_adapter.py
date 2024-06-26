# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from mock import patch

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata


class TestLoggerAdapter:

    @patch('config_modules_vmware.schemas.schema_utility.retrieve_reference_schema')
    @patch('config_modules_vmware.services.config.Config.get_section')
    @patch('config_modules_vmware.framework.logging.logging_context.LoggingContext.get_hostname_context')
    @patch('config_modules_vmware.framework.logging.logging_context.LoggingContext.get_controller_metadata_context')
    def test_logging_format(
            self,
            mock_logging_metadata_context,
            mock_logging_hostname_context,
            mock_config_get_section,
            mock_retrieve_schema,
            caplog
    ):
        mock_retrieve_schema.return_value = {
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
        test_name = "sample_controller_name"
        test_configuration_id = "9999"
        test_path_in_schema = "compliance_config.test_product.test_controller"
        test_title = "test metadata"
        test_tags = ["tag"]
        test_version = "1.0.0"
        test_since = "since"
        test_products = [BaseContext.ProductEnum.VCENTER]
        test_components = ["component"]
        test_status = ControllerMetadata.ControllerStatus.ENABLED
        test_impact = ControllerMetadata.RemediationImpact.REMEDIATION_SKIPPED
        test_scope = "scope"
        test_type = ControllerMetadata.ControllerType.COMPLIANCE

        test_metadata = ControllerMetadata(
            name=test_name,
            configuration_id=test_configuration_id,
            path_in_schema=test_path_in_schema,
            title=test_title,
            tags=test_tags,
            version=test_version,
            since=test_since,
            products=test_products,
            components=test_components,
            status=test_status,
            impact=test_impact,
            scope=test_scope,
            type=test_type,
        )

        mock_logging_metadata_context.return_value = test_metadata

        test_hostname = "vcenter-1.vrack.vsphere.local"
        mock_logging_hostname_context.return_value = test_hostname

        log_format = ("{hostname} - {controller_name} - {configuration_id} - {path_in_schema} - {title} - {tags} - "
                      "{version} - {since} - {products} - {components} - {status} - {impact} - {scope} - {type} - "
                      "{msg}")
        mock_config_get_section.return_value = {
            "Format": log_format
        }

        expected_log = (f"{test_hostname} - {test_name} - {test_configuration_id} - {test_path_in_schema} - "
                        f"{test_title} - {test_tags} - {test_version} - {test_since} - "
                        f"{test_products[0].value} - {test_components} - {test_status.value} - "
                        f"{test_impact.value} - {test_scope} - {test_type.value} - TEST ARG")

        caplog.set_level(logging.INFO)
        logger = LoggerAdapter(logging.getLogger(__name__))

        logger.info("TEST %s", "ARG")
        assert expected_log in caplog.text

    @patch('config_modules_vmware.services.config.Config.get_section')
    def test_logging_no_format(
            self,
            mock_config_get_section,
            caplog
    ):
        mock_config_get_section.return_value = {
            "Format": None
        }

        expected_log = "TEST ARG"
        caplog.set_level(logging.INFO)
        logger = LoggerAdapter(logging.getLogger(__name__))

        logger.info("TEST %s", "ARG")
        assert expected_log in caplog.text
