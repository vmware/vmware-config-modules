#!/bin/bash

set -e

python3 -m pip install sphinx==5.3.0 sphinx-markdown-builder==0.6.5

printf "Config Modules Controllers\n=============================\n\nProduct Controllers\n----------------------\n.. toctree::\n   :maxdepth: 3\n\n" > docs/controllers/index.rst
for dir in config_modules_vmware/controllers/*/
do
  dirname=$(basename "$dir")
  if [ "$dirname" != "__pycache__" ] ; then
    sphinx-apidoc -efEMT -o docs/controllers/"$dirname" config_modules_vmware/controllers/"$dirname" config_modules_vmware/controllers/"$dirname"/utils*
    printf '   '"$dirname"'/'"$dirname"'\n' >> docs/controllers/index.rst
  fi
done
sphinx-build -b markdown -E docs/controllers docs/controllers/markdown

echo ""
echo "Now run \"git add docs/controllers\" to include the generated docs in your commit."
