# Cycle 1.2

**Plan**: `plans/phase-5-6-composite-flags/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.2: Test `-rA` Flag [REGRESSION] [DEPENDS: 1.1]

**Objective**: Verify `-rA` shows everything including passes.

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

### GREEN Immediately: Write test for -rA flag

**Test:** `-rA` shows all sections including passes

**File:** `tests/test_output_expectations.py`

Add new test after `test_ra_flag_shows_all_except_passes`:

```python
def test_rA_flag_shows_everything() -> None:
    """Test -rA shows all sections including passes."""
    actual = run_pytest("examples.py", "-rA")

    # Should have all sections
    assert "## Failures" in actual, "Should show failures with -rA"
    assert "## Errors" in actual, "Should show errors with -rA"
    assert "## Skipped" in actual, "Should show skipped with -rA"
    assert "## Passes" in actual, "Should show passes with -rA"
    assert "## Warnings" in actual, "Should show warnings with -rA"

    # Verify Passes section exists (plain passes, not just with output)
    lines = actual.split("\n")
    sections = [line for line in lines if line.startswith("## ")]
    has_passes = any("Passes" in s for s in sections)
    assert has_passes, f"Should show passes section with -rA. Sections: {sections}"
```

**Expected GREEN immediately:**
Should pass immediately since `_should_show_section()` already handles `"A"` flag (returns `True` unconditionally).

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_rA_flag_shows_everything -v`
- Should pass immediately
- If fails, STOP - implementation from 1.1 incomplete

**Expected Outcome**: Test GREEN immediately, confirms `-rA` implementation complete

**Error Conditions**: Fails → STOP, debug `_should_show_section()` logic

**Validation**: Test passes ✓

**Success Criteria**: Regression test confirms `-rA` works

**Report Path**: plans/phase-5-6-composite-flags/reports/cycle-1-2-notes.md

---
