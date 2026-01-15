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
