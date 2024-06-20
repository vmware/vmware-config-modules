# Copyright 2024 Broadcom. All Rights Reserved.

#Test script to be run on the remote host: jump host
function runOnLinuxJump() {
	sshpass -p $LINUX_JUMP_PASSWORD ssh -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@$LINUX_JUMP_IP $1
}

#Creating workspace folder
runOnLinuxJump "if [ -d workspace ]; then rm -rf workspace; fi"
runOnLinuxJump "mkdir -p workspace;mkdir -p ~/workspace/config-modules-venv"

#Installing requirements for openssl1.1
runOnLinuxJump "yum install -y make gcc perl-core pcre-devel wget zlib-devel;"

#Install openssl 1.1 if it isn't installed
runOnLinuxJump "if ! [[ -d ~/openssl-3.1.2 ]]; then wget https://www.openssl.org/source/openssl-3.1.2.tar.gz --no-check-certificate;tar -xzvf openssl-3.1.2.tar.gz;cd openssl-3.1.2;./config --prefix=/usr --openssldir=/etc/ssl --libdir=lib no-shared zlib-dynamic;make;make install_sw;echo export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64 > /etc/profile.d/openssl.sh;fi;"

#Installing the development tools
runOnLinuxJump "yum -y install bzip2-devel libffi-devel;yum -y groupinstall 'Development Tools';"

#Downloading python
runOnLinuxJump "if ! [[ -d ~/Python-$PYTHON_VERSION ]]; then wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz;tar -xvf Python-$PYTHON_VERSION.tgz;cd ~/Python-$PYTHON_VERSION;source /etc/profile.d/openssl.sh;./configure --enable-optimizations --with-openssl=/usr;make altinstall;fi;"

#Copy config-module source to jump host
sshpass -p $LINUX_JUMP_PASSWORD scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ~/config-modules-repo.tar root@$LINUX_JUMP_IP:~/workspace

#Environment prep completed, running tests
runOnLinuxJump "~/Python-$PYTHON_VERSION/python -m venv ~/workspace/config-modules-venv;\
  ~/Python-$PYTHON_VERSION/python -m pip install --upgrade pip;\
  source ~/workspace/config-modules-venv/bin/activate;cd ~/workspace;\
	tar -xf config-modules-repo.tar;\
  cd config-modules;\
  ~/Python-$PYTHON_VERSION/python -m pip install dist/config_modules_vmware-*-py3-none-any.whl --force-reinstall;
	~/Python-$PYTHON_VERSION/python -m pip install -r requirements/functional-test-requirements.txt;\
	wget https://vdc-download.vmware.com/vmwb-repository/dcr-public/e36c0c36-2dee-4f3c-9ed3-fcf719f4ed81/88ed011c-74ea-4afd-b7eb-d9fab49f7a46/esxcli-8.0.0-22179150.tgz;\
	pip install esxcli-8.0.0-22179150.tgz;\
	export SM_HOST=$SM_HOST;\
  export SM_USERNAME=$SM_USERNAME;\
  export SM_PASSWORD=$SM_PASSWORD;\
  export TEST_SET_ID=${TEST_SET_ID};\
  ~/Python-$PYTHON_VERSION/python -m pytest functional_tests/central_test -s --capture sys --include_list '$INCLUDE_LIST' --exclude_list '$EXCLUDE_LIST or $ADDITIONAL_EXCLUDE_LIST'  --rollback $Rollback --compliance_values  functional_tests/values/compliance_values.yaml --drift_values functional_tests/values/drift_values.yaml  2>&1 | tee -a functional_test.log || true ";\

  #Copy test result file from jump host to the jenkins host
  mkdir -p test_result/$BUILD_ID
  sshpass -p $LINUX_JUMP_PASSWORD scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  root@$LINUX_JUMP_IP://root/workspace/config-modules/functional_test.log test_result/$BUILD_ID/functional_test.log
  sshpass -p $LINUX_JUMP_PASSWORD scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  root@$LINUX_JUMP_IP://root/workspace/config-modules/functional_tests/central_test/reports/functional_test.html test_result/$BUILD_ID/functional_test.html

  if ! test -f test_result/$BUILD_ID/functional_test.log; then
      exit 1
  fi

  if ! test -f test_result/$BUILD_ID/functional_test.html; then
      exit 1
  fi

  if grep -Fq 'FAILED functional_tests' test_result/$BUILD_ID/functional_test.log
  then
      echo "fail exit 1"
      # Fail jenkins job
      exit 1
  else
      echo "fail exit 0"
      exit 0
  fi
