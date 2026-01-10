# Phase 5 & 6 Implementation: Composite Flags & Edge Cases

**Reference:** See [Design Document](r-flag-parity-design.md) for overview and design decisions.

**Phases covered:** Phase 5 (Cycles 5.1-5.3) and Phase 6 (Cycles 6.1-6.2)

---

## Phase 5: Add Composite Flags (-ra, -rA, -rN)

### Cycle 5.1: Test -ra Shows All Except Passes

**RED: Write test for -ra flag**

**File:** `tests/test_output_expectations.py`

**Action:** Add new test:
```python
def test_ra_flag_shows_all_except_passes() -> None:
    """Test -ra shows all sections except regular passes."""
    actual = run_pytest("examples.py", "-ra")

    # Should have all sections except regular passes
    assert "## Failures" in actual, "Should show failures"
    assert "## Errors" in actual, "Should show errors"
    assert "## Skipped" in actual, "Should show skipped"

    # Should NOT have regular passes section (unless it's passes with output)
    # Note: This is tricky - we want xfail/xpass but not regular passes
    # For now, check that we have failure-related content
    lines = actual.split("\n")
    sections = [line for line in lines if line.startswith("## ")]

    # Should not have plain "## Passes" (without "with output")
    has_plain_passes = any("## Passes" == s for s in sections)
    assert not has_plain_passes, f"Should not show plain passes section with -ra. Sections: {sections}"
```

**Expected RED output:**
```
AssertionError: Should show skipped
```
Or similar, depending on which section is missing.

**Why it fails:** No composite flag parsing implemented yet.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_ra_flag_shows_all_except_passes -v`
- Must fail
- If passes, STOP

---

**GREEN: Implement composite flag parsing**

**File:** `src/pytest_markdown_report/plugin.py`

**Action 1:** Add helper method after `__init__()` (~line 117):
```python
def _should_show_section(self, flag: str) -> bool:
    """Determine if a section should be shown based on -r flags.

    Args:
        flag: Single character flag (f, E, s, x, p, P, w)

    Returns:
        True if section should be shown
    """
    # No flags: default to fEX (failures, errors, xpassed)
    if not self.report_flags:
        return flag in "fEX"

    # Reset flag: suppress all
    if "N" in self.report_flags:
        return False

    # Composite shortcuts
    if "A" in self.report_flags:  # All including passes
        return True
    if "a" in self.report_flags:  # All except passes
        return flag in "fEsxXw"

    # Individual flags
    return flag in self.report_flags
```

**Action 2:** Replace the flag logic in `_build_report_lines()` default mode section (~line 240):

Replace:
```python
has_explicit_flags = bool(self.report_flags)
if has_explicit_flags:
    show_errors = "E" in self.report_flags
    show_failures = "f" in self.report_flags or self.failed or self.xpassed
else:
    show_errors = True
    show_failures = True
show_xfailed = "x" in self.report_flags
```

With:
```python
show_errors = self._should_show_section("E")
show_failures = self._should_show_section("f")
show_xfailed = self._should_show_section("x")
show_skipped = self._should_show_section("s")
show_passes = self._should_show_section("p")
show_passed_output = self._should_show_section("P")
show_warnings = self._should_show_section("w")
```

**Action 3:** Update all the section conditions to use these variables:
```python
if show_errors and self.errors:
    lines.extend(self._generate_errors())

if show_failures and (self.failed or self.xpassed or (show_xfailed and self.xfailed)):
    lines.extend(self._generate_failures(show_xfailed=show_xfailed))

if show_skipped and self.skipped:
    lines.extend(self._generate_skipped())

if show_warnings and self.warnings:
    lines.extend(self._generate_warnings())

if show_passes and self.passed:
    lines.extend(self._generate_passes())

if show_passed_output and self.passed_with_output:
    lines.extend(self._generate_passed_with_output())
```

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_ra_flag_shows_all_except_passes -v`
- Must pass

**Verify no regression:** Run `just test`

---

### Cycle 5.2: Test -rA Shows Everything

**RED: Write test for -rA flag**

**File:** `tests/test_output_expectations.py`

**Action:** Add new test:
```python
def test_rA_flag_shows_everything() -> None:
    """Test -rA shows all sections including passes."""
    actual = run_pytest("examples.py", "-rA")

    # Should have all sections
    assert "## Failures" in actual, "Should show failures"
    assert "## Errors" in actual, "Should show errors"
    assert "## Skipped" in actual, "Should show skipped"
    assert "## Passes" in actual, "Should show passes with -rA"

    # Verify passes section exists
    lines = actual.split("\n")
    sections = [line for line in lines if line.startswith("## ")]
    has_passes = any("Passes" in s for s in sections)
    assert has_passes, f"Should show passes section with -rA. Sections: {sections}"
```

