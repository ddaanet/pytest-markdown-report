# Phase 1 & 2 Implementation: Separate Errors & Add -rp Flag

**Reference:** See [Design Document](r-flag-parity-design.md) for overview and design decisions.

**Phases covered:** Phase 1 (Cycles 1.1-1.5) and Phase 2 (Cycles 2.1-2.2)

---

## Phase 1: Separate Errors from Failures

### Cycle 1.1: Add Setup Error Test Fixture

**RED: Create test fixture that will be used in later tests**

**File:** `tests/examples.py`

**Action:** Add after line 74:
```python
@pytest.fixture
def broken_fixture() -> None:
    """Fixture that fails during setup."""
    msg = "Fixture setup failed"
    raise RuntimeError(msg)


def test_setup_error(broken_fixture: None) -> None:
    """Test with setup error."""
    assert True
```

**Verify:** Run `pytest tests/examples.py::test_setup_error`
- Should see "ERROR in setup" in current output
- This fixture is for use in upcoming tests

**No implementation needed - this is setup for next cycles**

---

### Cycle 1.2: Test That Errors Appear in Separate Section

**RED: Write test asserting ## Errors section exists**

**File:** `tests/test_output_expectations.py`

**Action:** Add after line 153:
```python
def test_errors_separate_from_failures() -> None:
    """Test that setup/teardown errors appear in separate ## Errors section."""
    actual = run_pytest("examples.py", "-rE")

    # Should have separate Errors section
    assert "## Errors" in actual, "Expected '## Errors' section for setup/teardown errors"

    # Setup error should appear in Errors section
    assert "test_setup_error ERROR in setup" in actual, "Expected setup error in Errors section"

    # Regular failures should NOT appear (only -rE flag)
    assert "test_edge_case FAILED" not in actual, "Should not show failures with -rE flag"
```

**Expected RED output:**
```
AssertionError: Expected '## Errors' section for setup/teardown errors
```

**Why it fails:** Current implementation puts setup errors in `## Failures` section, not separate `## Errors` section.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_errors_separate_from_failures -v`
- Must fail with "Expected '## Errors' section" message
- If test passes, STOP - implementation already exists

---

**GREEN: Create separate errors bucket**

**File:** `src/pytest_markdown_report/plugin.py`

**Action 1:** Add after line 111:
```python
self.errors: list[TestReport] = []  # Setup/teardown errors (non-collection)
```

**Action 2:** Modify `_categorize_single_report()` at line 208 to split errors:
```python
elif report.failed:
    # Separate call-phase failures from setup/teardown errors
    if report.when == "call":
        self.failed.append(report)
    else:
        self.errors.append(report)
```

**Action 3:** Add `_generate_errors()` method after line 357:
```python
def _generate_errors(self) -> list[str]:
    """Generate errors section (setup/teardown failures).

    Returns:
        List of markdown lines for errors section
    """
    lines = ["", "## Errors", ""]
    for report in self.errors:
        lines.extend(self._format_failure(report, symbol="ERROR"))
    return lines
```

**Action 4:** Update `_build_report_lines()` at line 236 to show errors when `-rE`:
```python
# Default mode: show failures based on -r flags
show_xfailed = "x" in self.report_flags
show_errors = "E" in self.report_flags

if show_errors and self.errors:
    lines.extend(self._generate_errors())

if self.failed or self.xpassed or (show_xfailed and self.xfailed):
    lines.extend(self._generate_failures(show_xfailed=show_xfailed))
```

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_errors_separate_from_failures -v`
- Must pass
- If fails, debug before continuing

**Verify no regression:** Run `just test`
- All existing tests must still pass
- If any fail, fix before continuing

---

### Cycle 1.3: Test Default Mode Shows Both Errors and Failures

**RED: Write test for default behavior (no -r flags)**

**File:** `tests/test_output_expectations.py`

**Action:** Add after previous test:
```python
def test_default_shows_errors_and_failures() -> None:
    """Test that default mode (no -r flags) shows both errors and failures."""
    actual = run_pytest("examples.py")

    # Default should show both sections
    assert "## Errors" in actual, "Default mode should show errors"
    assert "## Failures" in actual, "Default mode should show failures"

    # Both error and failure should appear
    assert "test_setup_error ERROR in setup" in actual
    assert "test_edge_case FAILED" in actual
```

**Expected RED output:**
```
AssertionError: Default mode should show errors
```

**Why it fails:** Default mode (no flags) doesn't check for 'E' in report_flags, so errors aren't shown.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_default_shows_errors_and_failures -v`
- Must fail
- If passes, STOP - check implementation

---

**GREEN: Make errors show by default**

**File:** `src/pytest_markdown_report/plugin.py`

**Action:** Modify the condition at line ~240 (from previous cycle):
```python
# Default mode: show failures and errors by default, respect -r flags for others
show_xfailed = "x" in self.report_flags
show_errors = "E" in self.report_flags or not self.report_flags  # Show by default

if show_errors and self.errors:
    lines.extend(self._generate_errors())
```

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_default_shows_errors_and_failures -v`
- Must pass

**Verify no regression:** Run `just test`

---

### Cycle 1.4: Test -rf Hides Errors (Only Failures)

**RED: Write test for -rf flag (failures only)**

**File:** `tests/test_output_expectations.py`

**Action:** Add after previous test:
```python
def test_rf_flag_hides_errors() -> None:
    """Test -rf shows only failures, not errors."""
    actual = run_pytest("examples.py", "-rf")

    # Should have failures
    assert "## Failures" in actual, "Should show failures with -rf"
    assert "test_edge_case FAILED" in actual

    # Should NOT have errors
    assert "## Errors" not in actual, "Should not show errors with -rf flag"
    assert "test_setup_error" not in actual
```

