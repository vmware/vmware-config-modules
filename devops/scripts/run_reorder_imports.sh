#!/bin/bash

set -e
echo "============================================="
echo "Run reorder-python-imports for config-modules"
echo "============================================="
python3 -m pip install reorder-python-imports

if [ $# -eq 0 ]
then
  echo "No files passed. Running reorder-python-imports on all .py files"
  FILES_TO_SCAN=$(find . -name "*.py" )
else
  FILES_TO_SCAN="$*"
fi
while read -r line; do
  filearray=("$line")
  for file in $filearray; do
    if [[ "$file" == *.py && "$file" != *"config_modules_vmware/framework/clients/vcenter/dependencies/"* ]]
    then
       reorder-python-imports --exit-zero-even-if-changed "$file"
    fi
  done
done <<< "$FILES_TO_SCAN"

