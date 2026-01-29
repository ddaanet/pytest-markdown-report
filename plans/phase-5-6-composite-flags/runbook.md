---
name: phase-5-6-composite-flags
type: tdd
model: haiku
---

# Phase 5-6: Composite Flags TDD Runbook

**Context**: Implement `-ra`, `-rA`, `-rN` composite flags and validate verbose override + flag combinations for pytest-markdown-report.

**Design**: plans/phase-5-6-design.md

**Status**: Draft

**Created**: 2026-01-29

## Weak Orchestrator Metadata

**Total Steps**: 6 (1 pre-implementation spike + 5 TDD cycles)

**Execution Model**: All steps: Haiku (TDD execution)

**Step Dependencies**: Sequential (0.1 → 1.1 → 1.2 → 1.3 → 2.1 → 2.2)

**Error Escalation**: Haiku → User on stop conditions/regression

**Report Locations**: plans/phase-5-6-composite-flags/reports/

**Success Criteria**: All cycles GREEN, no regressions, composite flags working

**Prerequisites**:
- Phases 1-4 complete (errors/failures separate, `-rp`, `-rP`, `-rw` flags implemented)
- Test suite passing

## Common Context

**Key Design Decisions:**

1. **pytest default `reportchars` is `"fE"`, not empty string**
   - Default behavior: show failures + errors (from `"fE"`)
   - xpassed follow `f` flag (rendered in Failures section)
   - No empty-string special case in `_should_show_section()`

2. **Composite flag expansion done by plugin, not pytest**
   - `-ra` → stored as `"a"`, plugin expands to "all except passes"
   - `-rA` → stored as `"A"`, plugin expands to "everything"
   - `-rN` → stored as `"N"`, plugin suppresses all sections

3. **`_should_show_section()` simplified logic**
   - No `X` flag special case (xpassed gate on `f`)
   - Check composite flags first (`N`, `A`, `a`)
   - Fall back to `flag in self.report_flags`

4. **Breaking change: `-rE` now hides failures**
   - Old: failures always shown (unconditional)
   - New: failures gated on `f` flag
   - Test `test_errors_separate_from_failures` expects old behavior, must be updated

**TDD Protocol:**

Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Project Paths:**
- Implementation: `src/pytest_markdown_report/plugin.py`
- Tests: `tests/test_output_expectations.py`
- Test fixtures: `tests/examples.py`

**Conventions:**
- Use Read/Write/Edit/Grep/Glob tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Write notes to plans/phase-5-6-composite-flags/reports/cycle-{X}-{Y}-notes.md
- Run `just test` for regression verification

**Stop Conditions (all cycles):**

STOP IMMEDIATELY if:
- RED phase test passes (expected failure)
- RED phase failure message doesn't match expected
- GREEN phase tests don't pass after implementation
- Any phase existing tests break (regression)

Actions when stopped:
1. Document in reports/cycle-{X}-{Y}-notes.md
2. Test passes unexpectedly → Investigate if feature exists, mark `[REGRESSION]`
3. Regression → STOP, report broken tests to user
4. Scope unclear → STOP, document ambiguity

**Dependencies:**

All cycles sequential: 0.1 → 1.1 → 1.2 → 1.3 → 2.1 → 2.2

---

## Cycle 0.1: Pre-Implementation Spike

**Objective**: Verify current behavior with composite flags to identify RED vs REGRESSION cycles.

**Script Evaluation**: Direct execution (bash verification)

**Execution Model**: Haiku

**Implementation:**

Run these commands to verify current behavior:

```bash
cd /Users/david/code/pytest-md

# Test -ra behavior
echo "=== Testing -ra ==="
pytest tests/examples.py -ra 2>&1 | head -30

# Test -rA behavior
echo "=== Testing -rA ==="
pytest tests/examples.py -rA 2>&1 | head -30

# Test -rN behavior
echo "=== Testing -rN ==="
pytest tests/examples.py -rN 2>&1 | head -30

# Test verbose with -rN
echo "=== Testing -v -rN ==="
pytest tests/examples.py -v -rN 2>&1 | head -30
```

**Document findings** in reports/spike-results.md:
- Which sections appear with each flag
- Whether any cycles might be `[REGRESSION]`
- Current behavior of `test_errors_separate_from_failures` (line 170 expectation)

**Expected Outcome**: Clear understanding of current state, cycle classifications

**Validation**: Findings documented, ready to proceed with TDD

**Success Criteria**: Know which cycles are RED vs REGRESSION

**Report Path**: plans/phase-5-6-composite-flags/reports/spike-results.md

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

## Design Decisions

**1. pytest default `reportchars` behavior**
- Choice: Handle default `"fE"` value correctly, no empty-string special case
- Rationale: pytest always sets `reportchars`, never leaves it empty. Measured via `pytest.Config.fromdictargs({}, [])` → `"fE"`.

**2. Composite flag expansion**
- Choice: Plugin expands composite flags (`a`, `A`, `N`), not pytest
- Rationale: pytest stores raw character. Verified via `pytest.Config.fromdictargs({}, ['-ra'])` → `"a"`, not `"fEsxXw"`.

**3. xpassed gating**
- Choice: Gate on `f` flag, not separate `X` flag
- Rationale: xpassed render in Failures section. Separating gate adds complexity. Default `"fE"` includes `f`, so xpassed still show by default. Simpler implementation.

**4. Breaking change: `-rE` behavior**
- Choice: `-rE` hides failures (shows only errors)
- Rationale: Matches pytest semantics (explicit flags mean "show only these"). No existing tests check `-rE` with failures expectation except `test_errors_separate_from_failures`, which is updated in cycle 1.1.

**5. Verbose mode isolation**
- Choice: Verbose uses separate `_build_verbose_sections()`, doesn't call `_should_show_section()`
- Rationale: Verbose always shows all sections regardless of `-r` flags. Already implemented correctly, no changes needed.

---

## Dependencies

**Before**: Phases 1-4 complete (separate errors/failures, `-rp`, `-rP`, `-rw` implemented)

**After**: Composite flags implemented, flag combinations validated, verbose override confirmed, ready for Phase 7 (documentation)

---

## Next Steps

After all cycles GREEN:

1. Run `just test` to verify full test suite passes
2. Review implementation for refactoring opportunities (optional)
3. Commit changes using `/commit` skill
4. Proceed to Phase 7 (documentation updates) if needed
