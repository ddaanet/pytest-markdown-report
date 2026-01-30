# Cycle 0.1: Pre-Implementation Spike Results

**Date**: 2026-01-30
**Objective**: Verify current behavior with composite flags to identify RED vs REGRESSION cycles

## Executive Summary

Current state: The plugin does NOT yet implement composite flag expansion (-ra, -rA, -rN). All three flags currently show identical output (same as default), indicating they are not being handled at all. The test `test_errors_separate_from_failures` currently PASSES, meaning it doesn't test the breaking change mentioned in design.

## Test Environment

- pytest version: 9.0.2
- pytest default -r value: `"fE"` (show failures + errors)
- Platform: darwin (macOS)

## Current Behavior Findings

### Composite Flag Results

All commands showed identical output pattern:

```
# Test Report
**Summary:** 7/11 passed, 2 failed, 1 skipped, 1 xfail

## Errors
### tests/examples.py::test_setup_error ERROR in setup
    (error details)

## Failures
### tests/examples.py::test_edge_case FAILED
    (failure details)
```

**Flag-by-flag observations:**

| Flag | Behavior | Current Output | Expected per Design |
|------|----------|-----------------|---------------------|
| `-ra` | Show all except passes | Shows Errors + Failures | Should expand to `"fExswpPw"` |
| `-rA` | Show all | Shows Errors + Failures | Should expand to `"fExswpPwX"` |
| `-rN` | Suppress all | Shows Errors + Failures | Should suppress ALL sections |
| `-v -rN` | Verbose + suppress all | Shows Errors + Failures + xfail | Should suppress all but keep verbose output format |

**Conclusion**: None of the composite flags are being expanded. They fall through to default behavior of `"fE"`.

### Breaking Change Test Status

**Test**: `test_errors_separate_from_failures` (line 155 of test_output_expectations.py)

**Current status**: ✅ PASSES

**What it tests**:
- Runs `pytest examples.py -rE`
- Expects both ## Errors and ## Failures sections to appear
- Expects setup error in Errors section
- Expects regular failures in Failures section

**Relevance to breaking change**:

Design specifies: "Breaking change: `-rE` now hides failures"
- Old behavior (current): -rE shows both Errors AND Failures
- New behavior (target): -rE shows ONLY Errors (failures gated on `f` flag)

This test will FAIL once the breaking change is implemented because it expects failures to be shown with `-rE`. The test will need to be updated to reflect new behavior.

**Classification**: This is a REGRESSION cycle - the test currently passes (feature exists) but will break when we implement the breaking change. Cycle 1.3 must update this test.

## Spike Output Records

### Command: `-ra` flag
```bash
pytest tests/examples.py -ra 2>&1 | head -30
```
Output: Shows Errors + Failures (same as default behavior)

### Command: `-rA` flag
```bash
pytest tests/examples.py -rA 2>&1 | head -30
```
Output: Shows Errors + Failures (same as default behavior)

### Command: `-rN` flag
```bash
pytest tests/examples.py -rN 2>&1 | head -30
```
Output: Shows Errors + Failures (same as default behavior)

### Command: `-v -rN` flag
```bash
pytest tests/examples.py -v -rN 2>&1 | head -30
```
Output: Shows Errors + Failures + xfail (verbose mode adds xfail by default)

## Cycle Classifications

Based on findings:

| Cycle | Type | Reasoning | RED Action |
|-------|------|-----------|-----------|
| 1.1 | Standard RED | `-ra` flag not yet implemented | Write test expecting sections per expansion |
| 1.2 | Standard RED | `-rA` flag not yet implemented | Write test expecting all sections |
| 1.3 | REGRESSION | `test_errors_separate_from_failures` must change for breaking change | Update test to reflect new behavior (no failures with -rE) |
| 2.1 | Standard RED | `-rN` flag not yet implemented | Write test expecting empty output |
| 2.2 | Standard RED | `-rN` override behavior with `-v` | Write test for verbose override |

## Plugin Code Review

Current plugin handling of report_flags (line 104, 292-305):

```python
self.report_flags = getattr(config.option, "reportchars", "")
```

The plugin stores raw reportchars value but:
- Does NOT expand composite flags (`N`, `A`, `a`)
- Does NOT handle `-rN` suppression
- Just checks `if "X" in self.report_flags` for individual flags

**What needs to be added:**
1. Composite flag expansion logic before individual flag checks
2. `-rN` handling to suppress ALL sections
3. `-rA` to show everything
4. `-ra` to show everything except passes

## Recommendation for Next Steps

1. **Cycle 1.1**: Implement `-ra` expansion and test
2. **Cycle 1.2**: Implement `-rA` expansion and test
3. **Cycle 1.3**: Update `test_errors_separate_from_failures` test (marked REGRESSION in cycle definition)
4. **Cycle 2.1**: Implement `-rN` suppression and test
5. **Cycle 2.2**: Test verbose mode override of `-rN`

All cycles ready to proceed as RED → GREEN → REFACTOR.

---

**Status**: Ready for TDD execution
**Validated**: Current behavior understood
**Next action**: Begin Cycle 1.1
