# Copyright 2024 Broadcom. All Rights Reserved.
import configparser
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class Config:
    """
    Class holding the config modules configuration.
    """

    _conf = None

    @classmethod
    def get_overrides_path(cls):
        """
        Get path containing any override files
        :return: The overrides path is set, None otherwise
        :rtype: str
        """
        return os.environ.get("OVERRIDES_PATH")

    @classmethod
    def _setup_config(cls):
        """
        Setup configuration through INI files.
        :return: The loaded configuration
        :rtype: configparser.ConfigParser
        """
        conf = configparser.ConfigParser(allow_no_value=True)

        default_config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        with open(default_config_path, "r", encoding="utf-8") as f:
            conf.read_file(f)
        logger.info(f"Loaded default config from {default_config_path}")

        overrides_path = cls.get_overrides_path()
        if overrides_path:
            overrides_config_path = os.path.join(overrides_path, "config-overrides.ini")
            files_read = conf.read(overrides_config_path, encoding="utf-8")
            if files_read:
                logger.info(f"Loaded config overrides from {files_read}")

        for section in conf.sections():
            logger.info(f"Section: {section} - {conf.items(section)}")

        return conf

    @classmethod
    def get_section(cls, section: str) -> Any:
        """
        Get a section of config-modules configuration.
        :param section: The section of the configuration to retrieve
        :type section: str
        :return: The configuration section
        :rtype: configparser.ConfigParser section
        """
        if cls._conf is None:
            cls._conf = cls._setup_config()
        return cls._conf[section]  # pylint: disable=unsubscriptable-object
