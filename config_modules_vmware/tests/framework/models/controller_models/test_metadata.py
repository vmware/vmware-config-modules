# Copyright 2024 Broadcom. All Rights Reserved.
from mock import patch

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata


class TestMetadata:

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
    def test_create_metadata_with_valid_path(self, mock_retrieve_schema):
        mock_retrieve_schema.return_value = self.mock_compliance_schema
        test_name = "sample_controller_name"
        test_path_in_schema = "compliance_config.test_product.test_controller"
        test_configuration_id = "9999"
        test_title = "test metadata"
        test_version = "1.0.0"
        test_products = [BaseContext.ProductEnum.VCENTER]
        test_status = ControllerMetadata.ControllerStatus.ENABLED
        test_controller_metadata = ControllerMetadata(
            name=test_name,
            path_in_schema=test_path_in_schema,
            configuration_id=test_configuration_id,
            title=test_title,
            version=test_version,
            products=test_products,
            status=test_status,
        )

        expected_spec = {"type": "boolean"}

        assert test_controller_metadata.name == test_name
        assert test_controller_metadata.path_in_schema == test_path_in_schema
        assert test_controller_metadata.configuration_id == test_configuration_id
        assert test_controller_metadata.title == test_title
        assert test_controller_metadata.version == test_version
        assert test_controller_metadata.products == test_products
        assert test_controller_metadata.status == test_status
        assert test_controller_metadata.spec == expected_spec

    @patch('config_modules_vmware.schemas.schema_utility.retrieve_reference_schema')
    def test_create_metadata_with_invalid_path(self, mock_retrieve_schema):
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

        expected_spec = {}
        assert test_controller_metadata.spec == expected_spec

    def test_create_metadata_for_configuration_controller(self):
        test_name = "sample_controller_name"
        test_path_in_schema = "compliance_config.test_product.test_controller"
        test_configuration_id = "9999"
        test_title = "test metadata"
        test_version = "1.0.0"
        test_products = [BaseContext.ProductEnum.VCENTER]
        test_status = ControllerMetadata.ControllerStatus.ENABLED
        test_type = ControllerMetadata.ControllerType.CONFIGURATION
        test_controller_metadata = ControllerMetadata(
            name=test_name,
            path_in_schema=test_path_in_schema,
            configuration_id=test_configuration_id,
            title=test_title,
            version=test_version,
            products=test_products,
            status=test_status,
            type=test_type
        )

        expected_spec = {}

        assert test_controller_metadata.name == test_name
        assert test_controller_metadata.path_in_schema == test_path_in_schema
        assert test_controller_metadata.configuration_id == test_configuration_id
        assert test_controller_metadata.title == test_title
        assert test_controller_metadata.version == test_version
        assert test_controller_metadata.products == test_products
        assert test_controller_metadata.status == test_status
        assert test_controller_metadata.type == test_type
        assert test_controller_metadata.spec == expected_spec

    def test_validate_with_valid_params(self):
        test_controller_metadata = ControllerMetadata(
            name="sample_controller_name",
            path_in_schema="compliance_config.test_product.invalid_key",
            configuration_id="9999",
            title="test metadata",
            version="1.0.0",
            products=[BaseContext.ProductEnum.VCENTER],
            status=ControllerMetadata.ControllerStatus.ENABLED,
        )
        assert test_controller_metadata.validate()

    def test_validate_disabled_status(self):
        test_controller_metadata = ControllerMetadata(
            status=ControllerMetadata.ControllerStatus.DISABLED,
        )
        assert test_controller_metadata.validate()

    def test_validate_with_invalid_param_type(self):
        test_controller_metadata = ControllerMetadata(
            name="sample_controller_name",
            path_in_schema="compliance_config.test_product.invalid_key",
            configuration_id="9999",
            title="test metadata",
            version=1,
            products=[BaseContext.ProductEnum.VCENTER],
            status=ControllerMetadata.ControllerStatus.ENABLED,
        )
        assert not test_controller_metadata.validate()

    def test_validate_with_missing_required_param(self):
        test_controller_metadata = ControllerMetadata(
            name="sample_controller_name",
            path_in_schema="compliance_config.test_product.invalid_key",
            configuration_id="9999",
            title="test metadata",
            products=[BaseContext.ProductEnum.VCENTER],
            status=ControllerMetadata.ControllerStatus.ENABLED,
        )
        assert not test_controller_metadata.validate()

    @patch('config_modules_vmware.schemas.schema_utility.retrieve_reference_schema')
    def test_to_dict(self, mock_retrieve_schema):
        mock_retrieve_schema.return_value = self.mock_compliance_schema
        test_name = "sample_controller_name"
        test_path_in_schema = "compliance_config.test_product.test_controller"
        test_configuration_id = "9999"
        test_title = "test metadata"
        test_version = "1.0.0"
        test_products = [BaseContext.ProductEnum.VCENTER]
        test_status = ControllerMetadata.ControllerStatus.ENABLED
        test_controller_metadata = ControllerMetadata(
            name=test_name,
            path_in_schema=test_path_in_schema,
            configuration_id=test_configuration_id,
            title=test_title,
            version=test_version,
            products=test_products,
            status=test_status,
        )

        expected_dict = {'components': [],
                         'configuration_id': test_configuration_id,
                         'impact': None,
                         'name': test_name,
                         'path_in_schema': test_path_in_schema,
                         'products': test_products,
                         'scope': None,
                         'type': ControllerMetadata.ControllerType.COMPLIANCE,
                         'since': None,
                         'status': test_status,
                         'tags': [],
                         'title': test_title,
                         'version': test_version,
                         'functional_test_targets': []}

        assert test_controller_metadata.to_dict(always_include_defaults=True) == expected_dict

    @patch('config_modules_vmware.schemas.schema_utility.retrieve_reference_schema')
    def test_to_dict_extra_args(self, mock_retrieve_schema):
        mock_retrieve_schema.return_value = self.mock_compliance_schema
        test_name = "sample_controller_name"
        test_path_in_schema = "compliance_config.test_product.test_controller"
        test_configuration_id = "9999"
        test_title = "test metadata"
        test_version = "1.0.0"
        test_products = [BaseContext.ProductEnum.VCENTER]
        test_status = ControllerMetadata.ControllerStatus.ENABLED
        test_controller_metadata = ControllerMetadata(
            name=test_name,
            path_in_schema=test_path_in_schema,
            configuration_id=test_configuration_id,
            title=test_title,
            version=test_version,
            products=test_products,
            status=test_status,
            extra_arg1="unused_arg",
            extra_arg2=123,
        )

        expected_dict = {'components': [],
                         'configuration_id': test_configuration_id,
                         'impact': None,
                         'name': test_name,
                         'path_in_schema': test_path_in_schema,
                         'products': test_products,
                         'scope': None,
                         'type': ControllerMetadata.ControllerType.COMPLIANCE,
                         'since': None,
                         'status': test_status,
                         'tags': [],
                         'title': test_title,
                         'version': test_version,
                         'functional_test_targets': []}

        assert test_controller_metadata.to_dict(always_include_defaults=True) == expected_dict
