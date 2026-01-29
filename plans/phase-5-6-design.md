# Design: Phase 5 & 6 — Composite Flags and Edge Cases

**Job:** Implement `-ra`, `-rA`, `-rN` composite flags and validate verbose override + flag combinations.

**Mode:** TDD
**Downstream:** `/plan-tdd`

---

## Critical Finding: pytest Default `reportchars`

The existing plan (`r-flag-parity-phase-5-6.md`) assumes `self.report_flags` is empty when no `-r` flag is passed. **This is wrong.**

**Measured behavior:**
```
Default (no -r):  reportchars = "fE"
-ra:              reportchars = "a"
-rA:              reportchars = "A"
-rN:              reportchars = "N"
-rsx:             reportchars = "sx"
-rf:              reportchars = "f"
```

Pytest stores raw characters — does NOT expand `a` → `fEsxXw`. Default is `"fE"`, not `""`.

### Impact on `_should_show_section()` Design

The existing plan's empty-string check is dead code:
```python
# WRONG — this never triggers
if not self.report_flags:
    return flag in "fEX"
```

Correct approach must handle the default `"fE"` value:
- Default shows failures + errors (from `"fE"`) plus xpassed (unconditionally, matching current behavior)
- Explicit flags override defaults completely (pytest replaces, doesn't append)

---

## Current State

**`_build_default_sections()`** (plugin.py:284-306):
- `show_xfailed = "x" in self.report_flags` — correct (off by default)
- `show_errors = "E" in self.report_flags` — correct (on by default, since reportchars="fE")
- Failures/xpassed always shown (line 296: unconditional check)
- Skipped, passes, passed_output, warnings gated on individual flags

**Problem:** The unconditional `self.failed or self.xpassed` on line 296 means `-rf` doesn't actually hide failures. The test `test_rf_flag_hides_errors` only checks errors are hidden, not that failures persist. But with composite flags, we need `-rN` to suppress failures too.

**Current failures behavior:** Always shown regardless of flags. This needs to change for `-rN` to work.

---

## Design Decisions

### 1. `_should_show_section()` Logic

```python
def _should_show_section(self, flag: str) -> bool:
    """Determine if a section should be shown based on -r flags."""
    # Composite: suppress all
    if "N" in self.report_flags:
        return False
    # Composite: all including passes
    if "A" in self.report_flags:
        return True
    # Composite: all except passes
    if "a" in self.report_flags:
        return flag not in ("p", "P")
    # Individual flags + xpassed always shown
    if flag == "X":
        return True
    return flag in self.report_flags
```

**Key decisions:**
- **xpassed (`X`) always shown** unless `-rN`: These are unexpected passes — always important. Matches current unconditional behavior.
- **`-rN` suppresses everything**: Including failures and xpassed. Only summary remains.
- **`-ra` = everything except passes**: `flag not in ("p", "P")` — simpler than enumerating.
- **`-rA` = everything**: Returns `True` unconditionally.
- **No empty-string special case**: Default `"fE"` is handled by `flag in self.report_flags`.

### 2. Failures Always Have `f` Flag

Currently failures show unconditionally. With `_should_show_section`, we gate on `show_failures`:
```python
show_failures = self._should_show_section("f")
if show_failures and (self.failed or self.xpassed or (show_xfailed and self.xfailed)):
    ...
```

This means `-rE` (errors only) would now hide failures. But wait — does the current test `test_rf_flag_hides_errors` expect failures to still show with `-rf`? Let me check.

**Current test `test_rf_flag_hides_errors`** checks:
- `-rf` → errors NOT shown, failures still shown

With the new logic: `-rf` → `reportchars = "f"` → `show_failures = True`, `show_errors = False`. Correct.

**But `-rE`** → `reportchars = "E"` → `show_failures = False`, `show_errors = True`. This would hide failures when only `-rE` is passed. Is that desired?

**Decision:** Yes. Explicit `-r` flags mean "show only these". `-rE` means "show only errors". This matches pytest behavior where `-rE` shows only error short summary, not failure short summary.

**BUT: xpassed special case.** xpassed are shown unconditionally in current behavior (line 296). Should `-rE` hide xpassed?

**Decision:** xpassed always shown unless `-rN`. They're unexpected passes — a signal you shouldn't miss. The `X` flag is separate from `f`. So xpassed shows with `-rE` (via the `X` always-true rule), and failures section header + xpassed appear even with `-rE`.

Actually, wait. xpassed items are rendered inside `_generate_failures()`. So if `show_failures` is False but xpassed exist, we'd still need to call `_generate_failures()` with only xpassed. Let me re-examine.

**Revised approach for failures section:**
```python
show_failures = self._should_show_section("f")
show_xpassed = self._should_show_section("X")  # always True unless -rN
has_failure_content = (
    (show_failures and self.failed)
    or (show_xpassed and self.xpassed)
    or (show_xfailed and self.xfailed)
)
if has_failure_content:
    lines.extend(self._generate_failures(
        show_xfailed=show_xfailed,
        show_failed=show_failures,
        show_xpassed=show_xpassed,
    ))
```

This requires `_generate_failures()` to accept `show_failed` and `show_xpassed` params. Currently it only takes `show_xfailed`.

**Simplification:** This is getting complex. Alternative: keep xpassed gated on `f` flag (they're in the Failures section). Then `-rE` hides both failures and xpassed.

**Final decision:** Gate xpassed on `f` flag, not separate `X`. Rationale:
- xpassed render inside Failures section
- Separating the gate adds params to `_generate_failures()`
- Current default `"fE"` includes `f`, so xpassed still show by default
- `-ra` and `-rA` both include `f` equivalent, so xpassed show there too
- Only case where xpassed hidden: explicit `-rE` or `-rs` without `f`. Acceptable — user explicitly chose not to see failures.

This simplifies `_should_show_section()`:
```python
def _should_show_section(self, flag: str) -> bool:
    if "N" in self.report_flags:
        return False
    if "A" in self.report_flags:
        return True
    if "a" in self.report_flags:
        return flag not in ("p", "P")
    return flag in self.report_flags
```

No `X` special case needed. xpassed gate follows `f`.

### 3. Breaking Change Assessment

**Current behavior (default, no -r):**
- Failures + xpassed: always shown → still shown (`f` in default `"fE"`)
- Errors: shown when `E` in flags → still shown (`E` in default `"fE"`)

**New behavior with -rN:**
- Nothing shown except summary → new feature, not breaking

**New behavior with -rf:**
- Currently: failures shown (unconditional), errors hidden
- New: failures shown (`f` in flags), errors hidden (`E` not in flags) → same

**Potential break: `-rE` without `f`:**
- Currently: errors shown, failures still shown (unconditional)
- New: errors shown, failures hidden (`f` not in `"E"`)
- **This is a behavior change.** But no test exists for this case, and it's the correct behavior (matching pytest semantics).

**Verdict:** No test regressions expected. The `-rE` behavior change is correct.

---

## Scope

### In Scope
- `_should_show_section()` helper method
- Refactor `_build_default_sections()` to use it
- Tests for `-ra`, `-rA`, `-rN`
- Test verbose overrides `-r` flags
- Test flag combinations

### Out of Scope
- Phase 7 (documentation)
- Changes to verbose/quiet mode logic
- Changes to `_generate_*` methods (signatures preserved)

---

## Architecture

### Method Placement

`_should_show_section()` goes after `__init__` (~line 118), before hook methods. Small utility, no dependencies.

### Refactored `_build_default_sections()`

```python
def _build_default_sections(self) -> list[str]:
    lines = []
    show_xfailed = self._should_show_section("x")
    if self._should_show_section("E") and self.errors:
        lines.extend(self._generate_errors())
    if self._should_show_section("f") and (
        self.failed or self.xpassed or (show_xfailed and self.xfailed)
    ):
        lines.extend(self._generate_failures(show_xfailed=show_xfailed))
    if self._should_show_section("s") and self.skipped:
        lines.extend(self._generate_skipped())
    if self._should_show_section("p") and self.passed:
        lines.extend(self._generate_passes())
    if self._should_show_section("P") and self.passed_with_output:
        lines.extend(self._generate_passed_with_output())
    if self._should_show_section("w") and self.warnings:
        lines.extend(self._generate_warnings())
    return lines
```

Changes from current code:
- `show_errors` replaced with `self._should_show_section("E")`
- `show_xfailed` now uses helper
- Failures gated on `self._should_show_section("f")` instead of unconditional
- Inline flag checks replaced with helper calls

### Existing Tests That May Be Affected

Run `just test` after Cycle 5.1 GREEN to catch regressions. Key tests:
- `test_default_shows_errors_and_failures` — uses default flags, should still pass
- `test_rf_flag_hides_errors` — `-rf` hides errors, shows failures, should still pass
- `test_errors_separate_from_failures` — `-rE` shows errors. **May now hide failures** if test checks for them

Need to verify `test_errors_separate_from_failures` expectations before implementing.

---

## Testing Strategy

**5 TDD cycles** as in existing plan, but with corrected logic:

| Cycle | Type | Test | Key Assertion |
|-------|------|------|--------------|
| 5.1 | RED→GREEN | `-ra` shows all except passes | Has Skipped, Errors, Failures; no Passes |
| 5.2 | REGRESSION | `-rA` shows everything | Has Passes section |
| 5.3 | REGRESSION | `-rN` suppresses all | No section headers, summary only |
| 6.1 | REGRESSION | verbose overrides `-rN` | `-v -rN` still shows all sections |
| 6.2 | REGRESSION | flag combinations | `-rsx`, `-rEf`, `-rpP` |

Cycles 5.2, 5.3, 6.1, 6.2 expected GREEN immediately (implementation in 5.1 covers them).

---

## Pre-Implementation Spike

Before writing tests, verify current behavior to identify which cycles are truly RED vs REGRESSION:

```bash
# What does current code do with -ra?
pytest tests/examples.py -ra --md-report /dev/null 2>&1 | head -20

# Does -rN currently suppress?
pytest tests/examples.py -rN --md-report /dev/null 2>&1 | head -20
```

If `-ra` already partially works (e.g., shows some sections), document which sections appear and adjust test expectations.

---

## Next Step

This design is ready for `/plan-tdd`. The planner should:
- Use the corrected `_should_show_section()` logic (no empty-string check)
- Verify `test_errors_separate_from_failures` before Cycle 5.1 GREEN
- Run pre-implementation spike first
