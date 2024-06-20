# Copyright 2024 Broadcom. All Rights Reserved.
import pytest
from mock import patch
from requests import HTTPError

from config_modules_vmware.framework.clients.aria_suite import aria_auth


@patch('requests.get')
def test_get_http_headers(mock_get):
    mock_get.json.return_value = {"username": "username", "password": "password"}     # nosec
    headers = aria_auth.get_http_headers()
    assert headers is not None
    assert all(key in headers for key in ['Authorization', 'Accept', 'Content-Type'])

    mock_get.return_value.status_code = 404
    mock_get.return_value.raise_for_status.side_effect = HTTPError
    with pytest.raises(HTTPError):
        aria_auth.get_http_headers()
