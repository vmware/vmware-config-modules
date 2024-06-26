#!/bin/bash

set -e
echo "============================================="
echo "Run security for config-modules"
echo "============================================="
python3 -m pip install bandit
python3 -m bandit -r -x tests config_modules_vmware
