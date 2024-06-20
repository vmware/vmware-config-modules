# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.services.mapper import mapper_utils

logger = LoggerAdapter(logging.getLogger(__name__))


class ControllerMetadataInterface:
    """Class to implement config management functionalities for control config(s)."""

    @staticmethod
    def query_by_id(desired_ids):
        if isinstance(desired_ids, str):
            desired_ids = [desired_ids]

        def query_function(metadata: ControllerMetadata):
            return metadata and metadata.configuration_id in desired_ids

        return query_function

    @staticmethod
    def query_by_tag(desired_tag):
        def query_function(metadata: ControllerMetadata):
            return metadata and desired_tag in metadata.tags

        return query_function

    @staticmethod
    def get_metadata_from_query(query_function):
        """Get a Controller's metadata based on input controller ID."""
        config_mapping = mapper_utils.get_mapping_template(mapper_utils.COMPLIANCE_MAPPING_FILE)

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
                    responses.append(controller_class.metadata.to_dict())
