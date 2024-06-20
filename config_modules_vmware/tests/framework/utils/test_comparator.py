# Copyright 2024 Broadcom. All Rights Reserved.
from config_modules_vmware.framework.utils.comparator import Comparator
from config_modules_vmware.framework.utils.comparator import ComparatorOptionForList


def test_comparator_option_missing_value_returns_default():
    default_value = ComparatorOptionForList.COMPARE_AFTER_SORT
    option = 'invalid_value'
    result = ComparatorOptionForList(option)
    assert result == default_value


def test_get_non_compliant_configs_equal():
    data_1 = {'key1': 1, 'key2': [1, 2], 'key3': {'key3_1': 'abc', 'key_3_2': {'key3_2_1': [500], 'key_3_2_3': 200}}}
    data_2 = {'key1': 1, 'key2': [1, 2], 'key3': {'key3_1': 'abc', 'key_3_2': {'key3_2_1': [500], 'key_3_2_3': 200}}}
    current, desired = Comparator.get_non_compliant_configs(data_1, data_2)
    assert current == {}
    assert desired == {}


def test_get_non_compliant_configs_not_equal():
    data_1 = {
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

    data_2 = {
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

    expected_result = {
        'current': {
            'key2': [1, 2, 3],
            'key3': {
                'key3_2': {
                    'key3_2_2': 10
                },
                'key3_3': []
            },
            'key5': "missing in data_2",
            'key6': None
        },
        'desired': {
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
    }
    current, desired = Comparator.get_non_compliant_configs(data_1, data_2)
    assert {'current': current, 'desired': desired} == expected_result


def test_get_non_compliant_configs_bool():
    data_1 = True
    data_2 = False
    current, desired = Comparator.get_non_compliant_configs(data_1, data_2)
    assert current is True
    assert desired is False


def test_get_non_compliant_configs_key_missing_in_current_config():
    data_1 = {'key1': 1,  'key2': '123'}
    data_2 = {'key1': 1}
    expected_result = {
        'current': {'key2': '123'},
        'desired': {'key2': None}
    }
    current, desired = Comparator.get_non_compliant_configs(data_1, data_2)
    assert current == expected_result.get('current')
    assert desired == expected_result.get('desired')


def test_get_non_compliant_configs_key_missing_in_desired_config():
    data_1 = {'key1': 1}
    data_2 = {'key1': 1, 'key2': '123'}
    expected_result = {
        'current': {'key2': None},
        'desired': {'key2': '123'}
    }
    current, desired = Comparator.get_non_compliant_configs(data_1, data_2)
    assert current == expected_result.get('current')
    assert desired == expected_result.get('desired')


def test_get_non_compliant_configs_with_list_sort_true():
    data_1 = [1, 2]
    data_2 = [2, 1]
    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.COMPARE_AFTER_SORT)
    assert current is None
    assert desired is None


def test_get_non_compliant_configs_with_list_sort_false():
    data_1 = [1, 2]
    data_2 = [2, 1]
    expected_result = {'current': [1, 2], 'desired': [2, 1]}
    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.COMPARE_WITHOUT_SORT)
    assert current == expected_result.get('current')
    assert desired == expected_result.get('desired')


def test_get_non_compliant_configs_for_list_of_dicts_sort_true():
    data_1 = [{'port': 90, 'ip': '10.10.10.10'}, {'port': 80, 'ip': '10.10.10.20'}]
    data_2 = [{'port': 80, 'ip': '10.10.10.20'}, {'port': 90, 'ip': '10.10.10.10'}]
    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.COMPARE_AFTER_SORT)
    assert current is None
    assert desired is None


def test_get_non_compliant_configs_for_list_of_dicts_sort_false():
    data_1 = [{'port': 90, 'ip': '10.10.10.10'}, {'port': 80, 'ip': '10.10.10.20'}]
    data_2 = [{'port': 80, 'ip': '10.10.10.20'}, {'port': 90, 'ip': '10.10.10.10'}]
    expected_result = {'current': [{'port': 90, 'ip': '10.10.10.10'}, {'port': 80, 'ip': '10.10.10.20'}],
                       'desired': [{'port': 80, 'ip': '10.10.10.20'}, {'port': 90, 'ip': '10.10.10.10'}]}
    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.COMPARE_WITHOUT_SORT)
    assert current == expected_result.get('current')
    assert desired == expected_result.get('desired')


def test_get_non_compliant_configs_with_mismatched_list():
    data_1 = [1, 2]
    data_2 = [1, 2, 3]
    expected_result = {'current': [1, 2], 'desired': [1, 2, 3]}
    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.COMPARE_AFTER_SORT)
    assert current == expected_result.get('current')
    assert desired == expected_result.get('desired')
    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.COMPARE_WITHOUT_SORT)
    assert current == expected_result.get('current')
    assert desired == expected_result.get('desired')


