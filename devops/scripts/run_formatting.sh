#!/bin/bash

set -e
echo "============================================="
echo "Run formatting for config-modules"
echo "============================================="
python3 -m pip install black==23.3.0
if [ "$1" ]; then
  python3 -m black -l 120 $1 --extend-exclude "config_modules_vmware/tests/|framework/clients/vcenter/dependencies/" .
else
  python3 -m black -l 120 --extend-exclude "config_modules_vmware/tests/|framework/clients/vcenter/dependencies/" .
fi
