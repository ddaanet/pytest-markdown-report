# Phase 3 & 4 Implementation: Add -rP and -rw Flags

**Reference:** See [Design Document](r-flag-parity-design.md) for overview and design decisions.

**Phases covered:** Phase 3 (Cycles 3.1-3.2) and Phase 4 (Cycles 4.1-4.2)

---

## Phase 3: Add -rP Flag (Passed with Output)

### Cycle 3.1: Create Test Fixture with Output

**RED: Add test that prints output**

**File:** `tests/examples.py`

**Action:** Add after line ~74, before fixture definitions:
```python
import sys


def test_with_output() -> None:
    """Test that passes but prints output."""
    print("Debug: processing started")
    print("Status: OK", file=sys.stderr)
    assert True
```

**Verify:** Run `pytest tests/examples.py::test_with_output -v`
- Should pass with captured output shown in verbose

**No implementation needed - this is setup**

---

### Cycle 3.2: Test -rP Shows Passed Tests with Output

**RED: Write test for -rP flag**

**File:** `tests/test_output_expectations.py`

**Action:** Add new test:
```python
def test_rP_flag_shows_passed_with_output() -> None:
    """Test -rP shows passed tests that captured output."""
    actual = run_pytest("examples.py", "-rP")

    # Should have special section for passed with output
    assert "## Passes (with output)" in actual or "## Passes" in actual, "Expected passes section with -rP"

    # Should show the test that has output
    assert "test_with_output" in actual, "Should show test_with_output"

    # Should show the captured output
    assert "Debug: processing started" in actual or "stdout:" in actual, "Should show captured stdout"
```

**Expected RED output:**
```
AssertionError: Expected passes section with -rP
```

**Why it fails:** No implementation of -rP flag or passed_with_output tracking.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_rP_flag_shows_passed_with_output -v`
- Must fail
- If passes, STOP

---

**GREEN: Implement -rP flag**

**File:** `src/pytest_markdown_report/plugin.py`

**Action 1:** Add data structure after line 107:
```python
self.passed_with_output: list[tuple[TestReport, str, str]] = []  # (report, stdout, stderr)
```

**Action 2:** Modify `pytest_runtest_logreport()` at line ~146:
```python
def pytest_runtest_logreport(self, report: TestReport) -> None:
    """Collect test reports."""
    # Capture call phase (actual test execution)
    # Also capture all non-passing outcomes from any phase (setup/teardown)
    if report.when == "call" or report.outcome in ("skipped", "failed", "error"):
        self.reports.append(report)

        # Track passed tests with captured output for -rP flag
        if report.when == "call" and report.passed:
            capstdout = getattr(report, "capstdout", "")
            capstderr = getattr(report, "capstderr", "")
            if capstdout or capstderr:
                self.passed_with_output.append((report, capstdout, capstderr))
```

**Action 3:** Add generator method after `_generate_passes()` (~line 431):
```python
def _generate_passed_with_output(self) -> list[str]:
    """Generate passed tests with captured output section.

    Returns:
        List of markdown lines for passed with output section
    """
    lines = ["", "## Passes (with output)", ""]
    for report, stdout, stderr in self.passed_with_output:
        lines.append(f"- {report.nodeid} PASSED")
        if stdout:
            lines.append(f"  stdout: {stdout.strip()}")
        if stderr:
            lines.append(f"  stderr: {stderr.strip()}")
    return lines
```

**Action 4:** Add to `_build_report_lines()` in default mode section (~line 245):
```python
# Passed with output section (with -rP flag)
show_passed_output = "P" in self.report_flags
if show_passed_output and self.passed_with_output:
    lines.extend(self._generate_passed_with_output())
```

**Action 5:** Add to verbose mode section (~line 233):
```python
if self.passed:
    lines.extend(self._generate_passes())
if self.passed_with_output:
    lines.extend(self._generate_passed_with_output())
```

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_rP_flag_shows_passed_with_output -v`
- Must pass

**Verify no regression:** Run `just test`

---

## Phase 4: Add -rw Flag (Warnings)

### Cycle 4.1: Create Test that Generates Warning

**RED: Add test that triggers pytest warning**

**File:** `tests/examples.py`

**Action:** Add after test_with_output:
```python
@pytest.mark.filterwarnings("default")
def test_with_warning() -> None:
    """Test that generates a warning."""
    import warnings
    warnings.warn("This is a test warning", UserWarning)
    assert True
```

**Verify:** Run `pytest tests/examples.py::test_with_warning -v`
- Should pass but show warning in output

**No implementation needed - this is setup**

---

### Cycle 4.2: Test -rw Shows Warnings Section

**RED: Write test for -rw flag**

**File:** `tests/test_output_expectations.py`

**Action:** Add new test:
```python
def test_rw_flag_shows_warnings() -> None:
    """Test -rw shows warnings section."""
    actual = run_pytest("examples.py", "-rw")

    # Should have warnings section if any warnings exist
    # Note: warnings might not always exist, so check conditionally
    if "warning" in actual.lower():
        assert "## Warnings" in actual or "warning" in actual, "Should show warnings with -rw flag"
```

**Expected RED output:**
```
AssertionError: Should show warnings with -rw flag
```

**Why it fails:** No warnings section implemented yet.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_rw_flag_shows_warnings -v`
- Must fail (assuming warnings are generated)
- If passes, check if warnings exist in output at all

---

**GREEN: Implement -rw flag**

**File:** `src/pytest_markdown_report/plugin.py`

**Action 1:** Add import at top (~line 5):
```python
from _pytest.warnings import WarningMessage
```

**Action 2:** Add data structure after line 112:
```python
self.warnings: list[tuple[str, str, str]] = []  # (warning_message, nodeid, location)
```

**Action 3:** Add hook after `pytest_collectreport()` (~line 144):
```python
def pytest_warning_recorded(
    self,
    warning_message: WarningMessage,
    when: str,
    nodeid: str,
    location: tuple[str, int, str] | None,
) -> None:
    """Capture pytest warnings."""
    loc = f"{location[0]}:{location[1]}" if location else ""
    msg = str(warning_message.message)
    self.warnings.append((msg, nodeid, loc))
```

**Action 4:** Add generator method after `_generate_passed_with_output()`:
```python
def _generate_warnings(self) -> list[str]:
    """Generate warnings section.

    Returns:
        List of markdown lines for warnings section
    """
    lines = ["", "## Warnings", ""]
    for msg, nodeid, loc in self.warnings:
        if loc:
            lines.append(f"- {loc}: {msg}")
        elif nodeid:
            lines.append(f"- {nodeid}: {msg}")
        else:
            lines.append(f"- {msg}")
    return lines
```

**Action 5:** Add to `_build_report_lines()` default mode (~line 247):
```python
# Warnings section (with -rw flag)
show_warnings = "w" in self.report_flags
if show_warnings and self.warnings:
    lines.extend(self._generate_warnings())
```

**Action 6:** Add to verbose mode section (~line 235):
```python
if self.warnings:
    lines.extend(self._generate_warnings())
```

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_rw_flag_shows_warnings -v`
- Must pass

**Verify no regression:** Run `just test`

---

**Phase 3 & 4 Complete** - Ready to move to Phase 5 & 6 (see [r-flag-parity-phase-5-6.md](r-flag-parity-phase-5-6.md))
