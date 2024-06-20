#!/bin/bash

set -e

python3 -m pip install -r requirements/unit-test-requirements.txt

echo "Build and install config-modules"
rm -rf dist/*
python3 -m pip install build
python3 -m build
built_package='dist/'$(python3 setup.py --fullname)'-py3-none-any.whl[api]'
python3 -m pip install $built_package --force-reinstall

echo "Running pytest with coverage"
coverage run -m pytest

echo "Coverage report:"
coverage report -m
