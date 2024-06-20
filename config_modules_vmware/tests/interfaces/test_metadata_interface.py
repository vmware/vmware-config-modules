# Copyright 2024 Broadcom. All Rights Reserved.
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
                spec={"test_key": str},  # schema of the output of the controller
            )

        return MockController

    def setup_method(self):
        self.config_mapping_template = \
            {
                "test_section": {
                    "test_controller": {
                        "vcenter": "path_to_class"
                    },
                    "test_controller_two": {
                        "vcenter": "path_to_class"
                    }
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
        expected_result = [mock_controller_classes[0].metadata.to_dict()]
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
        expected_result = [mock_controller_class.metadata.to_dict() for mock_controller_class in
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
        expected_result = [mock_controller_classes[0].metadata.to_dict()]
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
        expected_result = [mock_controller_classes[0].metadata.to_dict()]
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
        expected_result = [mock_controller_class.metadata.to_dict() for mock_controller_class in
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
        expected_result = [mock_controller_classes[1].metadata.to_dict()]
        assert controllers_query_id == expected_result
