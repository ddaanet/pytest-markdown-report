# Test Report

**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail

## Failures

### tests/examples.py::test_edge_case FAILED

```python
examples.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
examples.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```
