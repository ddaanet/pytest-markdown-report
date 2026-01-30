# Cycle 1.3

**Plan**: `plans/phase-5-6-composite-flags/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.3: Test `-rN` Flag [REGRESSION] [DEPENDS: 1.1]

**Objective**: Verify `-rN` suppresses all sections.

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

### GREEN Immediately: Write test for -rN flag

**Test:** `-rN` suppresses all sections (like quiet mode)

**File:** `tests/test_output_expectations.py`

Add new test after `test_rA_flag_shows_everything`:

```python
def test_rN_flag_suppresses_all_sections() -> None:
    """Test -rN suppresses all sections (like quiet mode)."""
    actual = run_pytest("examples.py", "-rN")

    # Should have summary
    assert "**Summary:**" in actual, "Should have summary line with -rN"

    # Should NOT have any section headers
    assert "## Failures" not in actual, "Should not show failures with -rN"
    assert "## Errors" not in actual, "Should not show errors with -rN"
    assert "## Skipped" not in actual, "Should not show skipped with -rN"
    assert "## Passes" not in actual, "Should not show passes with -rN"

    # Should be minimal output (summary + maybe rerun command)
    lines = [line for line in actual.split("\n") if line.strip()]
    assert len(lines) <= 3, f"Should have minimal output with -rN. Got {len(lines)} lines: {lines}"
```

**Expected GREEN immediately:**
Should pass immediately since `_should_show_section()` already handles `"N"` flag (returns `False` unconditionally).

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_rN_flag_suppresses_all_sections -v`
- Should pass immediately
- If fails, STOP - implementation from 1.1 incomplete

**Expected Outcome**: Test GREEN immediately, confirms `-rN` implementation complete

**Error Conditions**: Fails → STOP, debug `_should_show_section()` logic

**Validation**: Test passes ✓

**Success Criteria**: Regression test confirms `-rN` works

**Report Path**: plans/phase-5-6-composite-flags/reports/cycle-1-3-notes.md

---