**Expected RED output:**
```
AssertionError: Should not show errors with -rf flag
```

**Why it fails:** Current implementation shows errors by default when no -r flags. Need to implement logic where explicit flags override default.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_rf_flag_hides_errors -v`
- Must fail
- If passes, STOP

---

**GREEN: Implement flag parsing to respect explicit flags**

**File:** `src/pytest_markdown_report/plugin.py`

**Action:** Replace the show_errors logic at line ~240:
```python
# Default mode: respect -r flags
# If no flags: show failures and errors by default (fE)
# If explicit flags: only show what's requested
has_explicit_flags = bool(self.report_flags)

if has_explicit_flags:
    show_errors = "E" in self.report_flags
    show_failures = "f" in self.report_flags or self.failed or self.xpassed
else:
    # Default: show both errors and failures
    show_errors = True
    show_failures = True

show_xfailed = "x" in self.report_flags

if show_errors and self.errors:
    lines.extend(self._generate_errors())

if show_failures and (self.failed or self.xpassed or (show_xfailed and self.xfailed)):
    lines.extend(self._generate_failures(show_xfailed=show_xfailed))
```

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_rf_flag_hides_errors -v`
- Must pass

**Verify no regression:** Run `just test`

---

### Cycle 1.5: Update Summary to Include Error Count

**RED: Write test for summary with errors**

**File:** `tests/test_output_expectations.py`

**Action:** Add after previous test:
```python
def test_summary_includes_error_count() -> None:
    """Test that summary line includes error count."""
    actual = run_pytest("examples.py")

    # Summary should mention errors
    assert "error" in actual.lower(), "Summary should include error count"

    # Should have format like "X errors" in summary
    import re
    summary_line = [line for line in actual.split("\n") if "**Summary:**" in line][0]
    assert re.search(r"\d+ error", summary_line), f"Summary should include 'N error(s)': {summary_line}"
```

**Expected RED output:**
```
AssertionError: Summary should include error count
```

**Why it fails:** Summary generation doesn't include error count yet.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_summary_includes_error_count -v`
- Must fail
- If passes, STOP

---

**GREEN: Add error count to summary**

**File:** `src/pytest_markdown_report/plugin.py`

**Action 1:** Update `_generate_summary()` at line ~290:

Find the line:
```python
total = len(self.passed) + len(self.failed) + len(self.skipped) + len(self.xfailed) + len(self.xpassed)
```

Replace with:
```python
total = len(self.passed) + len(self.failed) + len(self.errors) + len(self.skipped) + len(self.xfailed) + len(self.xpassed)
```

Find the parts section (~line 300):
```python
if self.failed:
    parts.append(f"{len(self.failed)} failed")
```

Add after it:
```python
if self.errors:
    parts.append(f"{len(self.errors)} errors")
```

**Action 2:** Update `_generate_quiet()` similarly at line ~315.

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_summary_includes_error_count -v`
- Must pass

**Verify no regression:** Run `just test`

---

## Phase 2: Add -rp Flag (Passes in Default Mode)

### Cycle 2.1: Test -rp Shows Passes in Default Mode

**RED: Write test for -rp flag**

**File:** `tests/test_output_expectations.py`

**Action:** Add new test:
```python
def test_rp_flag_shows_passes() -> None:
    """Test -rp shows passes in default mode (not just verbose)."""
    actual = run_pytest("examples.py", "-rp")

    # Should have failures (default)
    assert "## Failures" in actual

    # Should have passes section (from -rp flag)
    assert "## Passes" in actual, "Expected '## Passes' section with -rp flag"

    # Should list passing tests
    assert "test_simple" in actual, "Should show passing test names"
```

**Expected RED output:**
```
AssertionError: Expected '## Passes' section with -rp flag
```

**Why it fails:** Current implementation only shows passes in verbose mode, not based on -rp flag.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_rp_flag_shows_passes -v`
- Must fail
- If passes, STOP

---

**GREEN: Add -rp flag support**

**File:** `src/pytest_markdown_report/plugin.py`

**Action:** Modify `_build_report_lines()` at line ~240, add after skipped section:

```python
# Passes section (with -rp flag in default mode, or verbose mode)
show_passes = "p" in self.report_flags
if show_passes and self.passed:
    lines.extend(self._generate_passes())
```

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_rp_flag_shows_passes -v`
- Must pass

**Verify no regression:** Run `just test`

---

### Cycle 2.2: Test -rp Doesn't Show in Verbose (Verbose Shows All)

**RED: Verify verbose behavior unchanged**

**File:** `tests/test_output_expectations.py`

**Action:** Add test:
```python
def test_verbose_shows_passes_regardless_of_rp() -> None:
    """Test that -v shows passes even without -rp flag."""
    actual_v = run_pytest("examples.py", "-v")
    actual_v_without_rp = run_pytest("examples.py", "-v")

    # Both should have passes (verbose always shows)
    assert "## Passes" in actual_v
    assert "## Passes" in actual_v_without_rp

    # Verify they're the same
    assert actual_v == actual_v_without_rp
```

**Expected RED output:**
This should actually pass (GREEN) immediately since verbose mode already shows passes.

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_verbose_shows_passes_regardless_of_rp -v`
- Should pass immediately (this is a regression test, not driving new code)
- This confirms verbose behavior is unchanged

---

**Phase 1 & 2 Complete** - Ready to move to Phase 3 & 4 (see [r-flag-parity-phase-3-4.md](r-flag-parity-phase-3-4.md))
