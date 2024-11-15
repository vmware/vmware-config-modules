# Contributing to `vmware-config-modules`

We welcome contributions from the community and first want to thank you for taking the time to contribute!

Please familiarize yourself with the [Code of Conduct](https://github.com/vmware/.github/blob/main/CODE_OF_CONDUCT.md) before contributing.

__Before you start working with `vmware-config-modules`, please read our [Developer Certificate of Origin](https://cla.vmware.com/dco).__

__All contributions to this repository must be signed as described on that page.__

## Ways to contribute

We welcome many different types of contributions and not all of them need a Pull request. Contributions may include:

* New features and proposals
* Documentation
* Bug fixes
* Issue Triage
* Answering questions and giving feedback
* Helping to onboard new contributors
* Other related activities

## Getting started

### Setting up your dev environment
We recommend setting up a Python virtual environment to avoid having conflicts with local dependencies:
```
# virtual env setup
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements/dev-requirements.txt
```

### Building from source
From the repository root directory run the below commands.
```shell
python3 -m pip install build
python3 -m build
```
 The .whl package will be under the `./dist` directory. That built whl package can be installed locally with
```shell
python3 -m pip install dist/config_modules-*-py3-none-any.whl --force-reinstall
```
### Running the unit tests
To simply run the unit tests, run the following commands.
```shell
python3 -m pip install -r requirements/unit-test-requirements.txt
pytest
```
There is also a script available that will run the tests and generate a coverage report for you which can be invoked with
```shell
./devops/scripts/run_functional_tests.sh
```
### Set up pre-commit
We use pre-commit to give early feedback on code quality and formatting.  
Once pre-commit is installed, it automatically runs whenever a developer tries to do a git commit with new changes. Only if all pre-commit hooks are passed can a developer commit the changes.  
Pre-commit can be installed into your virtual environment from above and set up with the following commands:
```shell
python3 -m pip install pre-commit
pre-commit install
```
Sample pre-commit response:
```
(env) ➜  config-poc git:(test_branch) ✗ git commit -m "test changes"
Fix formatting with Black................................................Passed
Reorder Imports..........................................................Passed
Run security analysis with Bandit........................................Passed
Run static code analysis with pylint.....................................Passed
Generate documentation...................................................Passed
[test_branch 1620b1c] test changes
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Any files modified or generated as part of pre-commit needs to be added to the commit using `git add` before committing.

Individual scripts are also provided in the [./devops/scripts](./devops/scripts) directory in case a developer wants to execute them individually:
- [Code Formatter](./devops/scripts/run_formatting.sh)
- [Re-Order imports](./devops/scripts/run_reorder_imports.sh)
- [Check for CWE violations](./devops/scripts/run_security_analysis.sh)
- [pyLint static analysis](./devops/scripts/run_static_code_analysis.sh)

If the changes are in the API layer, developer needs to generate the openapi spec (using the below steps) and add it to the git commit.
- Build and install config-module with the changes.
- Use the script to generate openapi spec - [Generate OpenAPI specification](./devops/scripts/generate_openapi_spec.py)

## Contribution Flow

This is a rough outline of what a contributor's workflow looks like:

* Make a fork of the repository within your GitHub account
* Create a topic branch in your fork from where you want to base your work
* Make commits of logical units
* Make sure your commit messages are in the proper format (see below)
* Push your changes to the topic branch in your fork
* Create a pull request containing that commit

### Pull Request Checklist
Before submitting your pull request, we advise you to use the following:

1. Check if your code changes will pass both code linting checks and unit tests.
2. Ensure your commit messages are descriptive. Suggestions of information to include as appropriate:
   1. A short summary.
   2. Any related GitHub issue references in the commit message. See [GFM syntax](https://guides.github.com/features/mastering-markdown/#GitHub-flavored-markdown) for referencing issues and commits.
   3. Detailed description
   4. Specify any desired state spec changes.
   5. Product, Category, Component
   6. Compliance Scope (PCI, NIST, VCF Compliance kit, etc.)
   7. Testing performed
3. Check the commits and commits messages and ensure they are free from typos.
4. Code changes have appropriate unit tests.
   1. Code coverage is expected __to be > 80%__.

## Reporting Bugs and Creating Issues

For specifics on what to include in your report, please follow the guidelines in the issue and pull request templates when available.

Issues should have Minimum Complete Verifiable Example (MCVE) that someone would need to be able to reproduce the error. This also means including versions of Python and dependencies, OS and any other relevant information.
