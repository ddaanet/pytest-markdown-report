# Test Plan: -r Flag Functionality

## Overview
Add test coverage for `-r` flag support (Phase 2 feature) to verify that `-rs` and `-rx` flags correctly control which sections appear in default mode output.

## Existing Coverage

The following scenarios are **already tested**:

✅ **Default mode baseline** - `test_default_mode()` verifies no XFAIL/Skipped sections
✅ **Verbose shows all sections** - `test_verbose_mode()` confirms all sections appear
✅ **Section ordering** - `test_skipped_section_separate()` verifies order in verbose mode
✅ **Quiet mode** - `test_quiet_mode()` verifies minimal output
✅ **No trailing blank lines** - `test_no_trailing_blank_lines()` checks all modes

## Missing Test Cases

### 1. -rs Flag Shows Skipped Section
**Test:** `test_default_with_rs_flag`
**Command:** `pytest examples.py -rs`

**Expected:**
- ✓ Failures section present
- ✓ Skipped section present
- ✗ XFAIL NOT present in Failures

**Verification:**
```python
def test_default_with_rs_flag() -> None:
    """Test -rs shows skipped section in default mode."""
    actual = run_pytest("examples.py", "-rs")

    assert "## Failures" in actual
    assert "test_edge_case FAILED" in actual

    assert "## Skipped" in actual
    assert "test_future_feature SKIPPED" in actual
    assert "Not implemented yet" in actual

    # XFAIL should still be hidden
    assert "test_known_bug XFAIL" not in actual
```

### 2. -rx Flag Shows XFail in Failures
**Test:** `test_default_with_rx_flag`
**Command:** `pytest examples.py -rx`

**Expected:**
- ✓ Failures section present
- ✓ XFAIL present in Failures section
- ✗ Skipped section NOT present

**Verification:**
```python
def test_default_with_rx_flag() -> None:
    """Test -rx shows xfailed tests in default mode."""
    actual = run_pytest("examples.py", "-rx")

    assert "## Failures" in actual
    assert "test_edge_case FAILED" in actual

    assert "test_known_bug XFAIL" in actual
    assert "Bug #123" in actual

    # Skipped should still be hidden
    assert "## Skipped" not in actual
```

### 3. -rsx Flag Shows Both Sections
**Test:** `test_default_with_rsx_flags`
**Command:** `pytest examples.py -rsx`

**Expected:**
- ✓ Failures section present
- ✓ XFAIL present in Failures section
- ✓ Skipped section present

**Verification:**
```python
def test_default_with_rsx_flags() -> None:
    """Test -rsx shows both skipped and xfailed in default mode."""
    actual = run_pytest("examples.py", "-rsx")

    assert "## Failures" in actual
    assert "test_edge_case FAILED" in actual
    assert "test_known_bug XFAIL" in actual

    assert "## Skipped" in actual
    assert "test_future_feature SKIPPED" in actual
```

## Implementation Location

Add tests to: `tests/test_output_expectations.py`

## Test Data Requirements

Uses existing `tests/examples.py` which contains:
- ✓ 1 failed test (`test_edge_case`)
- ✓ 1 skipped test (`test_future_feature`)
- ✓ 1 xfailed test (`test_known_bug`)
- ✓ 5 passed tests

## Success Criteria

- [ ] All 3 new test cases pass
- [ ] Tests run in <2 seconds
- [ ] No false positives (tests fail when behavior is wrong)
- [ ] All existing tests continue to pass (22 total → 25 total)

## Out of Scope

The following pytest `-r` flags are intentionally NOT supported (Phase 2):
- `-rf`: failed (always shown by default)
- `-rE`: error (always shown by default)
- `-rX`: xpassed (always shown by default)
- `-rp`: passed (use `-v` instead)
- `-ra`: all except passed
- `-rA`: all including passed

These may be added in future phases but are not part of current implementation.
