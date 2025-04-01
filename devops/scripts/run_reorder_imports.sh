#!/bin/sh

set -e
echo "============================================="
echo "Run reorder-python-imports for config-modules"
echo "============================================="
python3 -m pip install reorder-python-imports

run_all_files()
{
  FILES_TO_SCAN=$(find . -name "*.py")
  echo "$FILES_TO_SCAN" | while IFS= read -r file; do
    if [ "${file##*.}" = "py" ] && [ "${file#*config_modules_vmware/framework/clients/vcenter/dependencies/}" = "$file" ] && [ "${file#*support/}" = "$file" ] && [ "${file#*vcf_compliance_control_salt/}" = "$file" ]; then
      changed_file=$( (reorder-python-imports --exit-zero-even-if-changed "$file" 1>&2) 2>&1)
        if [ -n "$changed_file" ]
        then
          echo "$changed_file"
        fi
    fi
  done
}

run_passed_files()
{
  for file in "$@"
  do
    if [ "${file##*.}" = "py" ] && [ "${file#*config_modules_vmware/framework/clients/vcenter/dependencies/}" = "$file" ] && [ "${file#*support/}" = "$file" ] && [ "${file#*vcf_compliance_control_salt/}" = "$file" ]; then
      changed_file=$( (reorder-python-imports --exit-zero-even-if-changed "$file" 1>&2) 2>&1)
        if [ -n "$changed_file" ]
        then
          echo "$changed_file"
        fi
    fi
  done
}


if [ $# -eq 0 ]; then
  echo "No files passed. Running reorder-python-imports on all .py files"
  function_output=$(run_all_files)
  if [ -n "$function_output" ]
  then
    echo Files that failed:
    echo "$function_output"
    exit 1
  fi

else
  echo "Files passed as arguments. Running reorder-python-imports on the passed in files"
  function_output=$(run_passed_files "$@")
  if [ -n "$function_output" ]
  then
    echo Files that failed:
    echo "$function_output"
    exit 1
  fi
fi