def test_get_non_compliant_configs_list_with_instance_key():
    data_1 = [
        {'instance_key': "ssh", 'key2': 'test', 'key3': {'key3_1': 'abc', 'key3_2': [100, 200]}},
        {'instance_key': "dns", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
        {'instance_key': "ntp", 'key2': 'test', 'key3': {'key3_1': 'xyz', 'key3_2': [100, 200]}}]

    data_2 = [
        {'instance_key': "nfs", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
        {'instance_key': "ssh", 'key2': 'test', 'key3': {'key3_1': 'abc', 'key3_2': [100, 200]}},
        {'instance_key': "ntp", 'key2': 'test', 'key3': {'key3_1': 'xyz', 'key3_2': [200, 300]}, 'key_4': 'extra'}]

    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON,
        instance_key='instance_key')

    expected_current = [
        {'instance_key': "dns", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
        None,
        {'instance_key': "ntp", 'key3': {'key3_2': [100, 200]}, 'key_4': None},
    ]
    expected_desired = [
        None,
        {'instance_key': "nfs", 'key2': 'test', 'key3': { 'key3_1': 'pqr', 'key3_2': [100, 200]}},
        {'instance_key': "ntp", 'key3': {'key3_2': [200, 300]}, 'key_4': 'extra'},
    ]
    assert current == expected_current
    assert desired == expected_desired


def test_get_non_compliant_configs_list_with_instance_key_all_equal():
    data_1 = [
        {'instance_key': "nfs", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
        {'instance_key': "ssh", 'key2': 'test', 'key3': {'key3_1': 'abc', 'key3_2': [100, 200]}},
        {'instance_key': "ntp", 'key2': 'test', 'key3': {'key3_1': 'xyz', 'key3_2': [200, 300]}, 'key_4': 'extra'}]

    data_2 = [
        {'instance_key': "nfs", 'key2': 'test', 'key3': {'key3_1': 'pqr', 'key3_2': [100, 200]}},
        {'instance_key': "ssh", 'key2': 'test', 'key3': {'key3_1': 'abc', 'key3_2': [100, 200]}},
        {'instance_key': "ntp", 'key2': 'test', 'key3': {'key3_1': 'xyz', 'key3_2': [200, 300]}, 'key_4': 'extra'}]

    current, desired = Comparator.get_non_compliant_configs(
        data_1, data_2, comparator_option=ComparatorOptionForList.IDENTIFIER_BASED_COMPARISON,
        instance_key='instance_key')

    assert current == []
    assert desired == []


def test_get_non_compliant_configs_different_types():
    data_1 = [1, 2]
    data_2 = "test"
    data_3 = {'key1': 1}
    data_4 = 10
    current, desired = Comparator.get_non_compliant_configs(data_1, data_2)
    assert current == data_1
    assert desired == data_2

    current, desired = Comparator.get_non_compliant_configs(data_1, data_3)
    assert current == data_1
    assert desired == data_3

    current, desired = Comparator.get_non_compliant_configs(data_1, data_4)
    assert current == data_1
    assert desired == data_4

    current, desired = Comparator.get_non_compliant_configs(data_2, data_3)
    assert current == data_2
    assert desired == data_3


def test_get_non_compliant_configs_empty_dict():
    current, desired = Comparator.get_non_compliant_configs({}, {})
    assert current is None
    assert desired is None


def test_get_non_compliant_configs_empty_list():
    current, desired = Comparator.get_non_compliant_configs([], [])
    assert current is None
    assert desired is None


def test_get_non_compliant_configs_mixed_and_none():
    current, desired = Comparator.get_non_compliant_configs([], None)
    assert current == []
    assert desired is None
    current, desired = Comparator.get_non_compliant_configs(None, {})
    assert current is None
    assert desired == {}


def test_is_data_same_type_for_bool():
    data_1 = True
    data_2 = False
    data_3 = "test"
    data_4 = 1800
    assert Comparator.is_data_same_type(data_1, data_2) is True
    assert Comparator.is_data_same_type(data_1, data_3) is False
    assert Comparator.is_data_same_type(data_1, data_4) is False


def test_is_data_same_type_for_strings():
    data_1, data_2 = "test", "str"
    data_3 = True
    data_4 = 180
    assert Comparator.is_data_same_type(data_1, data_2) is True
    assert Comparator.is_data_same_type(data_1, data_3) is False
    assert Comparator.is_data_same_type(data_1, data_4) is False


def test_is_data_same_type_for_numbers():
    data_1, data_2, data_3 = 1800, int(1800), float(1800)
    data_4 = "test"
    data_5 = True
    assert Comparator.is_data_same_type(data_1, data_2) is True
    assert Comparator.is_data_same_type(data_2, data_3) is True
    assert Comparator.is_data_same_type(data_1, data_4) is False
    assert Comparator.is_data_same_type(data_1, data_5) is False
