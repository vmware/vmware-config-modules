import importlib
import logging
import os

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.utils import utils

COMPLIANCE_MAPPING_FILE = "control_config_mapping.json"
CONFIGURATION_MAPPING_FILE = "configuration_mapping.json"

logger = LoggerAdapter(logging.getLogger(__name__))


def get_mapping_template(file: str) -> dict:
    """
    Returns the config mapping json file.
    :param file: The mapping file to load
    :type file: str
    :return: the config mapping json file in python object format.
    :rtype: dict
    """
    config_mapping_file_path = os.path.join(os.path.dirname(__file__), file)
    return utils.read_json_file(config_mapping_file_path)


def get_class(module_path):
    try:
        partition = module_path.rpartition(".")
        module_str = partition[0]
        class_str = partition[2]
        module = importlib.import_module(module_str)
        return getattr(module, class_str)
    except Exception as e:
        logger.error(f"Could not load module from path {module_path}. {e}")
        raise Exception(f"Could not load module from path {module_path}. {e}") from e
