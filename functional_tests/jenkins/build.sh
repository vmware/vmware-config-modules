# Copyright 2024 Broadcom. All Rights Reserved.

#Build script to build config module on jenkins host
if ! python3.7 --version ; then
	curl -O https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz
	tar -xzf Python-3.7.17.tgz
	cd Python-3.7.17/
	./configure --enable-optimizations
	make altinstall
	unlink /usr/bin/python3
  ln -s  /usr/local/bin/python3.7 /usr/bin/python3
  cd ..
fi

cd  ./config-modules
python3 -m venv venv
source  venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/prod-requirements.txt
python3 -m pip install build

devops/scripts/build.sh
ls dist/*
cd ..
mkdir -p test_result/$BUILD_ID

if test -f drift_values.yaml; then
  cp drift_values.yaml ./config-modules/functional_tests/values
  cp compliance_values.yaml ./config-modules/functional_tests/values
else
  cp ./config-modules/functional_tests/values/sample_nimbus_drift_values.yaml ./config-modules/functional_tests/values/drift_values.yaml
  cp ./config-modules/functional_tests/values/sample_nimbus_compliance_values.yaml ./config-modules/functional_tests/values/compliance_values.yaml
fi

tar -cf ~/config-modules-repo.tar ./config-modules

ls ~/config-modules-repo.tar

if [ -z "$RACETRACK_ID" ]
then
	echo "No racetrack provided"
else
	echo "https://racetrack.eng.vmware.com/result.php?id=$RACETRACK_ID"
fi