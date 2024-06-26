# Copyright 2024 Broadcom. All Rights Reserved.
import copy
import numbers
from enum import Enum
from typing import Any
from typing import List
from typing import Tuple


class ComparatorOptionForList(Enum):
    """Enum defining options for comparing list data.
    COMPARE_AFTER_SORT: List will be sortd before comparison, so [1,2] == [2,1].
    COMPARE_WITHOUT_SORT: List will not be sorted before comparison, so [1,2] != [2,1].
    IDENTIFIER_BASED_COMPARISON: List is dicts with each element have an instance key.
    Compares each object based on keys and reports mismatch or missing dict objects.
    Default is set to COMPARE_AFTER_SORT.
    """

    COMPARE_AFTER_SORT = 0
    COMPARE_WITHOUT_SORT = 1
    IDENTIFIER_BASED_COMPARISON = 2

    @classmethod
    def _missing_(cls, value):
        return cls.COMPARE_AFTER_SORT


class Comparator:
    """Class with utils methods for comparing two sets of configuration data based on comparator options."""

    @staticmethod
    def _sort_recursive(obj: Any) -> Any:
        """Sort recursively within the data structure."""
        if isinstance(obj, list):
            return sorted(Comparator._sort_recursive(item) for item in obj)
        elif isinstance(obj, dict):
            return sorted((key, Comparator._sort_recursive(value)) for key, value in obj.items())
        else:
            return obj

    @staticmethod
    def _sort_list_by_instance_id(list_: List[dict], instance_key: str = "name") -> List[dict]:
        """Sort the list based on the instance_key.
        :param list_: List of dicts elements
        :type: list_: list[dict]
        :param instance_key: instance id of the object:
        :type instance_key: str
        :returns: List of dicts sorted based on the instance id.
        :rtype: list[dict]
        :raises: ValueError exception if instance_key is missing for any dict element in list_.

        """
        if not all(instance_key in x for x in list_):
            raise ValueError(f"Instance key '{instance_key} is not present in all dict elements.")
        return sorted(list_, key=lambda x: x[instance_key] if instance_key in x else None)

    @staticmethod
    def _compare_list_with_instance_key(
        list_1: List[dict], list_2: List[dict], instance_key: str
    ) -> Tuple[List[dict], List[dict]]:
        """Compare two list of dicts object with object having an instance id/key.

        :param list_1: Current list of dictionary object with instance key.
        :type list_1: list[dict]
        :param list_2: Desired list of dictionary objects with instance key.
        :type list_2: list[dict]
        :param instance_key: Instance id of the object.
        :type instance_key: str
        :return: Return tuple of lists of non_matching elements, missing or extra elements between them.
        :rtype: Tuple[List[dict], List[dict]]
        :raises: ValueError exception if instance_key is missing for any dict element in list_1 or list_2.
        """

        list_1 = Comparator._sort_list_by_instance_id(list_1, instance_key)
        list_2 = Comparator._sort_list_by_instance_id(list_2, instance_key)

        result_list_1 = []
        result_list_2 = []

        iter_1, iter_2 = iter(list_1), iter(list_2)
        dict_1, dict_2 = next(iter_1, None), next(iter_2, None)

        while dict_1 is not None or dict_2 is not None:
            if dict_1 == dict_2:
                dict_1, dict_2 = next(iter_1, None), next(iter_2, None)
            elif dict_1 is not None and (dict_2 is None or dict_1[instance_key] < dict_2[instance_key]):
                result_list_1.append(dict_1)
                result_list_2.append(None)
                dict_1 = next(iter_1, None)
            elif dict_2 is not None and (dict_1 is None or dict_1[instance_key] > dict_2[instance_key]):
                result_list_1.append(None)
                result_list_2.append(dict_2)
                dict_2 = next(iter_2, None)
            else:
                non_matching_data_1, non_matching_data_2 = Comparator.get_non_compliant_configs(
                    dict_1, dict_2, ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON, instance_key
                )
                if non_matching_data_1 and non_matching_data_2:
                    result_list_1.append(non_matching_data_1)
                    result_list_2.append(non_matching_data_2)
                dict_1, dict_2 = next(iter_1, None), next(iter_2, None)

        return result_list_1, result_list_2

    @staticmethod
    def is_data_same_type(data_1: Any, data_2: Any) -> bool:
        """Compare data type and return true if the data type is same or if the data are numbers.
        :param data_1: First data to compare.
        :type: data_1: Any
        :param data_2: Second data to compare.
        :type data_2: Any
        :returns: True if same data type or of type numbers.
        :rtype: bool
        """
        # If both data are numbers type return True.In the compliance reference schema
        # there are properties with type numbers, so long(180) and int(180) should be considered same.
        # Also, boolean should not be considered as number. Check boolean data type first.
        if isinstance(data_1, bool) != isinstance(data_2, bool):
            return False
        if isinstance(data_1, numbers.Number) and isinstance(data_2, numbers.Number):
            return True
        return type(data_1) == type(data_2)

    @staticmethod
    def get_non_compliant_configs(
        current_config: Any,
        desired_config: Any,
        comparator_option=ComparatorOptionForList.COMPARE_AFTER_SORT,
        instance_key="name",
    ) -> Tuple[Any, Any]:
        """Compare current config and desired config and return non_compliant configs only.
        Notes for the caller for this method.
        1. Supported structures for the config data: dict, str, int, float, bool, list[str], list[int],
        list[dict(no instance key)], list[dict(with instance key)], list[float], list[bool].

        Nested list[dicts] like list[dicts(with instance key){ list[ dicts (with instance key]}} is not supported.
        complex {dict, list[dict (with instance key]}.
        Mixed_list is not supported. like [1,"two", True]

        2. For IDENTIFIER_BASED_COMPARISON comparison, current support is only for top level list of dicts only.
        Also, each element must have the instance key.
        Sample input:
        .. code-block:: json
            current_config = [
                {'instance_key': "ssh", 'key2': 'test', 'key3': {'key3_1': 'abc', 'key3_2': [100, 200]}},
                {'instance_key': "dns", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
                {'instance_key': "ntp", 'key2': 'test', 'key3': {'key3_1': 'xyz', 'key3_2': [100, 200]}}]

            desired_config = [
                {'instance_key': "nfs", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
                {'instance_key': "ssh", 'key2': 'test', 'key3': {'key3_1': 'abc', 'key3_2': [100, 200]}},
                {'instance_key': "ntp", 'key2': 'test', 'key3': {'key3_1': 'xyz', 'key3_2': [200, 300]}}]

        Sample response:
        .. code-block:: json
            current_non_compliant_configs = [
                {'instance_key': "dns", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
                None,
                {'instance_key': "ntp", 'key3': {'key3_2': [100, 200]}},
            ]
            desired_non_compliant_configs = [
                None,
                {'instance_key': "nfs", 'key2': 'test', 'key3': { 'key3_1': 'pqr', 'key3_2': [100, 200]}},
                {'instance_key': "ntp", 'key3': {'key3_2': [200, 300]}},
            ]

        3. Default for all List (nested as well) is SORT the list and compare.
        4. For regular dicts it does check recursively and returns only the keys which are non_compliant.

        Sample input:
        .. code-block:: json
            current_config = {
                'key1': 1,
                'key2': [1, 2, 3],
                'key3': {
                    'key3_1': 'abc',
                    'key3_2': {
                        'key3_2_1': [500, 700],
                        'key3_2_2': 10
                    },
                    'key3_3': []
                },
                'key4': True,
                'key5': "missing in data_2"
            }

            desired_config = {
                'key1': 1,
                'key2': [1, 2],
                'key3': {
                    'key3_1': 'abc',
                    'key3_2': {
                        'key3_2_1': [700, 500],
                        'key3_2_2': 20
                    },
                    'key3_3': None
                },
                'key4': True,
                'key6': "missing in data_1"
            }

        Sample Response:
        .. code-block:: json
            current_non_compliant_configs = {
                'key2': [1, 2, 3],
                'key3': {
                    'key3_2': {
                        'key3_2_2': 10
                    },
                    'key3_3': []
                },
                'key5': "missing in data_2",
                'key6': None
            }
            'desired_non_compliant_configs': {
                'key2': [1, 2],
                'key3': {
                    'key3_2': {
                        'key3_2_2': 20
                    },
                    'key3_3': None
                },
                'key5': None,
                'key6': "missing in data_1"
            }

        :param current_config: Current config data structure.
        :type current_config: Any
        :param desired_config: Desired config data structure.
        :type desired_config: Any
        :param comparator_option: Enum for comparator option for list comparisons.
        :type comparator_option: ComparatorOptionForList
        :param instance_key: Optional instance_key needed for ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON
        :return: Return tuple of non_matching data as non_matching_data_1, non_matching_data_2
        :rtype: Tuple[Any, Any]
        """

        # If data type of current and desired config is not same(for numbers ignore data type), return them.
        if not Comparator.is_data_same_type(current_config, desired_config):
            return current_config, desired_config

        # If the current and desired config is of dict type, recursively call and create "current" and "desired"
        # for non_compliant configs.
        elif isinstance(current_config, dict):
            # Empty dicts are considered same, return None, None
            if not current_config and not desired_config:
                return None, None

            # Handle other dicts
            current_non_compliant_configs = {}
            desired_non_compliant_configs = {}
            for key in set(current_config.keys()).union(set(desired_config.keys())):
                if key in current_config and key in desired_config:
                    # For identifier based comparison, insert the key-value for instance_key and continue.
                    if key == instance_key and comparator_option == ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON:
                        current_non_compliant_configs.setdefault(key, current_config.get(key, None))
                        desired_non_compliant_configs.setdefault(key, desired_config.get(key, None))
                        continue

                    # For nested level, currently do not support for IDENTIFIER_BASED_COMPARISON.
                    # set it to COMPARE_AFTER_SORT
                    if comparator_option == ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON:
                        cmp_option = ComparatorOptionForList.COMPARE_AFTER_SORT
                    else:
                        cmp_option = comparator_option

                    # If the key is present in both current and desired, recursively call get_non_compliant_configs.
                    nested_diff_current, nested_diff_desired = Comparator.get_non_compliant_configs(
                        current_config[key], desired_config[key], cmp_option, instance_key
                    )

                    if (
                        not Comparator.is_data_same_type(nested_diff_current, nested_diff_desired)
                        or nested_diff_current
                        or nested_diff_desired
                    ):
                        # If either of current or desired is not None or not-empty, insert the key-value in
                        # both current and desired.
                        current_non_compliant_configs.setdefault(key, nested_diff_current)
                        desired_non_compliant_configs.setdefault(key, nested_diff_desired)
                else:
                    # Handle mismatch keys, set the value to None where key is not present.
                    current_non_compliant_configs.setdefault(key, current_config.get(key, None))
                    desired_non_compliant_configs.setdefault(key, desired_config.get(key, None))

        else:
            # If the data is list of dict objects and identified based comparison is required,
            # return with call to compare_list_with_instance_key.
            if isinstance(current_config, list):
                if (
                    all(isinstance(d, dict) for d in current_config)
                    and all(isinstance(d, dict) for d in desired_config)
                    and comparator_option == ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON
                ):
                    return Comparator._compare_list_with_instance_key(current_config, desired_config, instance_key)

            # For all other cases, based on compare_option either sort or not sort the data and compare.
            # Only when COMPARE_WITHOUT_SORT is set, do not sort the list.
            if comparator_option == ComparatorOptionForList.COMPARE_WITHOUT_SORT:
                data_1 = current_config
                data_2 = desired_config
            else:
                # Sort the data.
                data_1 = copy.deepcopy(current_config)
                data_2 = copy.deepcopy(desired_config)
                data_1 = Comparator._sort_recursive(data_1)
                data_2 = Comparator._sort_recursive(data_2)

            current_non_compliant_configs, desired_non_compliant_configs = None, None
            # If the data not equal and either current_config or desired_config is not None.
            if (data_1 != data_2) and (current_config or desired_config):
                current_non_compliant_configs = current_config
                desired_non_compliant_configs = desired_config

        return current_non_compliant_configs, desired_non_compliant_configs
