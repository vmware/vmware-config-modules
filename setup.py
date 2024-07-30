# Copyright 2024 Broadcom. All Rights Reserved.
from setuptools import setup

import config_modules_vmware


def read(fname):
    with open(fname, "r") as fh:
        return fh.read()


def _parse_requirements(requirements_file):
    requirements = []
    with open(requirements_file, encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith(("#", "-r", "--")):
                continue
            requirements.append(line)
    return requirements


setup(
    name=config_modules_vmware.name,
    # duplicate information due to concourse pipeline requirement
    version="0.13.2.0",
    description=config_modules_vmware.description,
    author=config_modules_vmware.author,
    install_requires=_parse_requirements("requirements/prod-requirements.txt"),
    extras_require={"api": _parse_requirements("requirements/api-requirements.txt")},
    python_requires=">=3.7, <3.12.0",
    tests_require=_parse_requirements("requirements/unit-test-requirements.txt"),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
)
