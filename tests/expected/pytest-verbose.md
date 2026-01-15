# Test Report

**Summary:** 7/11 passed, 2 failed, 1 skipped, 1 xfail

## Errors

### tests/examples.py::test_setup_error ERROR in setup

```python
examples.py:96: in broken_fixture
    raise RuntimeError(msg)
E   RuntimeError: Fixture setup failed
```

## Failures

### tests/examples.py::test_edge_case FAILED

```python
examples.py:42: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
examples.py:20: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```

### tests/examples.py::test_known_bug XFAIL

**Reason:** Bug #123

```python
examples.py:57: in test_known_bug
    raise ValueError(msg)
E   ValueError: Known issue
```

## Skipped

### tests/examples.py::test_future_feature SKIPPED

**Reason:** Not implemented yet

## Passes

- tests/examples.py::test_invalid_input[-False]
- tests/examples.py::test_invalid_input[x-True]
- tests/examples.py::test_simple
- tests/examples.py::test_validation_pass
- tests/examples.py::test_critical_path
- tests/examples.py::test_with_output
- tests/examples.py::test_with_warning

## Passes (with output)

- tests/examples.py::test_with_output PASSED
  stdout: Debug: processing started
  stderr: Status: OK
## Warnings

- tests/examples.py::test_with_warning: This is a test warning
