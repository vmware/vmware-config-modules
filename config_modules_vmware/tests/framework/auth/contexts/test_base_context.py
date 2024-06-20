# Copyright 2024 Broadcom. All Rights Reserved.
from mock import patch

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext


class TestBaseContext:

    @patch('config_modules_vmware.framework.auth.contexts.base_context.BaseContext.__enter__')
    @patch('config_modules_vmware.framework.auth.contexts.base_context.BaseContext.__exit__')
    def test_base_context_initialization(self, mock_exit, mock_enter):
        product_category = BaseContext.ProductEnum.VCENTER
        product_version = "8.0.3"
        context = BaseContext(product_category=BaseContext.ProductEnum.NSXT_EDGE, product_version="1.0")
        with context:
            context.product_category = product_category
            context.product_version = product_version
            pass
        assert context.product_category == product_category
        assert context.product_version == product_version
        assert mock_enter.call_count == 1
        assert mock_exit.call_count == 1
