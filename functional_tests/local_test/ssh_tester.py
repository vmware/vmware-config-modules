# Copyright 2024 Broadcom. All Rights Reserved.
import json
import os
import re

from distutils.version import StrictVersion

from functional_tests.local_test.ssh_command import SshCommand
from functional_tests.utils.constants import AUTH_CONTEXT
from functional_tests.utils.constants import CONTROL
from functional_tests.utils.constants import HOST_NAME
from functional_tests.utils.constants import PRODUCT
from functional_tests.utils.constants import ROLLBACK
from functional_tests.utils.constants import SSH_CREDENTIAL
from functional_tests.utils.credential_api_client import Credential
from functional_tests.utils.credential_api_client import get_sddc_manager_context

REGEX_PATTERN = r"Python\s*([\d.]+\d)\n"


def get_required_python_version():
    version = os.getenv("PYTHON_VERSION")
    return version if version else "3.7"


class SshTest(SshCommand):
    cache_instanes = {}  # SshTest instances are cached by appliance host name

    def __init__(self, credential: Credential):
        self.python = "python"
        super().__init__(credential)
        self.setup_test_env(get_required_python_version())

    @classmethod
    def get_instance(cls, credential: Credential):
        if credential.hostname not in cls.cache_instanes:
            cls.cache_instanes[credential.hostname] = SshTest(credential)
        return cls.cache_instanes[credential.hostname]

    def run_ssh_test(self, product_control_dict):
        """
        use ssh to run the control functional tet on the appliance locally
        :param product_control_dict: product and control dict
        :type: dict
        :return: functional test result
        :rtype: str
        """
        sm_context = get_sddc_manager_context()
        local_test_dict = {}
        for key in product_control_dict:
            if key == AUTH_CONTEXT or key == SSH_CREDENTIAL:
                pass
            else:
                local_test_dict[key] = product_control_dict[key]
        file_name = local_test_dict[PRODUCT] + "_" + local_test_dict[CONTROL] + "_" + local_test_dict[HOST_NAME]
        root_path = "~/workspace/config-modules/"
        ctx_file_path = root_path + file_name + ".json"
        expanded_file_path = os.path.expanduser(ctx_file_path)
        with open(expanded_file_path, "w", encoding="utf8") as json_file:
            json.dump(local_test_dict, json_file, ensure_ascii=False)

        self.scp_put(expanded_file_path, remote_path=f"{root_path}")
        local_test_log_file = root_path + file_name + ".log"

        cmd = f"source ~/workspace/config-modules-venv/bin/activate;cd ~/workspace/config-modules;\
                         export SM_HOST={sm_context.hostname};\
                         export SM_USERNAME={sm_context.username};\
                         export SM_PASSWORD={sm_context.password};\
                         {self.python} -m pytest functional_tests/local_test -s --capture sys --context {ctx_file_path} 2>&1 | tee -a {local_test_log_file};"
        print(f"{cmd}\n")
        output, error = self.send_cmd(cmd)
        return output, error

    def setup_test_env(self, python_version):
        # create workspace
        self.send_cmd(
            "shell; chsh -s /bin/bash; if [ -d workspace ]; then rm -rf workspace; fi; mkdir -p workspace;\
        mkdir -p ~/workspace/config-modules-venv;"
        )

        # copy source repo tar file
        self.scp_put("~/workspace/config-modules-repo.tar", remote_path="~/workspace")

        # Get python version, check if the python meet the minimum version requirement
        if StrictVersion(self._get_appliance_python_version()) < StrictVersion(python_version):
            install_cmds = (
                [
                    "yum install -y make gcc perl-core pcre-devel wget zlib-devel;",
                    "if ! [[ -d ~/openssl-3.1.2 ]]; then wget https://www.openssl.org/source/openssl-3.1.2.tar.gz --no-check-certificate;tar -xzvf openssl-3.1.2.tar.gz;cd openssl-3.1.2;./config --prefix=/usr --openssldir=/etc/ssl --libdir=lib no-shared zlib-dynamic;make;make install_sw;echo export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64 > /etc/profile.d/openssl.sh;fi;",
                    "yum -y install bzip2-devel libffi-devel;yum -y groupinstall 'Development Tools';",
                    f"if ! [[ -d ~/Python-{python_version} ]]; then wget https://www.python.org/ftp/python/{python_version}/Python-{python_version}.tgz;tar -xvf Python-{python_version}.tgz;cd ~/Python-{python_version};source /etc/profile.d/openssl.sh;./configure --enable-optimizations --with-openssl=/usr;make altinstall;fi;",
                ],
            )
            for cmd in install_cmds:
                self.send_cmd(cmd)
            self.python = f"~/Python-{python_version}/python"

        python_venv_cmd = f"{self.python} -m venv ~/workspace/config-modules-venv; cd ~/workspace;\
                         if ! [[-d pip ]]; then curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; {self.python} get-pip.py; fi;\
                         {self.python} -m pip install --upgrade pip;\
                         source ~/workspace/config-modules-venv/bin/activate;\
                         tar -xf config-modules-repo.tar;\
                         cd config-modules;\
                         {self.python} -m pip install dist/config_modules_vmware-*-py3-none-any.whl --force-reinstall;\
                         {self.python} -m pip install -r requirements/functional-test-requirements.txt;\
                         wget https://vdc-download.vmware.com/vmwb-repository/dcr-public/e36c0c36-2dee-4f3c-9ed3-fcf719f4ed81/88ed011c-74ea-4afd-b7eb-d9fab49f7a46/esxcli-8.0.0-22179150.tgz;\
                         pip install esxcli-8.0.0-22179150.tgz;"

        self.send_cmd(python_venv_cmd)

    def _get_appliance_python_version(self):
        version = "0.0"
        try:
            string, error = self.send_cmd("python --version")
            version = re.search(REGEX_PATTERN, string).group(1)
        except Exception as e:
            print(f"Fail to get the python version {e}\n")
        return version
