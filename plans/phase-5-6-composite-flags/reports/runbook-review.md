# TDD Runbook Review: phase-5-6-composite-flags

**Reviewed**: 2026-01-29
**Runbook**: plans/phase-5-6-composite-flags/runbook.md
**Reviewer**: tdd-plan-reviewer (review-tdd-plan skill)

---

## Summary

- **Total cycles**: 6 (0.1 spike + 5 TDD cycles)
- **Violations found**: 3 critical
- **Overall assessment**: NEEDS REVISION

---

## Critical Issues

### Issue 1: GREEN phase contains complete implementation code
**Location**: Cycle 1.1, lines 203-224
**Problem**: Complete `_should_show_section()` implementation prescribed in GREEN phase

The GREEN phase provides the entire method implementation:

```python
def _should_show_section(self, flag: str) -> bool:
    """Determine if a section should be shown based on -r flags.

    Args:
        flag: Single character flag (f, E, s, x, p, P, w)

    Returns:
        True if section should be shown
    """
    # Composite: suppress all
    if "N" in self.report_flags:
        return False
    # Composite: all including passes
    if "A" in self.report_flags:
        return True
    # Composite: all except passes
    if "a" in self.report_flags:
        return flag not in ("p", "P")
    # Individual flags
    return flag in self.report_flags
```

**Why this violates TDD principles:**
- Prescribes exact code, turning agent into code copier
- Test doesn't drive implementation discovery
- No room for agent to determine optimal approach
- Violates RED→GREEN incremental learning

**Recommended fix:**

Replace the implementation code block with behavior description:

```markdown
**Action 1:** Add helper method `_should_show_section()` after `__init__()` (after line 117)

**Behavior:**
- Accept single character flag (f, E, s, x, p, P, w)
- Return True if section should be shown based on self.report_flags
- Handle composite flags: "N" (suppress all), "A" (show all), "a" (show all except p/P)
- Fall back to checking if flag is in self.report_flags

**Implementation hint:** Check composite flags first (early returns), then check individual flags

**Tests will drive**: The exact conditional structure and order of checks
```

---

### Issue 2: GREEN phase prescribes complete refactored method
**Location**: Cycle 1.1, lines 230-256
**Problem**: Complete `_build_default_sections()` refactoring prescribed

The GREEN phase provides the entire refactored method body (27 lines of implementation code).

**Why this violates TDD principles:**
- Same as Issue 1 - prescribes exact implementation
- Agent becomes code copier, not implementer
- Doesn't allow test failures to guide refactoring approach

**Recommended fix:**

Replace with behavior-oriented guidance:

```markdown
**Action 2:** Refactor `_build_default_sections()` to use `_should_show_section()` helper

**Current behavior** (lines 284-306):
- Direct flag checks like `"E" in self.report_flags`
- Unconditional failure/error display

**New behavior:**
- Replace all direct flag checks with `self._should_show_section(flag)` calls
- Gate every section on appropriate flag (E, f, s, p, P, w)
- Maintain existing section order

**Implementation hint:**
- Extract `show_xfailed = self._should_show_section("x")` once at top
- Use in failures section condition check

**Tests will drive**: The exact conditional structure for each section
```

---

### Issue 3: GREEN phase prescribes test update implementation
**Location**: Cycle 1.1, lines 262-265
**Problem**: Exact test assertion code prescribed

```python
# Failures should NOT appear (only errors requested)
assert "test_edge_case FAILED" not in actual, "Failures should be hidden with -rE (errors only)"
```

**Why this violates TDD principles:**
- Not really implementation code, but still prescriptive for test updates
- Minor violation compared to Issues 1-2

**Recommended fix:**

Replace with behavior description:

```markdown
**Action 3:** Update `test_errors_separate_from_failures` expectation (line 169-170)

**Behavior change:**
- Old: Failures shown with `-rE` (unconditional failure display)
- New: `-rE` shows only errors (failures hidden)

**Update assertion:** Change from expecting failures to expecting NO failures with `-rE`

**Implementation hint:** Invert the assertion on line 170
```

---

## Warnings

### Warning 1: Multiple actions in single cycle
**Location**: Cycle 1.1
**Details**: 3 separate actions (add method, refactor method, update test) in one cycle

**Rationale for accepting:**
- All 3 actions needed for `-ra` flag to work
- Cannot split into sub-cycles (test requires all 3 changes)
- Not technically a TDD violation, just complex

**Recommendation:** Consider adding comment explaining why all 3 actions are minimal unit for this feature.

---

### Warning 2: REGRESSION cycles contain test code
**Location**: Cycles 1.2, 1.3, 2.1, 2.2
**Details**: These cycles labeled [REGRESSION] and contain complete test implementations

