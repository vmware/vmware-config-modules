# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re

from config_modules_vmware.framework.logging.logging_context import LoggingContext
from config_modules_vmware.services.config import Config


class LoggerAdapter(logging.LoggerAdapter):
    """
    LoggerAdapter that formats log messages with values from LoggingContext.
    """

    def __init__(self, logger, extra=None):
        super().__init__(logger, extra)
        self.format = Config.get_section("logging.adapter")["Format"]
        self.regex = re.compile("\\w+= ")

    def process(self, msg, kwargs):
        if not self.format:
            return super().process(msg, kwargs)

        metadata = LoggingContext.get_controller_metadata_context()
        hostname = LoggingContext.get_hostname_context()
        attributes = {
            "controller_name": metadata.name if metadata else "",
            "configuration_id": metadata.configuration_id if metadata else "",
            "path_in_schema": metadata.path_in_schema if metadata else "",
            "title": metadata.title if metadata else "",
            "tags": metadata.tags if metadata else "",
            "version": metadata.version if metadata else "",
            "since": metadata.since if metadata else "",
            "products": self._get_products(metadata),
            "components": metadata.components if metadata else "",
            "status": metadata.status.value if metadata and metadata.status else "",
            "impact": metadata.impact.value if metadata and metadata.impact else "",
            "scope": metadata.scope if metadata else "",
            "type": metadata.type.value if metadata and metadata.type else "",
            "hostname": hostname if hostname else "",
            "msg": msg,
        }
        formatted_msg = self.format.format_map(attributes)
        # Remove empty key values i.e. "controller= "
        formatted_msg = self.regex.sub("", formatted_msg)
        return formatted_msg, kwargs

    def _get_products(self, metadata):
        if metadata:
            if len(metadata.products) == 1:
                return metadata.products[0].value
            elif len(metadata.products) > 1:
                return [product.value for product in metadata.products]
        return ""
