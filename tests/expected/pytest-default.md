# Test Report

**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail

## Failures

### tests/test_example.py::test_edge_case FAILED

```python
test_example.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_example.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```

### tests/test_example.py::test_known_bug XFAIL

**Reason:** Bug #123

```python
test_example.py:54: in test_known_bug
    raise ValueError("Known issue")
E   ValueError: Known issue
```

## Skipped

### tests/test_example.py::test_future_feature SKIPPED

**Reason:** Not implemented yet
