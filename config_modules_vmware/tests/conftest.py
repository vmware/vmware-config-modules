import pytest
from mock import MagicMock
from mock import mock_open


class TestUtils:
    builtin_open = open

    @staticmethod
    def create_mock_file_open(read_data="", filename=None, raise_error=False):
        def mock_open_callable(*args, **kwargs):
            if filename is None or filename in args[0]:
                if raise_error:
                    raise FileNotFoundError("File not found")
                return mock_open(
                    read_data=read_data)(*args, **kwargs)
            return TestUtils.builtin_open(*args, **kwargs)
        return mock_open_callable


@pytest.fixture
def test_utils():
    return TestUtils
