#!/bin/bash

set -e

echo "Run static code checks"

sh devops/scripts/run_formatting.sh --check

sh devops/scripts/run_reorder_imports.sh

sh devops/scripts/run_security_analysis.sh

sh devops/scripts/run_static_code_analysis.sh

echo "Run build"

python3 -m build
