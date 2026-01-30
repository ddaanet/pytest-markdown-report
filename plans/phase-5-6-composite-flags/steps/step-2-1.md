# Cycle 2.1

**Plan**: `plans/phase-5-6-composite-flags/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.1: Test Verbose Overrides `-r` Flags [REGRESSION] [DEPENDS: 1.1]

**Objective**: Verify verbose mode ignores all `-r` flags including `-rN`.

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

### GREEN Immediately: Write test verifying verbose ignores -r flags

**Test:** `-v` shows all sections regardless of `-r` flags

**File:** `tests/test_output_expectations.py`

Add new test after `test_rN_flag_suppresses_all_sections`:

```python
def test_verbose_ignores_r_flags() -> None:
    """Test that -v shows all sections regardless of -r flags."""
    actual_v = run_pytest("examples.py", "-v")
    actual_vrf = run_pytest("examples.py", "-v", "-rf")
    actual_vrN = run_pytest("examples.py", "-v", "-rN")

    # All should have same sections (verbose overrides -r)
    for label, actual in [("plain -v", actual_v), ("-v -rf", actual_vrf), ("-v -rN", actual_vrN)]:
        assert "## Failures" in actual, f"{label} should show failures (verbose overrides)"
        assert "## Passes" in actual, f"{label} should show passes (verbose overrides)"
        assert "## Errors" in actual, f"{label} should show errors (verbose overrides)"

    # Specifically verify -v -rN still shows sections (verbose wins over -rN suppress)
    assert "## Failures" in actual_vrN, "Verbose should override -rN suppression"
    assert "## Passes" in actual_vrN, "Verbose should override -rN suppression"
```

**Expected GREEN immediately:**
Should pass immediately. Verbose mode uses `_build_verbose_sections()` which doesn't call `_should_show_section()`, so verbose already ignores `-r` flags.

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_verbose_ignores_r_flags -v`
- Should pass immediately
- If fails, STOP - verbose mode may be calling `_should_show_section()` incorrectly

**Expected Outcome**: Test GREEN immediately, confirms verbose override works

**Error Conditions**: Fails → STOP, check `_build_verbose_sections()` doesn't use `_should_show_section()`

**Validation**: Test passes ✓

**Success Criteria**: Regression test confirms verbose mode isolation

**Report Path**: plans/phase-5-6-composite-flags/reports/cycle-2-1-notes.md

---
