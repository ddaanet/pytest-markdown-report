# Phase 7 & Implementation Checklist

**Reference:** See [Design Document](r-flag-parity-design.md) for overview and design decisions.

**Phase covered:** Phase 7 (Cycles 7.1-7.3) - Documentation and checklist

---

## Phase 7: Documentation

### Cycle 7.1: Update AGENTS.md [DEPENDS: 6.2]

**No test needed - documentation only**

**File:** `AGENTS.md`

**Action:** Update "Report Categorization Logic" section (lines 106-135):

Replace with:
```markdown
### Report Categorization Logic

Test outcomes are categorized and displayed in separate sections:

- `failed`: Test assertion failures (call phase) → **## Failures** section
- `errors`: Setup/teardown/collection errors → **## Errors** section
- `xfailed`: Expected failures (`@pytest.mark.xfail` that fail) → **## Failures** section
- `xpassed`: Unexpected passes (xfail tests that pass) → **## Failures** section (always shown)
- `skipped`: Tests marked skip or conditional skips → **## Skipped** section
- `passed`: Successful tests → **## Passes** section
- `passed_with_output`: Passing tests with captured output → **## Passes (with output)** section
- `warnings`: Pytest warnings → **## Warnings** section

**Display modes:**
- **Default mode**: Respects -r flags (defaults to fEX: failures + errors + xpassed)
- **Verbose mode (-v)**: Always shows all sections regardless of -r flags
- **Quiet mode (-q)**: Shows only summary line

**Available -r flags:**
- `f` = failed tests (default: shown)
- `E` = errors in setup/teardown (default: shown)
- `s` = skipped tests
- `x` = xfailed tests
- `X` = xpassed tests (default: shown)
- `p` = passed tests
- `P` = passed tests with captured output
- `w` = pytest warnings
- `a` = all except passes (shortcut for fEsxXw)
- `A` = all including passes (shortcut for fEsxXpPw)
- `N` = none (suppress all sections except summary)

**Examples:**
```bash
pytest                       # Default: failures + errors + xpassed
pytest -rs                   # Add skipped section
pytest -rx                   # Add xfailed section
pytest -rsx                  # Show skipped + xfailed
pytest -rp                   # Add passes
pytest -ra                   # Show all except passes
pytest -rA                   # Show everything
pytest -rN                   # Summary only (like -q)
pytest -rf                   # Only failures (hide errors)
pytest -rE                   # Only errors (hide failures)
```

**Section order:** Summary → Errors → Failures → Skipped → Warnings → Passes → Passes (with output)
```

---

### Cycle 7.2: Update README.md [DEPENDS: 7.1]

**No test needed - documentation only**

**File:** `README.md`

**Action 1:** Add section after "Verbosity Modes" (~line 54):

```markdown
### Controlling Output Sections

Use `-r` flags to show/hide specific sections in default mode:

```bash
# Show skipped tests
pytest -rs

# Show expected failures (xfail)
pytest -rx

# Show passed tests
pytest -rp

# Show all except passes
pytest -ra

# Show everything
pytest -rA

# Suppress all sections (summary only)
pytest -rN
```

**Available flags:**
- `f` = failed tests (shown by default)
- `E` = errors (shown by default)
- `s` = skipped tests
- `x` = xfailed tests
- `X` = xpassed tests (shown by default)
- `p` = passed tests
- `P` = passed tests with output
- `w` = warnings
- `a` = all except passes
- `A` = all including passes
- `N` = none (suppress sections)

**Note:** Verbose mode (`-v`) shows all sections regardless of `-r` flags.
```

**Action 2:** Update "Output Format" section (~line 78) to add Errors example before Failures:

```markdown
### Default Mode

````markdown
# Test Report

**Summary:** 2/7 passed, 3 failed, 1 error, 1 skipped

## Errors

### test_database.py::test_with_db ERROR in setup

```python
conftest.py:15: in db_connection
    raise ConnectionError("Database unavailable")
E   ConnectionError: Database unavailable
```

## Failures

### test_validation.py::test_invalid_input[empty] FAILED

```python
test_validation.py:42: in test_invalid_input
    assert validate(input) == expected
E   AssertionError: assert False == True
```
````
```

---

### Cycle 7.3: Update session.md [DEPENDS: 7.2]

**No test needed - session tracking**

**File:** `session.md`

**Action:** Replace content with:
```markdown
# Current Session Context

**Status:** 🚧 Full -r flag parity implementation in progress

---

## Current Work

**Implementation:** TDD-driven full -r flag support
- Following strict RED-GREEN-REFACTOR discipline
- 22 TDD cycles across 7 phases

**Completed Cycles:** (track progress here)
- [ ] Phase 1: Separate errors from failures (5 cycles)
- [ ] Phase 2: Add -rp flag (2 cycles)
- [ ] Phase 3: Add -rP flag (2 cycles)
- [ ] Phase 4: Add -rw flag (2 cycles)
- [ ] Phase 5: Add composite flags (3 cycles)
- [ ] Phase 6: Edge cases (2 cycles)
- [ ] Phase 7: Documentation (3 updates)

**Current cycle:** [Agent to update]

**Test status:** All existing tests must continue passing

---

## Previous Work (Archive)

✅ Phase 0-4 complete (bug fixes, -rs/-rx flags, test coverage)
```

---

## Implementation Checklist for Haiku Agent

### Pre-Implementation Verification
- [ ] Read entire plan thoroughly
- [ ] Verify all existing tests pass: `just test`
- [ ] Understand RED-GREEN-REFACTOR discipline
- [ ] Commit to stopping if any test is GREEN when expected RED

