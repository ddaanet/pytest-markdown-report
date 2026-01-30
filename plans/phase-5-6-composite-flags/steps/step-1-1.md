# Cycle 1.1

**Plan**: `plans/phase-5-6-composite-flags/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.1: Implement `-ra` Flag [DEPENDS: 0.1]

**Objective**: Add `_should_show_section()` helper and refactor `_build_default_sections()` to support `-ra` (all except passes).

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `-ra` shows all sections except passes

**File:** `tests/test_output_expectations.py`

Add new test after `test_rw_flag_without_warnings_shows_no_section`:

```python
def test_ra_flag_shows_all_except_passes() -> None:
    """Test -ra shows all sections except regular passes."""
    actual = run_pytest("examples.py", "-ra")

    # Should have all sections except regular passes
    assert "## Failures" in actual, "Should show failures with -ra"
    assert "## Errors" in actual, "Should show errors with -ra"
    assert "## Skipped" in actual, "Should show skipped with -ra"
    assert "## Warnings" in actual, "Should show warnings with -ra"

    # Should NOT have Passes section (but may have "Passes (with output)")
    lines = actual.split("\n")
    sections = [line for line in lines if line.startswith("## ")]

    # Check no plain "## Passes" section (without "with output")
    has_plain_passes = any(s == "## Passes" for s in sections)
    assert not has_plain_passes, f"Should not show plain passes with -ra. Sections: {sections}"
```

**Expected failure:**
```
AssertionError: Should show skipped with -ra
```
Or similar, depending on which section is missing.

**Why it fails:** No composite flag parsing implemented yet. Current code only checks individual flags like `"s" in self.report_flags`, which won't match `report_flags = "a"`.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_ra_flag_shows_all_except_passes -v`
- Must fail with missing section assertion
- If passes, STOP - feature may already exist

---

### GREEN Phase

**Implementation:** Add `_should_show_section()` method and refactor `_build_default_sections()`.

**Note:** This cycle has 3 actions (add method, refactor method, update test) because all are needed for `-ra` flag to work. Cannot split into sub-cycles as the test requires all changes to pass.

**Changes:**

**File:** `src/pytest_markdown_report/plugin.py`

**Action 1:** Add helper method `_should_show_section()` after `__init__()` (after line 117)

**Behavior:**
- Accept single character flag (f, E, s, x, p, P, w)
- Return True if section should be shown based on self.report_flags
- Handle composite flags: "N" (suppress all), "A" (show all), "a" (show all except p/P)
- Fall back to checking if flag is in self.report_flags

**Implementation hints:**
- Check composite flags first (use early returns for clarity)
- Order: N (suppress) → A (all) → a (all except passes) → individual check
- For "a" flag: return True unless flag is "p" or "P"
- Tests will verify the exact conditional structure

**Action 2:** Refactor `_build_default_sections()` to use `_should_show_section()` helper (lines 284-306)

**Current behavior:**
- Direct flag checks like `"E" in self.report_flags` (line 293)
- Unconditional failure display (line 296)
- Individual inline checks for each section

**New behavior:**
- Replace all direct flag checks with `self._should_show_section(flag)` calls
- Gate every section on appropriate flag: E (errors), f (failures/xpassed), s (skipped), p (passes), P (passed with output), w (warnings)
- Maintain existing section order: errors → failures → skipped → passes → passed_output → warnings

**Implementation hints:**
- Extract `show_xfailed = self._should_show_section("x")` once at top (needed for failures section condition)
- Replace line 293: `show_errors = "E" in self.report_flags` → gate on `self._should_show_section("E")`
- Replace line 296: unconditional check → gate on `self._should_show_section("f")`
- Update docstring to mention composite flags (a, A, N)
- Tests will drive the exact conditional structure for each section

**Action 3:** Update `test_errors_separate_from_failures` expectation (line 169-170)

**Behavior change:**
- Old: Failures shown with `-rE` (unconditional failure display)
- New: `-rE` shows only errors (failures hidden when `f` not in flags)

**Update assertion:** Change from expecting failures to show → expecting failures to be hidden with `-rE`

**Implementation hint:** Invert the assertion on line 170 (change `in` to `not in` or adjust assertion logic)

**Sequencing notes:**
1. Implement `_should_show_section()` first (Action 1)
2. Refactor `_build_default_sections()` to use new helper (Action 2)
3. Update `test_errors_separate_from_failures` to match new behavior (Action 3)
4. Run tests after each change to catch integration issues early

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_ra_flag_shows_all_except_passes -v`
- Must pass

**Verify no regression:** Run `just test`
- All existing tests pass (including updated `test_errors_separate_from_failures`)

**Expected Outcome**: `-ra` flag working, test GREEN, no regressions

**Error Conditions**:
- RED doesn't fail → STOP (document which section already works)
- GREEN doesn't pass → Debug assertion/implementation mismatch
- Regression → STOP, report broken tests

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test fails during RED, passes during GREEN, no breaks

**Report Path**: plans/phase-5-6-composite-flags/reports/cycle-1-1-notes.md

---
