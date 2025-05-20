# Copyright 2025 Broadcom. All Rights Reserved.
import logging
import re
from typing import List

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


def name_pattern_match(name: str, name_match_patterns: List) -> bool:
    """
    Check if a given name matches any name/pattern in input list.

    :param name: name.
    :type name: str
    :param name_match_patterns: a list of names/patterns to compare.
    :type name_match_patterns: List
    :return: True if name matches any name or pattern in name_match_pattern list
    :rtype: bool
    """
    for name_or_pattern in name_match_patterns:
        if re.match(name_or_pattern, name, re.IGNORECASE):
            logger.debug(f"name: {name} -match-: {name_or_pattern}")
            return True
    return False


def filter_member_configs(all_member_configs: List, exclude_patterns: List) -> List:
    """
    Remove member configs in user exclude list.

    :param all_member_configs: all bash shell authorized members configs.
    :type all_member_configs: List
    :param exclude_patterns: user input exclude name/patterns.
    :type exclude_patterns: List
    :return: a list of configs to compare with desired input.
    :rtype: List
    """
    filtered_member_configs = []
    for member_config in all_member_configs:
        name = member_config["name"]
        # check if name matches the name in exclude list
        if name_pattern_match(name, exclude_patterns):
            logger.debug(f"Exclude this user - {member_config}")
            continue
        filtered_member_configs.append(member_config)

    logger.debug(f"Filtered member configs: {filtered_member_configs}")
    return filtered_member_configs