**Rationale for accepting:**
- Appropriate use case: These tests verify implementation from Cycle 1.1
- Tests should pass immediately (GREEN immediately pattern)
- Not prescribing implementation code, only verification tests
- Consistent with TDD principles for regression coverage

**No action needed:** This is correct usage.

---

## Cycle-by-Cycle Analysis

### Cycle 0.1 (Spike)
**Type**: Pre-implementation spike
**Status**: ✓ PASS - No TDD violations (exploratory phase)

### Cycle 1.1 (RED/GREEN)
**Type**: Feature implementation
**Status**: ✗ FAIL - 3 critical violations (Issues 1, 2, 3)

**RED Phase** (lines 151-190):
- ✓ Test specification clear
- ✓ Expected failure message specified
- ✓ Explanation of why test will fail

**GREEN Phase** (lines 193-284):
- ✗ Complete implementation code for `_should_show_section()` (Issue 1)
- ✗ Complete refactored method for `_build_default_sections()` (Issue 2)
- ✗ Prescriptive test update code (Issue 3)

**Sequencing check:**
- ✓ Test will fail in RED (no composite flag parsing exists)
- ✓ Implementation will make test pass

### Cycle 1.2 (REGRESSION)
**Type**: Regression verification
**Status**: ✓ PASS - Appropriate test-only cycle

**Notes:**
- [REGRESSION] tag correct
- "GREEN Immediately" expectation correct
- Test code appropriate for verification

### Cycle 1.3 (REGRESSION)
**Type**: Regression verification
**Status**: ✓ PASS - Appropriate test-only cycle

### Cycle 2.1 (REGRESSION)
**Type**: Regression verification
**Status**: ✓ PASS - Appropriate test-only cycle

### Cycle 2.2 (REGRESSION)
**Type**: Integration verification
**Status**: ✓ PASS - Appropriate test-only cycle

---

## Recommendations

### 1. Remove implementation code from Cycle 1.1 GREEN phase

**Action 1 fix:**
- Remove lines 203-224 (complete `_should_show_section()` implementation)
- Replace with behavior description + hints (see Issue 1)

**Action 2 fix:**
- Remove lines 230-256 (complete `_build_default_sections()` refactoring)
- Replace with behavior-oriented guidance (see Issue 2)

**Action 3 fix:**
- Remove lines 262-265 (prescriptive test update code)
- Replace with behavior description (see Issue 3)

### 2. Add implementation hints for sequencing

**Recommended additions to Cycle 1.1 GREEN:**

```markdown
**Sequencing notes:**
1. Implement `_should_show_section()` first
2. Update `_build_default_sections()` to use new helper
3. Update `test_errors_separate_from_failures` to match new behavior
4. Run tests after each change to catch integration issues early
```

### 3. Consider splitting Action 3 to separate cycle

**Optional improvement:**
- Move test update (Action 3) to separate Cycle 1.1b
- Makes Cycle 1.1 purely about feature implementation
- Makes Cycle 1.1b about fixing regression from behavior change

**Trade-off:**
- Cleaner separation of concerns
- More cycles to track
- Test might fail in 1.1 due to old expectation (could be confusing)

**Recommendation:** Keep as-is (3 actions in one cycle), but acknowledge complexity in runbook.

---

## Overall Assessment

**NEEDS REVISION**

The runbook violates TDD principles by prescribing complete implementation code in the GREEN phase. The agent executing this runbook would become a code copier rather than an implementer discovering solutions through test-driven development.

**Required fixes:**
- Remove all implementation code from Cycle 1.1 GREEN phase (Issues 1, 2, 3)
- Replace with behavior descriptions and implementation hints
- Let tests drive the implementation structure

**Strengths:**
- RED phase specifications are excellent
- REGRESSION cycles appropriately structured
- Stop conditions well-defined
- Sequencing logic sound

**After fixes:** This runbook will properly support TDD methodology with tests driving implementation discovery.

---

## Key Principles Violated

1. **Tests drive implementation** - Not scripts
   - Violated in Cycle 1.1 GREEN phase (prescriptive code)

2. **Minimal means minimal** - One behavior per cycle
   - Borderline acceptable (3 actions needed for single feature)

3. **RED must fail** - Before GREEN can pass
   - ✓ Satisfied (proper sequencing)

4. **Describe behavior** - Not code
   - Violated in Cycle 1.1 GREEN phase (exact code provided)

5. **Provide hints** - Not solutions
   - Violated in Cycle 1.1 GREEN phase (complete solutions provided)

---

**Next steps:** Apply fixes to Cycle 1.1 GREEN phase, then proceed with prepare-runbook.py and execution.
