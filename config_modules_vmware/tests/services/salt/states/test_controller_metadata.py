# Copyright 2024 Broadcom. All Rights Reserved.
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from config_modules_vmware.services.salt.states import controller_metadata

NAME = "test"


@pytest.fixture
def configure_loader_modules():
    return {controller_metadata: {"__opts__": {}, "__pillar__": {}}}


def test_virtual():
    assert controller_metadata.__virtual__() == "vmware_controller_metadata"


@pytest.fixture(autouse=True)
def patch_salt_loaded_objects():
    # This needs to be the same as the module we're importing
    with (
        patch(
            "config_modules_vmware.services.salt.states.controller_metadata.__opts__",
            {
                "cachedir": ".",
                "saltext.vmware": {
                    "host": "test.vcenter.local",
                    "user": "test",
                    "password": "test",
                },
            },
            create=True,
        ),
        patch.object(controller_metadata, "__pillar__", {}, create=True),
        patch.object(controller_metadata, "__salt__", {}, create=True),
    ):
        yield


@pytest.mark.skip(reason="Disabling as this loads the salt file module and does not work on mac OS (M1)")
def test_managed():
    mock_validate = MagicMock(return_value=True)
    mock_file_managed = MagicMock(return_value={"Result": True})
    mock_controller_metadata = {
        "vcenter": {
            "backup_schedule_config": {
                "metadata": {
                    "global_key": "global_value",
                    "configuration_id": "1112",
                    "instance_metadata_1": True,
                    "metadata_2": {"nested_key_1": "nested_key_1_value"},
                }
            }
        }
    }

    with patch.dict(
        controller_metadata.__salt__,
        {
            "vmware_controller_metadata.validate": mock_validate,
        },
    ):
        with patch(
            "salt.states.file.managed", autospec=True, return_value=mock_file_managed
        ):
        # Alternate loading
        # with patch.dict(
        #     file.__states__, {"file.managed": mock_file_managed}
        # ):
            result = controller_metadata.managed(
                name=NAME, controller_metadata=mock_controller_metadata
            )

    assert result is not None
    assert result["Result"]
