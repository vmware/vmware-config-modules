# Copyright 2024 Broadcom. All Rights Reserved.
import logging
from enum import Enum

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.schemas import schema_utility
from config_modules_vmware.services.config import Config

logger = LoggerAdapter(logging.getLogger(__name__))


class ControllerMetadata:
    """
    | Every Controller is expected to have metadata. There is a set of REQUIRED_METADATA defined below.
    """

    class RemediationImpact(str, Enum):
        """
        Enum Class to define remediation impacts.
        """

        RESTART_REQUIRED = "RESTART_REQUIRED"
        REMEDIATION_SKIPPED = "REMEDIATION_SKIPPED"

    class ControllerStatus(str, Enum):
        """
        Enum Class to define controller status.
        If a controller's status is disabled, any operation for that controller will be skipped.
        """

        ENABLED = "ENABLED"
        DISABLED = "DISABLED"

    class ControllerType(str, Enum):
        """
        Enum Class to define controller type.
        """

        COMPLIANCE = "COMPLIANCE"
        CONFIGURATION = "CONFIGURATION"

    REQUIRED_METADATA = ["name", "configuration_id", "path_in_schema", "title", "version", "products", "status"]
    EXCLUDED_METADATA_FROM_DICT = ["_spec", "_custom_metadata"]
    ControllerMetadataTypes = {
        "name": str,
        "configuration_id": str,
        "path_in_schema": str,
        "title": str,
        "tags": list,
        "version": str,
        "since": str,
        "products": list,
        "components": list,
        "status": ControllerStatus,
        "impact": RemediationImpact,
        "scope": str,
        "type": ControllerType,
        "spec": dict,
        "functional_test_targets": list,
        "custom_metadata": dict,
    }

    def __init__(self, **kwargs):
        """Initialize a new Metadata instance."""
        self._name = kwargs.get("name")
        self._configuration_id = kwargs.get("configuration_id")
        self._path_in_schema = kwargs.get("path_in_schema")
        self._title = kwargs.get("title")
        self._tags = kwargs.get("tags", [])
        self._version = kwargs.get("version")
        self._since = kwargs.get("since")
        self._products = kwargs.get("products", [])
        self._components = kwargs.get("components", [])
        self._status = kwargs.get("status")
        self._impact = kwargs.get("impact")
        self._scope = kwargs.get("scope")
        self._type = kwargs.get("type", ControllerMetadata.ControllerType.COMPLIANCE)
        self._functional_test_targets = kwargs.get("functional_test_targets", [])
        self._custom_metadata = {}

        self._spec = self._get_spec_from_schema()

    @property
    def name(self):
        """The controller's name."""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def configuration_id(self):
        """The controller's id as defined in the compliance kit."""
        return self._configuration_id

    @configuration_id.setter
    def configuration_id(self, configuration_id: str):
        self._configuration_id = configuration_id

    @property
    def path_in_schema(self):
        """The path in the schema to this controller."""
        return self._path_in_schema

    @path_in_schema.setter
    def path_in_schema(self, path_in_schema: str):
        self._path_in_schema = path_in_schema

    @property
    def title(self):
        """The controller's title as defined in the compliance kit."""
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def tags(self):
        """The controller's tags."""
        return self._tags

    @tags.setter
    def tags(self, tags: list):
        self._tags = tags

    @property
    def version(self):
        """The controller's version."""
        return self._version

    @version.setter
    def version(self, version: str):
        self._version = version

    @property
    def since(self):
        """The version when the controller was first introduced into the compliance kit."""
        return self._since

    @since.setter
    def since(self, since: str):
        self._since = since

    @property
    def products(self):
        """The products the controller is associated with."""
        return self._products

    @products.setter
    def products(self, products: list):
        self._products = products

    @property
    def components(self):
        """The components within a product the controller is associated with."""
        return self._components

    @components.setter
    def components(self, components: list):
        self._components = components

    @property
    def status(self):
        """
        The controller's status (ENABLED/DISABLED).
        If DISABLED, all operations for this controller will be skipped.
        """
        return self._status

    @status.setter
    def status(self, status: ControllerStatus):
        self._status = status

    @property
    def impact(self):
        """The impact on the product/component of performing remediation."""
        return self._impact

    @impact.setter
    def impact(self, impact: RemediationImpact):
        self._impact = impact

    @property
    def scope(self):
        """
        Any relevant information or limitations regarding how the controller is run.
        i.e. must be run on the VC appliance.
        """
        return self._scope

    @scope.setter
    def scope(self, scope: str):
        self._scope = scope

    @property
    def type(self):
        """The type of controller"""
        return self._type

    @type.setter
    def type(self, controller_type: str):
        self._type = controller_type

    @property
    def functional_test_targets(self):
        """
        Any relevant information or limitations regarind how the controller is run.
        i.e. must be run on the VC appliance.
        """
        return self._functional_test_targets

    @functional_test_targets.setter
    def functional_test_targets(self, functional_test_targets: list):
        self._functional_test_targets = functional_test_targets

    @property
    def spec(self):
        """The schema expected of the controller's current or desired state."""
        return self._spec

    @spec.setter
    def spec(self, spec: str):
        self._spec = spec

    @property
    def custom_metadata(self):
        """Any custom metadata provided by user to add or override defaults."""
        return self._custom_metadata

    @custom_metadata.setter
    def custom_metadata(self, custom_metadata: dict):
        self._custom_metadata = custom_metadata

    def _get_spec_from_schema(self):
        if self.type == ControllerMetadata.ControllerType.CONFIGURATION:
            compliance_schema = {}
        else:
            try:
                compliance_schema = schema_utility.retrieve_reference_schema("compliance")
                if not self.path_in_schema:
                    compliance_schema = {}
                else:
                    keys = self.path_in_schema.split(".")
                    for key in keys:
                        compliance_schema = compliance_schema["properties"][key]
                    compliance_schema = compliance_schema["properties"]["value"]
            except KeyError as e:
                if self.path_in_schema != "compliance_config.sample_product.sample_controller_name":
                    logger.error(
                        f"Path in schema [{self.path_in_schema}]is not valid in the compliance schema. "
                        f"Invalid key: [{e}]"
                    )
                compliance_schema = {}
        return compliance_schema

    def validate(self):
        if self.status == ControllerMetadata.ControllerStatus.DISABLED:
            return True
        for property_, type_ in self.ControllerMetadataTypes.items():
            if getattr(self, property_, None) is None:
                if property_ in self.REQUIRED_METADATA:
                    return False
            else:
                if not isinstance(getattr(self, property_), type_):
                    return False
        return True

    def to_dict(self, always_include_defaults=False):
        """

        :param always_include_defaults: Whether to include the built in attributes or only the custom ones.
        If this is false, it will get the value from the config.ini.
        It is mostly used for generating documentation.
        :type always_include_defaults: bool
        :return: Dictionary of the metadata attributes.
        """
        if not always_include_defaults:
            custom_metadata_config = Config.get_section("metadata")
            custom_metadata_only = custom_metadata_config.getboolean("IncludeOnlyCustomMetadata")
            if custom_metadata_only:
                return self._custom_metadata
        response_dict = {}
        for key, value in vars(self).items():
            if key.startswith("_"):
                if key not in self.EXCLUDED_METADATA_FROM_DICT:
                    response_dict[key[1:]] = value
        response_dict.update(self._custom_metadata)
        return response_dict
