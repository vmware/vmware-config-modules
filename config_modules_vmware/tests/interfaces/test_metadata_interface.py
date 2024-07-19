# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import MagicMock
from mock import patch

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.interfaces.metadata_interface import ControllerMetadataInterface


class TestMetadataInterface:

    @staticmethod
    def create_mock_controller_class(configuration_id, tags=None, impact=None):
        if tags is None:
            tags = ["test_tag1", "test_tag2"]

        class MockController:
            logger = MagicMock()
            metadata = ControllerMetadata(
                name="TestController",  # Controller name
                path_in_schema="compliance_config.sample_product.sample_controller_name",
                # path in the schema to this controller's definition.
                configuration_id=configuration_id,  # Configuration ID as defined in compliance kit.
                title="test controller title",  # Controller title as defined in compliance kit.
                tags=tags,  # controller tags for future querying and filtering
                version="1.0.0",  # version of the controller implementation.
                since="",  # version when the controller was first introduced in the compliance kit.
                products=[BaseContext.ProductEnum.VCENTER],  # product from enum in BaseContext.
                components=[],  # subcomponent within the product if applicable.
                status=ControllerMetadata.ControllerStatus.ENABLED,  # used to enable/disable a controller
                impact=impact,
                # from enum in ControllerMetadata.RemediationImpact.
                scope="",
                # any information or limitations about how the controller operates. i.e. runs as a CLI on VCSA.
            )

        return MockController

    def setup_method(self):
        self.config_mapping_template = \
            {
                "compliance_config": {
                    "test_product": {
                        "test_controller": "path_to_class",
                        "test_controller_two": "path_to_class"
                    }
                }
            }
        self.expected_metadata_before_update = {
            "name": "TestController",
            "configuration_id": "1234",
            "path_in_schema": "compliance_config.sample_product.sample_controller_name",
            "title": "test controller title",
            "tags": [
                "test_tag1",
                "test_tag2"
            ],
            "version": "1.0.0",
            "since": "",
            "products": [
                "vcenter"
            ],
            "components": [],
            "status": "ENABLED",
            "impact": None,
            "scope": "",
            "type": "COMPLIANCE",
            "functional_test_targets": []
        }
        self.expected_metadata_after_update = {
            "name": "TestController",
            "configuration_id": "1234",
            "path_in_schema": "compliance_config.sample_product.sample_controller_name",
            "title": "This is my new overridden title",
            "tags": [
                "test_tag1",
                "test_tag2"
            ],
            "version": "1.0.0",
            "since": "",
            "products": [
                "vcenter"
            ],
            "components": [],
            "status": "ENABLED",
            "impact": None,
            "scope": "",
            "type": "COMPLIANCE",
            "functional_test_targets": [],
            "new_metadata_key": "new_metadata_value",
            "new_complex_metadata": {
                "child_new_metadata_key": "child_new_metadata_value"
            }
        }

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_controller_not_found(self, mapper_get_mapping_template_mock,
                                                 mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mapper_get_class_mock.side_effect = Exception("Could not load module.")
        query_id = "1234"
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_id(query_id))
        expected_result = []
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_controller_no_metadata(self, mapper_get_mapping_template_mock,
                                                   mapper_get_class_mock):
        mock_controller_class = self.create_mock_controller_class("1234")
        del mock_controller_class.metadata
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mapper_get_class_mock.return_value = mock_controller_class
        query_id = "1234"
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_id(query_id))
        expected_result = []
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_by_id_single_match(self, mapper_get_mapping_template_mock,
                                               mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_classes = [self.create_mock_controller_class("1234"),
                                   self.create_mock_controller_class("5678")]
        mapper_get_class_mock.side_effect = mock_controller_classes
        query_id = "1234"
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_id(query_id))
        expected_result = [mock_controller_classes[0].metadata.to_dict(always_include_defaults=True)]
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_by_id_single_no_match(self, mapper_get_mapping_template_mock,
                                                  mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_classes = [self.create_mock_controller_class("5678"),
                                   self.create_mock_controller_class("7890")]
        mapper_get_class_mock.side_effect = mock_controller_classes
        query_id = "1234"
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_id(query_id))
        expected_result = []
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_by_id_list_match(self, mapper_get_mapping_template_mock,
                                             mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        query_ids = ["1234", "5678"]
        mock_controller_classes = [self.create_mock_controller_class("1234"),
                                   self.create_mock_controller_class("5678")]
        mapper_get_class_mock.side_effect = mock_controller_classes
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_id(query_ids))
        expected_result = [mock_controller_class.metadata.to_dict(always_include_defaults=True) for
                           mock_controller_class in
                           mock_controller_classes]
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_by_id_list_no_match(self, mapper_get_mapping_template_mock,
                                                mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        query_ids = ["1234", "5678"]
        mock_controller_classes = [self.create_mock_controller_class("1234"),
                                   self.create_mock_controller_class("7890")]
        mapper_get_class_mock.side_effect = mock_controller_classes
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_id(query_ids))
        expected_result = [mock_controller_classes[0].metadata.to_dict(always_include_defaults=True)]
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_by_tag_single_match(self, mapper_get_mapping_template_mock,
                                                mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        query_tag = "matching_tag"
        mock_controller_classes = [self.create_mock_controller_class("1234", tags=[query_tag]),
                                   self.create_mock_controller_class("5678")]
        mapper_get_class_mock.side_effect = mock_controller_classes
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_tag(query_tag))
        expected_result = [mock_controller_classes[0].metadata.to_dict(always_include_defaults=True)]
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_by_tag_multi_match(self, mapper_get_mapping_template_mock,
                                               mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_classes = [self.create_mock_controller_class("1234"),
                                   self.create_mock_controller_class("5678")]
        query_tag = "test_tag1"
        mapper_get_class_mock.side_effect = mock_controller_classes
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_tag(query_tag))
        expected_result = [mock_controller_class.metadata.to_dict(always_include_defaults=True) for
                           mock_controller_class in
                           mock_controller_classes]
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_query_by_tag_no_match(self, mapper_get_mapping_template_mock,
                                            mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_classes = [self.create_mock_controller_class("1234"),
                                   self.create_mock_controller_class("5678")]
        query_tag = "non_matching_tag"
        mapper_get_class_mock.side_effect = mock_controller_classes
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            ControllerMetadataInterface.query_by_tag(query_tag))
        expected_result = []
        assert controllers_query_id == expected_result

    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_metadata_lambda_query_by_impact(self, mapper_get_mapping_template_mock,
                                             mapper_get_class_mock):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_classes = [
            self.create_mock_controller_class(
                "1234",
                impact=ControllerMetadata.RemediationImpact.RESTART_REQUIRED),
            self.create_mock_controller_class("5678")]
        mapper_get_class_mock.side_effect = mock_controller_classes
        controllers_query_id = ControllerMetadataInterface.get_metadata_from_query(
            lambda metadata: metadata.impact != ControllerMetadata.RemediationImpact.RESTART_REQUIRED)
        expected_result = [mock_controller_classes[1].metadata.to_dict(always_include_defaults=True)]
        assert controllers_query_id == expected_result

    @patch('configparser.ConfigParser.__getitem__', return_value={'MetadataFileName': 'abc'})
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_load_custom_metadata_file_only(self, mapper_get_mapping_template_mock,
                                            mapper_get_class_mock, config_parser, test_utils):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_class = self.create_mock_controller_class("1234")
        mapper_get_class_mock.return_value = mock_controller_class
        ControllerMetadataInterface.custom_metadata_updated = False
        mock_file_read_data = """
        {
          "test_product": {
            "test_controller": {
              "metadata":{
                "new_metadata_key": "new_metadata_value",
                "new_complex_metadata": {
                  "child_new_metadata_key": "child_new_metadata_value"
                },
                "title": "This is my new overridden title"
              }
            }
          }
        }
        """
        with patch("builtins.open", test_utils.create_mock_file_open(read_data=mock_file_read_data)):
            assert mock_controller_class.metadata.to_dict(
                always_include_defaults=True) == self.expected_metadata_before_update
            ControllerMetadataInterface.load_custom_metadata_file()
            assert mock_controller_class.metadata.to_dict(
                always_include_defaults=True) == self.expected_metadata_after_update

    @patch('configparser.ConfigParser.__getitem__', return_value={'MetadataFileName': 'abc'})
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_load_custom_metadata_file_bad_product(self, mapper_get_mapping_template_mock,
                                                   mapper_get_class_mock, config_parser, test_utils):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_class = self.create_mock_controller_class("1234")
        mapper_get_class_mock.return_value = mock_controller_class
        ControllerMetadataInterface.custom_metadata_updated = False
        mock_file_read_data = """
        {
          "bad_product": {
            "test_controller": {
              "metadata":{
                "new_metadata_key": "new_metadata_value",
                "new_complex_metadata": {
                  "child_new_metadata_key": "child_new_metadata_value"
                },
                "title": "This is my new overridden title"
              }
            }
          }
        }
        """
        with patch("builtins.open", test_utils.create_mock_file_open(read_data=mock_file_read_data)):
            assert mock_controller_class.metadata.to_dict(
                always_include_defaults=True) == self.expected_metadata_before_update
            ControllerMetadataInterface.load_custom_metadata_file()
            assert mock_controller_class.metadata.to_dict(
                always_include_defaults=True) == self.expected_metadata_before_update

    @patch('configparser.ConfigParser.__getitem__', return_value={'MetadataFileName': 'abc'})
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_load_custom_metadata_file_bad_controller_name(self, mapper_get_mapping_template_mock,
                                                           mapper_get_class_mock, config_parser, test_utils):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_class = self.create_mock_controller_class("1234")
        mapper_get_class_mock.return_value = mock_controller_class
        ControllerMetadataInterface.custom_metadata_updated = False
        mock_file_read_data = """
        {
          "test_product": {
            "bad_controller_name": {
              "metadata":{
                "new_metadata_key": "new_metadata_value",
                "new_complex_metadata": {
                  "child_new_metadata_key": "child_new_metadata_value"
                },
                "title": "This is my new overridden title"
              }
            }
          }
        }
        """
        with patch("builtins.open", test_utils.create_mock_file_open(read_data=mock_file_read_data)):
            assert mock_controller_class.metadata.to_dict(
                always_include_defaults=True) == self.expected_metadata_before_update
            ControllerMetadataInterface.load_custom_metadata_file()
            assert mock_controller_class.metadata.to_dict(
                always_include_defaults=True) == self.expected_metadata_before_update

    @patch('configparser.ConfigParser.__getitem__', return_value={'MetadataFileName': 'abc'})
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_load_custom_metadata_file_no_metadata(self, mapper_get_mapping_template_mock,
                                                   mapper_get_class_mock, config_parser, test_utils):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mock_controller_class = self.create_mock_controller_class("1234")
        del mock_controller_class.metadata
        mapper_get_class_mock.return_value = mock_controller_class
        ControllerMetadataInterface.custom_metadata_updated = False
        mock_file_read_data = """
        {
          "test_product": {
            "test_controller": {
              "metadata":{
                "new_metadata_key": "new_metadata_value",
                "new_complex_metadata": {
                  "child_new_metadata_key": "child_new_metadata_value"
                },
                "title": "This is my new overridden title"
              }
            }
          }
        }
        """
        with patch("builtins.open", test_utils.create_mock_file_open(read_data=mock_file_read_data)):
            ControllerMetadataInterface.load_custom_metadata_file()

    @patch('configparser.ConfigParser.__getitem__', return_value={'MetadataFileName': 'abc'})
    @patch('config_modules_vmware.services.mapper.mapper_utils.get_class')
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_load_custom_metadata_file_get_class_error(self, mapper_get_mapping_template_mock,
                                                       mapper_get_class_mock, config_parser, test_utils):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        mapper_get_class_mock.side_effect = Exception("Could not load module.")
        ControllerMetadataInterface.custom_metadata_updated = False
        mock_file_read_data = """
        {
          "test_product": {
            "test_controller": {
              "metadata":{
                "new_metadata_key": "new_metadata_value",
                "new_complex_metadata": {
                  "child_new_metadata_key": "child_new_metadata_value"
                },
                "title": "This is my new overridden title"
              }
            }
          }
        }
        """
        with patch("builtins.open", test_utils.create_mock_file_open(read_data=mock_file_read_data)):
            ControllerMetadataInterface.load_custom_metadata_file()

    @patch('configparser.ConfigParser.__getitem__', return_value={'MetadataFileName': 'abc'})
    @patch('config_modules_vmware.services.mapper.mapper_utils'
           '.get_mapping_template')
    def test_load_custom_metadata_file_not_found(self, mapper_get_mapping_template_mock, config_parser, test_utils):
        mapper_get_mapping_template_mock.return_value = self.config_mapping_template
        ControllerMetadataInterface.custom_metadata_updated = False
        with patch("builtins.open",
                   test_utils.create_mock_file_open(filename="controller_metadata.json", raise_error=True)):
            ControllerMetadataInterface.load_custom_metadata_file()

    def test_validate_custom_metadata(self):
        custom_metadata = {
          "vcenter": {
            "backup_schedule_config": {
              "metadata": {
                "new_metadata_key": "new_metadata_value",
                "new_complex_metadata": {
                  "child_new_metadata_key": "child_new_metadata_value"
                },
                "title": "This is my new overridden title"
              }
            },
            "ntp": {
              "metadata": {
                "configuration_id": "123"
              }
            }
          },
          "sddc_manager": {
            "ntp": {
              "metadata": {
                "new_metadata_key": "new_metadata_value",
              }
            }
          }
        }
        ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_not_dict(self):
        custom_metadata = "string"
        with pytest.raises(TypeError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_invalid_product(self):
        custom_metadata = {
          "invalid_product": {
            "ntp": {
              "metadata": {
                "configuration_id": "123"
              }
            }
          }
        }
        with pytest.raises(ValueError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_invalid_product_value(self):
        custom_metadata = {
          "vcenter": "string"
        }
        with pytest.raises(TypeError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_invalid_control(self):
        custom_metadata = {
          "vcenter": {
            "invalid_control": {
              "metadata": {
                "new_metadata_key": "new_metadata_value"
              }
            }
          }
        }
        with pytest.raises(ValueError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_invalid_control_type(self):
        custom_metadata = {
          "vcenter": {
            "backup_schedule_config": "string"
          }
        }
        with pytest.raises(ValueError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_invalid_control_body(self):
        custom_metadata = {
          "vcenter": {
            "backup_schedule_config": {
              "no_metadata": {
                "new_metadata_key": "new_metadata_value"
              }
            }
          }
        }
        with pytest.raises(ValueError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_invalid_metadata_type(self):
        custom_metadata = {
          "vcenter": {
            "backup_schedule_config": {
              "metadata": "string"
            }
          }
        }
        with pytest.raises(TypeError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)

    def test_validate_custom_metadata_invalid_metadata_field_type(self):
        custom_metadata = {
          "vcenter": {
            "backup_schedule_config": {
              "metadata": {
                "new_metadata_key": "new_metadata_value",
                "title": 123
              }
            }
          }
        }
        with pytest.raises(TypeError):
            ControllerMetadataInterface.validate_custom_metadata(custom_metadata)
