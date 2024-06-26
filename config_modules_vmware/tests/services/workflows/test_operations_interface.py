# Copyright 2024 Broadcom. All Rights Reserved.
from mock import patch

from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.services.workflows.operations_interface import OperationsInterface


class TestOperationsInterface:

    @patch.multiple(OperationsInterface, __abstractmethods__=set())
    def test_should_skip_controller_no_metadata(self):
        operations_interface = OperationsInterface()
        class MockController:
            pass

        assert operations_interface.should_skip_controller(MockController(), None)

    @patch.multiple(OperationsInterface, __abstractmethods__=set())
    def test_should_skip_controller_metadata_filter(self):
        operations_interface = OperationsInterface()
        class MockController:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

        assert operations_interface.should_skip_controller(MockController(), lambda metadata: False)

    @patch.multiple(OperationsInterface, __abstractmethods__=set())
    def test_should_skip_controller_disabled(self):
        operations_interface = OperationsInterface()
        class MockController:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.DISABLED)

        assert operations_interface.should_skip_controller(MockController(), None)

    @patch.multiple(OperationsInterface, __abstractmethods__=set())
    def test_should_skip_controller_false(self):
        operations_interface = OperationsInterface()
        class MockController:
            metadata = ControllerMetadata(status=ControllerMetadata.ControllerStatus.ENABLED)

        assert not operations_interface.should_skip_controller(MockController(), None)
