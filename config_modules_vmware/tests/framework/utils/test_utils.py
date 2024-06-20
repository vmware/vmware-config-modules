# Copyright 2024 Broadcom. All Rights Reserved.
import json
from subprocess import CompletedProcess

import pytest
from mock import mock_open
from mock import patch

from config_modules_vmware.framework.utils import utils


def test_filter_dict_keys_valid_input():
    input_data = {'key1': 1, 'key2': 'abc', 'key3': True}
    desired_keys = ['key1', 'key3']
    expected_result = {'key1': 1, 'key3': True}
    assert utils.filter_dict_keys(input_data, desired_keys) == expected_result


def test_filter_dict_keys_empty_input_data():
    input_data = {}
    desired_keys = ['key1', 'key3']
    assert utils.filter_dict_keys(input_data, desired_keys) == {}


def test_filter_dict_keys_empty_desired_keys():
    input_data = {'key1': 1, 'key2': 'abc', 'key3': True}
    desired_keys = []
    assert utils.filter_dict_keys(input_data, desired_keys) == {}


def test_filter_dict_keys_invalid_input_data_type():
    with pytest.raises(TypeError, match = "Input 'data' must be a dictionary."):
        utils.filter_dict_keys('invalid_data', ['key1'])


def test_filter_dict_keys_invalid_desired_keys_type():
    with pytest.raises(TypeError, match = "Input 'desired_keys' must be a list."):
        utils.filter_dict_keys({'key1': 1, 'key2': 'abc', 'key3': True}, 'invalid_keys')


def test_read_json_file_valid_file_path():
    json_file_path = 'valid_file.json'
    json_data = {'key1': 1}

    with patch('os.path.exists', return_value=True), \
            patch('os.path.isfile', return_value=True), \
            patch('builtins.open', mock_open(read_data=json.dumps(json_data))):
        assert utils.read_json_file(json_file_path) == json_data


def test_read_json_file_invalid_file_path():
    json_file_path = 'non_existent_file.json'
    with patch('os.path.exists', return_value=True), \
            pytest.raises(Exception, match=f"Missing file {json_file_path}."):
        utils.read_json_file(json_file_path)


def test_read_json_file_invalid_file_type():
    json_file_path = 'invalid.txt'
    with patch('os.path.exists', return_value=True), \
            patch('os.path.isfile', return_value=True), \
            patch('builtins.open', mock_open(read_data="abc")), \
            pytest.raises(Exception, match=f"Error decoding {json_file_path}."):
        utils.read_json_file(json_file_path)


def test_read_json_file_invalid_json_data():
    json_file_path = 'incorrect.json'
    with patch('os.path.exists', return_value=True), \
            patch('os.path.isfile', return_value=True), \
            patch('builtins.open', mock_open(read_data='{"key1": }')), \
            pytest.raises(Exception, match=f"Error decoding {json_file_path}."):
        utils.read_json_file(json_file_path)


@patch('subprocess.run')
def test_run_shell_cmd(mock_subprocess):
    expected_output = CompletedProcess(args=None, returncode=0, stdout="sample_output", stderr="sample_error")
    mock_subprocess.return_value = expected_output
    command_output, command_error, _ = utils.run_shell_cmd("sample_command")
    assert command_output == expected_output.stdout
    assert command_error == expected_output.stderr


def test_run_shell_cmd_invalid_input():
    with pytest.raises(ValueError):
        utils.run_shell_cmd("")


class TestUtils:
    def setup_method(self):
        self.std_err_bytes = b'Std Err'
        self.std_out_bytes = b'Std Out'

        self.std_err_str = self.std_err_bytes.decode('utf-8')
        self.std_out_str = self.std_out_bytes.decode('utf-8')

    def test_filter_dict_keys(self):
        desired_output = {
            "internet_access_enabled": True,
            "host": "hcl.vmware.com",
            "port": 80,
            "user": "proxy_user"
        }

        proxy_config = {
            "internet_access_enabled": True,
            "host": "hcl.vmware.com",
            "port": 80,
            "user": "proxy_user",
            "password": "super_complex_string"
        }
        desired_keys = ['internet_access_enabled', 'host', 'port', 'user']
        result = utils.filter_dict_keys(proxy_config, desired_keys)
        assert result == desired_output

    def test_dict_filter_wrong_input_type(self):
        invalid_type = [{
            "internet_access_enabled": True,
            "host": "hcl.vmware.com",
            "port": 80,
            "user": "proxy_user",
            "password": "super_complex_string"
        }]
        desired_keys = ['internet_access_enabled', 'host', 'port', 'user']

        with pytest.raises(TypeError):
            utils.filter_dict_keys(invalid_type, desired_keys)

    def test_dict_filter_wrong_desired_key_type(self):
        proxy_config = {
            "internet_access_enabled": True,
            "host": "hcl.vmware.com",
            "port": 80,
            "user": "proxy_user",
            "password": "super_complex_string"
        }
        invalid_filter = {"foo": "bar"}
        with pytest.raises(TypeError):
            utils.filter_dict_keys(proxy_config, invalid_filter)

    def test_get_product_major_version(self):
        assert utils.get_product_major_version("8.0.3") == 8

    def test_get_product_major_version_empty(self):
        assert utils.get_product_major_version("") is None

    def test_get_product_major_version_not_version(self):
        assert utils.get_product_major_version("test") is None

    def test_get_product_major_version_invalid(self):
        assert utils.get_product_major_version(".") is None
