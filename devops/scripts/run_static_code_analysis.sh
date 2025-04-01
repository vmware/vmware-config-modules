#!/bin/bash

set -e
echo "============================================="
echo "Run static code analysis for config-modules"
echo "============================================="
python3 -m pip install -r requirements/api-requirements.txt
python3 -m pip install -r requirements/salt-requirements.txt

python3 -m pip install pylint
python3 -m pylint --rcfile=.pylintrc config_modules_vmware/*