**Expected RED output:**
Should actually pass (GREEN) immediately since `_should_show_section()` already handles "A" flag.

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_rA_flag_shows_everything -v`
- Should pass immediately
- This confirms -rA implementation is complete

---

### Cycle 5.3: Test -rN Suppresses All Sections

**RED: Write test for -rN flag**

**File:** `tests/test_output_expectations.py`

**Action:** Add new test:
```python
def test_rN_flag_suppresses_all_sections() -> None:
    """Test -rN suppresses all sections (like quiet mode)."""
    actual = run_pytest("examples.py", "-rN")

    # Should have summary
    assert "**Summary:**" in actual, "Should have summary line"

    # Should NOT have any section headers
    assert "## Failures" not in actual, "Should not show failures section"
    assert "## Errors" not in actual, "Should not show errors section"
    assert "## Skipped" not in actual, "Should not show skipped section"
    assert "## Passes" not in actual, "Should not show passes section"

    # Should be similar to quiet mode output
    lines = [line for line in actual.split("\n") if line.strip()]
    assert len(lines) <= 3, f"Should have minimal output (summary + maybe rerun). Got {len(lines)} lines: {lines}"
```

**Expected RED output:**
Should actually pass (GREEN) immediately since `_should_show_section()` already handles "N" flag.

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_rN_flag_suppresses_all_sections -v`
- Should pass immediately
- This confirms -rN implementation is complete

---

## Phase 6: Edge Cases and Integration

### Cycle 6.1: Test Verbose Overrides -r Flags

**RED: Write test verifying verbose ignores -r flags**

**File:** `tests/test_output_expectations.py`

**Action:** Add new test:
```python
def test_verbose_ignores_r_flags() -> None:
    """Test that -v shows all sections regardless of -r flags."""
    actual_v = run_pytest("examples.py", "-v")
    actual_vrf = run_pytest("examples.py", "-v", "-rf")
    actual_vrN = run_pytest("examples.py", "-v", "-rN")

    # All should have same sections (verbose overrides -r)
    for actual in [actual_v, actual_vrf, actual_vrN]:
        assert "## Failures" in actual, "Verbose should always show failures"
        assert "## Passes" in actual, "Verbose should always show passes"

    # Verify -v with -rN still shows sections (verbose wins)
    assert "## Failures" in actual_vrN, "Verbose should override -rN"
```

**Expected RED output:**
```
AssertionError: Verbose should override -rN
```

**Why it fails:** Verbose mode doesn't currently call `_should_show_section()`, so it might not override -rN properly.

**Verify RED:** Run `pytest tests/test_output_expectations.py::test_verbose_ignores_r_flags -v`
- Must fail
- If passes, check that verbose mode correctly overrides all flags

---

**GREEN: Ensure verbose mode ignores -r flags**

**File:** `src/pytest_markdown_report/plugin.py`

**Action:** Verify verbose mode section in `_build_report_lines()` (~line 228):

Ensure verbose mode does NOT call `_should_show_section()`:
```python
if self.verbosity > 0:
    # Verbose mode: show all sections, ignore -r flags
    if self.failed or self.xfailed or self.xpassed:
        lines.extend(self._generate_failures())
    if self.errors:
        lines.extend(self._generate_errors())
    if self.skipped:
        lines.extend(self._generate_skipped())
    if self.warnings:
        lines.extend(self._generate_warnings())
    if self.passed:
        lines.extend(self._generate_passes())
    if self.passed_with_output:
        lines.extend(self._generate_passed_with_output())
```

**No changes needed if already structured this way.**

**Verify GREEN:** Run `pytest tests/test_output_expectations.py::test_verbose_ignores_r_flags -v`
- Must pass

**Verify no regression:** Run `just test`

---

### Cycle 6.2: Test Flag Combinations Work Together

**RED: Write comprehensive integration test**

**File:** `tests/test_output_expectations.py`

**Action:** Add comprehensive test:
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

**Expected RED output:**
Should pass (GREEN) immediately if previous implementations were correct.

**Verify GREEN immediately:** Run `pytest tests/test_output_expectations.py::test_multiple_flags_combine_correctly -v`
- Should pass (integration/regression test)

---

**Phase 5 & 6 Complete** - Ready to move to Phase 7 (see [r-flag-parity-phase-7-checklist.md](r-flag-parity-phase-7-checklist.md))
