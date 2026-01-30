# Cycle 2.2

**Plan**: `plans/phase-5-6-composite-flags/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.2: Test Flag Combinations [REGRESSION] [DEPENDS: 1.1]

**Objective**: Verify multiple individual `-r` flags combine correctly.

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

### GREEN Immediately: Write comprehensive integration test

**Test:** Multiple `-r` flags combine correctly

**File:** `tests/test_output_expectations.py`

Add new test after `test_verbose_ignores_r_flags`:

```python
def test_multiple_flags_combine_correctly() -> None:
    """Test that multiple -r flags combine correctly."""
    # -rsx should show skipped and xfailed
    actual_rsx = run_pytest("examples.py", "-rsx")
    assert "## Skipped" in actual_rsx, "-rsx should show skipped"
    assert "test_known_bug XFAIL" in actual_rsx, "-rsx should show xfailed"

    # -rEf should show errors and failures
    actual_rEf = run_pytest("examples.py", "-rEf")
    assert "## Errors" in actual_rEf, "-rEf should show errors"
    assert "## Failures" in actual_rEf, "-rEf should show failures"

    # -rpP should show both types of passes
    actual_rpP = run_pytest("examples.py", "-rpP")
    passes_sections = [line for line in actual_rpP.split("\n") if "## Passes" in line]
    # Should have at least one passes section
    assert len(passes_sections) >= 1, f"-rpP should show passes. Got sections: {passes_sections}"
```

**Expected GREEN immediately:**
Should pass immediately if previous implementations were correct. The `_should_show_section()` method checks `flag in self.report_flags`, which handles multi-character strings like `"sx"`, `"Ef"`, `"rpP"`.

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_multiple_flags_combine_correctly -v`
- Should pass (integration/regression test)
- If fails, STOP - debug flag combination logic

**Expected Outcome**: Test GREEN immediately, confirms flag combinations work

**Error Conditions**: Fails → STOP, debug `flag in self.report_flags` behavior with multi-char strings

**Validation**: Test passes ✓

**Success Criteria**: Regression test confirms all flag combinations work

**Report Path**: plans/phase-5-6-composite-flags/reports/cycle-2-2-notes.md

---
