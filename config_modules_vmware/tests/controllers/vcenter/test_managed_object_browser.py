import os.path
import xml.dom.minidom  # nosec
import xml.etree.ElementTree as ETree  # nosec

import pytest
from mock import patch

from config_modules_vmware.controllers.vcenter.managed_object_browser import ManagedObjectBrowser
from config_modules_vmware.controllers.vcenter.managed_object_browser import MOB_KEY
from config_modules_vmware.controllers.vcenter.managed_object_browser import SERVICE_NAME
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus


@pytest.fixture()
def setup_teardown():
    xml_content = f'<config><vpxd><enableDebugBrowse>true</enableDebugBrowse></vpxd></config>'
    tmp_file = 'temp.xml'

    dom = xml.dom.minidom.parseString(xml_content)  # nosec
    pretty_xml = dom.toprettyxml(indent="  ")

    with open('temp.xml', 'w', encoding='utf-8') as f:
        f.write(pretty_xml + '\n')

    yield tmp_file

    if os.path.exists(tmp_file):
        os.remove(tmp_file)


class TestManagedObjectBrowser:
    def setup_method(self):
        self.controller = ManagedObjectBrowser()
        self.incorrect_xml_content = f'<config><vpxd><enableDebugBrowse>unexpected_value</enableDebugBrowse></vpxd></config>'
        self.desired_value = False
        self.non_compliant_value = True

    @patch("config_modules_vmware.controllers.vcenter.managed_object_browser.VPXD_CFG_FILE_PATH", new='temp.xml')
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_get_success(self, mock_vc_context, setup_teardown):
        result, errors = self.controller.get(mock_vc_context)

        assert result is True
        assert not errors

    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("xml.etree.ElementTree.parse")
    def test_get_failed(self, mock_xml_parse, mock_vc_context):
        mock_xml_parse.return_value.getroot.return_value = ETree.fromstring(self.incorrect_xml_content)

        result, errors = self.controller.get(mock_vc_context)
        expected_errors = ['Unexpected value unexpected_value for property enableDebugBrowse']
        assert errors == expected_errors
        assert result is None

    @patch("config_modules_vmware.controllers.vcenter.managed_object_browser.VPXD_CFG_FILE_PATH", new='temp.xml')
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success(self,  mock_execute_shell_cmd, mock_vc_context, setup_teardown):
        mock_execute_shell_cmd.side_effect = [
            ("Successfully restarted service vpxd", "", 1),
            ("Running:\nvmware-vpxd", "", 1)
        ]

        result, errors = self.controller.set(mock_vc_context, self.desired_value)
        tmp_file = setup_teardown
        tree = ETree.parse(tmp_file)  # nosec
        root = tree.getroot()
        vpxd_element = root.find('vpxd')
        assert vpxd_element is not None

        mob_element = vpxd_element.find(MOB_KEY)
        assert mob_element is not None
        assert mob_element.text == 'false'

        assert result == RemediateStatus.SUCCESS
        assert not errors

        # Check get post set
        result, errors = self.controller.get(mock_vc_context)
        assert result is self.desired_value
        assert not errors

    @patch("config_modules_vmware.controllers.vcenter.managed_object_browser.VPXD_CFG_FILE_PATH", new='temp.xml')
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_failed(self,  mock_execute_shell_cmd, mock_vc_context, setup_teardown):
        mock_execute_shell_cmd.side_effect = [
            ("Successfully restarted service vpxd", "", 1),
            ("", "", 1)
        ]

        result, errors = self.controller.set(mock_vc_context, self.desired_value)
        expected_errors = [f"Service {SERVICE_NAME} is not running post restart. Please resolve this issue."]

        assert result == RemediateStatus.FAILED
        assert errors == expected_errors

    @patch("config_modules_vmware.controllers.vcenter.managed_object_browser.VPXD_CFG_FILE_PATH", new='temp.xml')
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    def test_check_compliance_non_compliant(self, mock_vc_context, setup_teardown):
        result = self.controller.check_compliance(mock_vc_context, self.desired_value)

        expected_result = {
            consts.STATUS: ComplianceStatus.NON_COMPLIANT,
            consts.CURRENT: True,
            consts.DESIRED: False
        }
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.managed_object_browser.VPXD_CFG_FILE_PATH", new='temp.xml')
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_check_remediation_and_compliance_post_remediation(self, mock_execute_shell_cmd,
                                                               mock_vc_context, setup_teardown):
        mock_execute_shell_cmd.side_effect = [
            ("Successfully restarted service vpxd", "", 1),
            ("Running:\nvmware-vpxd", "", 1)
        ]
        result = self.controller.remediate(mock_vc_context, self.desired_value)

        expected_result = {
            consts.STATUS: RemediateStatus.SUCCESS,
            consts.OLD: True,
            consts.NEW: False
        }
        assert result == expected_result

        # check compliance post remediation
        result = self.controller.check_compliance(mock_vc_context, self.desired_value)

        expected_result = {
            consts.STATUS: ComplianceStatus.COMPLIANT
        }
        assert result == expected_result

    @patch("config_modules_vmware.controllers.vcenter.managed_object_browser.VPXD_CFG_FILE_PATH", new='temp.xml')
    @patch("config_modules_vmware.framework.auth.contexts.vc_context.VcenterContext")
    @patch("config_modules_vmware.framework.utils.utils.run_shell_cmd")
    def test_set_success_create_missing_elements(self,  mock_execute_shell_cmd, mock_vc_context, setup_teardown):
        mock_execute_shell_cmd.side_effect = [
            ("Successfully restarted service vpxd", "", 1),
            ("Running:\nvmware-vpxd", "", 1)
        ]
        xml_content = f'<config></config>'
        tmp_file = 'temp.xml'

        dom = xml.dom.minidom.parseString(xml_content)  # nosec
        pretty_xml = dom.toprettyxml(indent="  ")

        with open('temp.xml', 'w', encoding='utf-8') as f:
            f.write(pretty_xml + '\n')

        result, errors = self.controller.set(mock_vc_context, self.desired_value)
        assert result == RemediateStatus.SUCCESS
        assert errors == []

        if os.path.exists(tmp_file):
            os.remove(tmp_file)
