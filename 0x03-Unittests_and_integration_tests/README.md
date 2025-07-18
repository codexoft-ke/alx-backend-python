# 0x03. Unittests and Integration Tests

This project focuses on understanding and implementing unit tests and integration tests in Python using the `unittest` framework and various testing patterns.

## Learning Objectives

At the end of this project, you should be able to explain:
- The difference between unit and integration tests
- Common testing patterns such as mocking, parametrizations and fixtures
- How to use the `unittest` framework effectively
- How to use `unittest.mock` for mocking dependencies
- How to parameterize tests for multiple input scenarios

## Concepts Covered

### Unit Testing
Unit testing is the process of testing that a particular function returns expected results for different sets of inputs. A unit test should:
- Test standard inputs and corner cases
- Only test the logic defined inside the tested function
- Mock most calls to additional functions, especially network or database calls
- Answer the question: "If everything defined outside this function works as expected, does this function work as expected?"

### Integration Testing
Integration tests aim to test a code path end-to-end. They:
- Test interactions between every part of your code
- Only mock low-level functions that make external calls (HTTP requests, file I/O, database I/O)
- Verify that different components work together correctly

## Requirements

- All files interpreted/compiled on Ubuntu 18.04 LTS using python3 (version 3.7)
- All files should end with a new line
- First line of all files should be `#!/usr/bin/env python3`
- Code should use the pycodestyle style (version 2.5)
- All files must be executable
- All modules, classes, and functions should have documentation
- All functions and coroutines must be type-annotated

## Project Structure

```
.
├── README.md
├── utils.py              # Utility functions to be tested
├── client.py             # Client class for GitHub API interactions
├── fixtures.py           # Test fixtures and data
└── test_utils.py         # Unit tests for utils module
```

## Tasks

### 0. Parameterize a unit test

**File**: `test_utils.py`

Created a `TestAccessNestedMap` class that inherits from `unittest.TestCase` to test the `utils.access_nested_map` function.

**Features**:
- Uses `@parameterized.expand` decorator to test multiple input scenarios
- Tests the function with different nested map structures and paths
- Verifies the function returns expected results for each input combination
- Method body is kept to 2 lines as required

**Test Cases**:
- `nested_map={"a": 1}, path=("a",)` → expects `1`
- `nested_map={"a": {"b": 2}}, path=("a",)` → expects `{"b": 2}`
- `nested_map={"a": {"b": 2}}, path=("a", "b")` → expects `2`

## Running Tests

Execute tests using:
```bash
python -m unittest test_utils.py
```

For verbose output:
```bash
python -m unittest test_utils.py -v
```

## Dependencies

- `unittest` (built-in)
- `parameterized` (for parameterized testing)
- `typing` (for type annotations)

## Resources

- [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [parameterized](https://pypi.org/project/parameterized/)
- [Memoization](https://en.wikipedia.org/wiki/Memoization)
