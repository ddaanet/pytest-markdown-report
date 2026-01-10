# Implementation Plan: Full -r Flag Parity (TDD) - Design Document

**Goal:** Make pytest-markdown-report the standard for agentic Python development by achieving complete pytest -r flag compatibility.

**Status:** Ready for TDD implementation
**Executor:** Haiku agent
**Discipline:** Strict RED-GREEN-REFACTOR
**Estimated complexity:** Medium (22 TDD cycles, ~200 LOC changes)

---

## TDD Protocol (MANDATORY)

### RED-GREEN-REFACTOR Cycle

**Every implementation follows this strict sequence:**

1. **RED:** Write a test that fails
2. **VERIFY RED:** Run test and confirm failure with expected error message
3. **GREEN:** Write minimal code to pass the test
4. **VERIFY GREEN:** Run test and confirm it passes
5. **REFACTOR:** Clean up if needed (optional)
6. **VERIFY GREEN:** Confirm test still passes after refactor

### Stop Conditions

**STOP IMMEDIATELY if:**
- A new test passes on first run (should be RED)
- Test failure message doesn't match expected
- Test passes after partial implementation
- Any existing test breaks (regression)

**Required actions when stopped:**
- Document what happened in session.md
- Investigate why test didn't fail as expected
- Fix test to ensure RED before continuing
- Do NOT proceed to next cycle

---

## Design Decisions (RESOLVED)

### 1. Default Behavior
**Decision:** Keep current defaults, implement `-rN` for explicit reset.
- No flags → Show failures + xpassed (current behavior preserved)
- `-v` → Show all sections (current behavior)
- `-q` → Summary only (current behavior)
- `-rN` → Explicitly suppress all sections except summary

### 2. Failure/Error Separation
**Decision:** Separate `E` (collection/setup errors) from `f` (test failures).

**Output structure:**
```markdown
## Errors
### conftest.py COLLECTION ERROR
### test_foo.py::test_bar ERROR in setup

## Failures
### test_foo.py::test_baz FAILED
```

### 3. Passed with Output (`-rP`)
**Decision:** Implement with condensed format.

**Format:**
```markdown
## Passes (with output)
- test_foo.py::test_debug PASSED
  stdout: "Debug info here"
```

### 4. Warnings (`-rw`)
**Decision:** Implement warnings section.

### 5. Flag Composition
**Decision:** Support all pytest flag combinations: `-rf`, `-rs`, `-rx`, `-rp`, `-rw`, `-rE`, `-ra`, `-rA`, `-rN`

### 6. Backwards Compatibility
**Decision:** Zero breaking changes. All existing tests must continue to pass.

---

## Implementation Phases Overview

This design is implemented across 7 phases with 22 TDD cycles total:

- **Phase 1 (5 cycles):** Separate errors from failures
- **Phase 2 (2 cycles):** Add -rp flag (passes in default mode)
- **Phase 3 (2 cycles):** Add -rP flag (passed with output)
- **Phase 4 (2 cycles):** Add -rw flag (warnings)
- **Phase 5 (3 cycles):** Add composite flags (-ra, -rA, -rN)
- **Phase 6 (2 cycles):** Edge cases and integration
- **Phase 7 (3 cycles):** Documentation updates

For implementation details, see:
- **[Phase 1 & 2 Implementation](r-flag-parity-phase-1-2.md)** - Separate errors from failures; add -rp flag
- **[Phase 3 & 4 Implementation](r-flag-parity-phase-3-4.md)** - Add -rP and -rw flags
- **[Phase 5 & 6 Implementation](r-flag-parity-phase-5-6.md)** - Composite flags and edge cases
- **[Phase 7 & Checklist](r-flag-parity-phase-7-checklist.md)** - Documentation and final checklist

---

## Flag Reference Table

| Flag | Description | Shows By Default | Phase |
|------|-------------|------------------|-------|
| `f` | Failed tests (call phase) | ✅ Yes | 1 |
| `E` | Setup/teardown/collection errors | ✅ Yes | 1 |
| `s` | Skipped tests | ❌ No | 5 |
| `x` | Expected failures (xfail) | ❌ No | 5 |
| `X` | Unexpected passes (xpassed) | ✅ Yes | 5 |
| `p` | Passed tests | ❌ No | 2 |
| `P` | Passed tests with captured output | ❌ No | 3 |
| `w` | Pytest warnings | ❌ No | 4 |
| `a` | All except passes (fEsxXw) | ❌ No | 5 |
| `A` | All including passes (fEsxXpPw) | ❌ No | 5 |
| `N` | None/suppress all sections | ❌ No | 5 |

---

## Expected Test Counts

| Milestone | Tests | New |
|-----------|-------|-----|
| Before implementation | ~25 | - |
| After Phase 1 | ~30 | +5 |
| After Phase 2 | ~32 | +2 |
| After Phase 3 | ~33 | +1 |
| After Phase 4 | ~34 | +1 |
| After Phase 5 | ~37 | +3 |
| After Phase 6 | ~39 | +2 |
| Final | ~39 | +14 |

---

## Key Implementation Points

### Report Categorization
- `failed` (call phase) → **## Failures** section
- `failed` (setup/teardown) → **## Errors** section
- `errors` (collection) → **## Errors** section
- `xfailed` → **## Failures** section
- `xpassed` → **## Failures** section (always shown by default)
- `skipped` → **## Skipped** section
- `passed` → **## Passes** section
- `passed_with_output` → **## Passes (with output)** section
- `warnings` → **## Warnings** section

### Display Logic
1. **Default mode (no -r flags):** Show fEX (failures + errors + xpassed)
2. **With -r flags:** Show only requested sections
3. **Verbose mode (-v):** Show all sections, ignore -r flags
4. **Quiet mode (-q):** Show only summary

### Flag Composition Rules
- `a` expands to: `fEsxXw` (all except passes)
- `A` expands to: `fEsxXpPw` (all including passes)
- `N` suppresses everything except summary
- Explicit flags override defaults: `-rf` hides errors, `-rE` hides failures

---

## Cross-References

- **TDD Cycles 1.1-1.5:** [Phase 1 & 2 Implementation](r-flag-parity-phase-1-2.md)
- **TDD Cycles 2.1-2.2:** [Phase 1 & 2 Implementation](r-flag-parity-phase-1-2.md)
- **TDD Cycles 3.1-3.2:** [Phase 3 & 4 Implementation](r-flag-parity-phase-3-4.md)
- **TDD Cycles 4.1-4.2:** [Phase 3 & 4 Implementation](r-flag-parity-phase-3-4.md)
- **TDD Cycles 5.1-5.3:** [Phase 5 & 6 Implementation](r-flag-parity-phase-5-6.md)
- **TDD Cycles 6.1-6.2:** [Phase 5 & 6 Implementation](r-flag-parity-phase-5-6.md)
- **TDD Cycles 7.1-7.3:** [Phase 7 & Checklist](r-flag-parity-phase-7-checklist.md)

---

**Ready to begin strict TDD implementation. See implementation phase documents for detailed cycles.**
