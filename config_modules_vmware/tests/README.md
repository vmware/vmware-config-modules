## Testing Guidelines

* All tests adhere to pep8 standards.
* All tests must be stand-alone and deterministic.
* All changes shall be accompanied by a test.

## Running tests

### Running tests locally (unit tests)

Invoke the below from root directory:
```
./devops/scripts/run_functional_tests.sh
```

## Coverage

### Running tests with coverage:
`coverage run -m pytest`

### Viewing coverage data:
`coverage html`