### Phase 1: Separate Errors (5 cycles)
- [ ] Cycle 1.1: Add setup error fixture
- [ ] Cycle 1.2: Test errors separate section (RED → GREEN)
- [ ] Cycle 1.3: Test default shows both (RED → GREEN)
- [ ] Cycle 1.4: Test -rf hides errors (RED → GREEN)
- [ ] Cycle 1.5: Test summary error count (RED → GREEN)

### Phase 2: Add -rp (2 cycles)
- [ ] Cycle 2.1: Test -rp shows passes (RED → GREEN)
- [ ] Cycle 2.2: Test verbose unchanged (GREEN immediately)

### Phase 3: Add -rP (2 cycles)
- [ ] Cycle 3.1: Add output fixture
- [ ] Cycle 3.2: Test -rP shows output (RED → GREEN)

### Phase 4: Add -rw (2 cycles)
- [ ] Cycle 4.1: Add warning fixture
- [ ] Cycle 4.2: Test -rw shows warnings (RED → GREEN)

### Phase 5: Composite Flags (3 cycles)
- [ ] Cycle 5.1: Test -ra all except passes (RED → GREEN)
- [ ] Cycle 5.2: Test -rA everything (GREEN immediately)
- [ ] Cycle 5.3: Test -rN suppresses (GREEN immediately)

### Phase 6: Edge Cases (2 cycles)
- [ ] Cycle 6.1: Test verbose overrides (RED or GREEN)
- [ ] Cycle 6.2: Test flag combinations (GREEN immediately)

### Phase 7: Documentation
- [ ] Update AGENTS.md
- [ ] Update README.md
- [ ] Update session.md

### Post-Implementation
- [ ] Run full test suite: `just test -v`
- [ ] Manually test all flags: `-rf`, `-rE`, `-rs`, `-rx`, `-rp`, `-rP`, `-rw`, `-ra`, `-rA`, `-rN`
- [ ] Verify no regressions in existing behavior
- [ ] Update session.md with completion status

---

## Success Criteria

- [ ] All 35+ tests pass (25 existing + 10+ new)
- [ ] Every new test was RED before implementation
- [ ] No existing tests broke during implementation
- [ ] All -r flags work as documented
- [ ] Errors properly separated from failures
- [ ] Documentation updated completely
- [ ] Zero breaking changes to existing behavior

---

## Emergency Stop Conditions

**STOP IMMEDIATELY and update session.md if:**
1. ❌ New test passes when expected to fail (RED)
2. ❌ Existing test breaks (regression)
3. ❌ Test failure message doesn't match expected
4. ❌ Uncertain about why test passed/failed
5. ❌ Implementation seems to work but test still fails

**When stopped:**
- Document the cycle number and what happened in session.md
- Investigate why test didn't fail as expected
- If feature already works correctly:
  - Convert test to regression test, mark `[REGRESSION]`
  - Mark cycle complete, proceed to next
- If test is incorrect:
  - Fix test to ensure RED before continuing
  - Do NOT proceed to next cycle until RED verified
- Run `git diff` to see changes
- Wait for guidance if unclear

---

## Notes for Implementation Agent

### Critical Reminders
1. **RED must fail** - If new test passes immediately, STOP
2. **Run tests frequently** - After every code change
3. **No skipping cycles** - Complete each RED-GREEN pair
4. **Verify regressions** - Run `just test` after each GREEN
5. **Update session.md** - Track progress through cycles

### Testing Commands
```bash
# Run single test
pytest tests/test_output_expectations.py::test_name -v

# Run all tests
just test

# Run with verbose output
just test -v

# Run only new tests (if marked)
pytest tests/test_output_expectations.py -v -k "flag"
```

### Expected Test Counts
- Before: ~25 tests
- After Phase 1: ~30 tests
- After Phase 2: ~32 tests
- After Phase 3: ~33 tests
- After Phase 4: ~34 tests
- After Phase 5: ~37 tests
- After Phase 6: ~39 tests

### Code Style
- 4-space indentation
- Type hints on all methods
- Docstrings for all public methods
- Follow existing patterns in plugin.py
- Use existing `escape_markdown()` for user text

---

## TDD Discipline Verification

Before starting, confirm understanding:
- ✅ I will write tests before code
- ✅ I will verify every test is RED before implementing
- ✅ I will stop if a test is unexpectedly GREEN
- ✅ I will run `just test` after every GREEN
- ✅ I will track progress in session.md
- ✅ I will not skip any cycles

**Ready to begin strict TDD implementation.**

---

## Document Cross-References

**Design & Overview:**
- [r-flag-parity-design.md](r-flag-parity-design.md) - Design decisions, protocol, flag reference

**Implementation Phases:**
- [r-flag-parity-phase-1-2.md](r-flag-parity-phase-1-2.md) - Phase 1 (cycles 1.1-1.5) and Phase 2 (cycles 2.1-2.2)
- [r-flag-parity-phase-3-4.md](r-flag-parity-phase-3-4.md) - Phase 3 (cycles 3.1-3.2) and Phase 4 (cycles 4.1-4.2)
- [r-flag-parity-phase-5-6.md](r-flag-parity-phase-5-6.md) - Phase 5 (cycles 5.1-5.3) and Phase 6 (cycles 6.1-6.2)

**This Document:**
- [r-flag-parity-phase-7-checklist.md](r-flag-parity-phase-7-checklist.md) - Phase 7 documentation and implementation checklist
