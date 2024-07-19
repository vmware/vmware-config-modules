# Copyright 2024 Broadcom. All Rights Reserved.
import json
import logging
from typing import List

from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.clients.common.consts import COMPLIANCE_CONFIG
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.services.config import Config
from config_modules_vmware.services.mapper import mapper_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class ControllerMetadataInterface:
    """Class to implement config management functionalities for control config(s)."""

    custom_metadata_updated = False

    @staticmethod
    def query_by_id(desired_ids: List[str]):
        def query_function(metadata: ControllerMetadata):
            return metadata and metadata.configuration_id in desired_ids

        return query_function

    @staticmethod
    def query_by_tag(desired_tag: str):
        def query_function(metadata: ControllerMetadata):
            return metadata and desired_tag in metadata.tags

        return query_function

    @staticmethod
    def get_metadata_from_query(query_function):
        """Get a Controller's metadata based on input controller ID."""
        config_mapping = mapper_utils.get_mapping_template(mapper_utils.COMPLIANCE_MAPPING_FILE)
        ControllerMetadataInterface.load_custom_metadata_file(config_mapping=config_mapping)
        responses = []
        try:
            ControllerMetadataInterface._iterate_config_mapping(config_mapping, query_function, responses)
        except Exception as e:
            logger.error(f"Failure while retrieving metadata from controllers: {e}")
            return []

        return responses

    @staticmethod
    def _iterate_config_mapping(config_mapping_dict, function, responses):
        for _, value in config_mapping_dict.items():
            if isinstance(value, dict):
                ControllerMetadataInterface._iterate_config_mapping(value, function, responses)
            elif isinstance(value, str):
                controller_class = mapper_utils.get_class(value)
                if not controller_class or not hasattr(controller_class, "metadata"):
                    continue
                if function(controller_class.metadata):
                    responses.append(controller_class.metadata.to_dict(always_include_defaults=True))

    @classmethod
    def load_custom_metadata_file(cls, config_mapping=None):
        if not cls.custom_metadata_updated:
            if not config_mapping:
                config_mapping = mapper_utils.get_mapping_template(mapper_utils.COMPLIANCE_MAPPING_FILE)
            if COMPLIANCE_CONFIG in config_mapping:
                config_mapping = config_mapping[COMPLIANCE_CONFIG]
            custom_metadata_config = Config.get_section("metadata")
            metadata_filename = custom_metadata_config.get("MetadataFileName")
            if metadata_filename:
                try:
                    with open(metadata_filename, "r", encoding="UTF-8") as metadata_file:
                        custom_metadata_json = json.load(metadata_file)
                        # Parse the custom metadata file and load the metadata into the controllers
                        # Start by iterating over the products found in the custom metadata file
                        # Verify they are in the config_mapping.json
                        for product, controllers in custom_metadata_json.items():
                            if product not in config_mapping:
                                logger.error(
                                    f"Error parsing custom metadata file {metadata_filename}. "
                                    f'Product "{product}" is not found in control_config_mapping.json'
                                )
                                continue
                            # Loop over each controller within the product defined in the custom metadata file.
                            # Verify it is in the config_mapping.json under that product.
                            for controller_name, controller_metadata in controllers.items():
                                if controller_name not in config_mapping[product]:
                                    logger.error(
                                        f"Error parsing custom metadata file {metadata_filename}. "
                                        f'Controller "{controller_name}" is not found in control_config_mapping.json'
                                    )
                                    continue
                                controller_class_file = config_mapping[product][controller_name]
                                # Try to load that controller class
                                try:
                                    controller_class = mapper_utils.get_class(controller_class_file)
                                except Exception as e:
                                    logger.error(
                                        f"There was an error when loading class [{controller_class_file}]. [{e}]"
                                    )
                                    continue
                                if not controller_class or not hasattr(controller_class, "metadata"):
                                    logger.error(
                                        f"Error parsing custom metadata file {metadata_filename}."
                                        f' Controller class in "{controller_class_file}" '
                                        f'does not have a "metadata" class attribute'
                                    )
                                    continue
                                # Set the "custom_metadata" attribute in the controller's metadata
                                # to the dict found in the custom metadata file.
                                controller_class.metadata.custom_metadata = controller_metadata.get("metadata", {})
                except FileNotFoundError:
                    logger.error(f"Custom Metadata file {metadata_filename} does not exist or cannot be accessed.")
            cls.custom_metadata_updated = True

    @staticmethod
    def validate_custom_metadata(custom_metadata: dict):
        """
        Validate custom metadata is valid - has correct product/controls, format, and types
        :param custom_metadata: The custom metadata
        :type custom_metadata: dict
        :raises: TypeError or ValueError if invalid
        """
        if not isinstance(custom_metadata, dict):
            raise TypeError("Custom metadata is not a dict")

        config_mapping = mapper_utils.get_mapping_template(mapper_utils.COMPLIANCE_MAPPING_FILE)
        config_mapping = config_mapping.get(consts.COMPLIANCE_CONFIG)

        for product, controls in custom_metadata.items():
            if product not in config_mapping:
                raise ValueError(f"Invalid product: {product}")
            if not isinstance(controls, dict):
                raise TypeError(f"Value of '{product}' should be a dict")

            for control_name, control_body in controls.items():
                if control_name not in config_mapping.get(product):
                    raise ValueError(f"Invalid control: product - {product}, control - {control_name}")
                if not isinstance(control_body, dict) or consts.METADATA not in control_body:
                    raise ValueError(
                        f"Product - {product}, control - {control_name} should contain '{consts.METADATA}'"
                    )

                metadata = control_body.get(consts.METADATA)
                if not isinstance(metadata, dict):
                    raise TypeError(f"Metadata for product - {product}, control - {control_name} should be a dict")
                for metadata_field, metadata_type in ControllerMetadata.ControllerMetadataTypes.items():
                    if metadata_field in metadata and not isinstance(metadata.get(metadata_field), metadata_type):
                        raise TypeError(
                            f"Metadata '{metadata_field}' for product - {product}, control - {control_name} should be of type '{metadata_type}'"
                        )
