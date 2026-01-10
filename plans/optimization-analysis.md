# Token Optimization Analysis

**Goal:** NEVER larger than equivalent pytest output without plugin.

**Current status:** Markdown default (228 tokens) vs tuned pytest (180 tokens) = **27% LARGER**

---

## Benchmark Results (tests/examples.py)

| Format | Tokens | vs Pytest Default | vs Tuned Pytest |
|--------|--------|-------------------|-----------------|
| Default pytest | 381 | baseline | +112% |
| Tuned pytest (-q --tb=short --no-header) | 180 | -53% | baseline |
| **Markdown default** | **228** | **-40%** | **+27%** |
| Markdown verbose (-v) | 303 | -20% | +68% |
| Markdown quiet (-q) | 46 | -88% | -74% |

**Problem:** Markdown default is larger than best-tuned pytest.

---

## Optimization Opportunities

### 1. XFAIL Traceback Removal ✓ RECOMMENDED

**Current behavior:**
```markdown
### tests/examples.py::test_known_bug XFAIL

**Reason:** Bug #123

```python
tests/examples.py:55: in test_known_bug
    raise ValueError(msg)
E   ValueError: Known issue
```
```

**Token cost:** ~35 tokens for traceback + fencing

**Argument for removal:**
- XFAIL are **morally PASS** - expected failures, not actionable
- Reason string provides sufficient context
- Traceback is redundant (failure is expected)
- Pytest doesn't show XFAIL details in default output
- TDD agents don't need to debug expected failures

**Proposed format:**
```markdown
### tests/examples.py::test_known_bug XFAIL

**Reason:** Bug #123
```

**Savings:** ~33 tokens per XFAIL (7 lines → 3 lines)

**Edge case:** `strict=True` XFAIL that passes becomes XPASS → shows in Failures with full context (correct behavior)

---

### 2. Bold Markup Optimization ✓ RECOMMENDED

**Current usage:**
- `**Summary:**` (4 tokens)
- `**Reason:**` (3 tokens per occurrence)

**Analysis:**
- Each `**` pair adds 1 token
- Summary line: remove `**` from "Summary:", use plain text
- Reason labels: remove entirely, inline reasons directly

**Current:**
```markdown
**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail

**Reason:** Bug #123
```

**Proposed:**
```markdown
Summary: 5/8 passed, 1 failed, 1 skipped, 1 xfail

Reason: Bug #123
```

**OR** (inline reasons - see nested list discussion):
```markdown
- test_known_bug XFAIL (Bug #123)
```

**Savings:**
- Summary: 2 tokens
- Reason: 2 tokens × N occurrences (2-3 per report = 4-6 tokens)
- **Total: 6-8 tokens per report**

---

### 3. Heading Count Integration MAYBE

**Current:**
```markdown
# Test Report

**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail
```

**Proposed:**
```markdown
# Test Report: 5/8 passed, 1 failed, 1 skipped, 1 xfail
```

**Analysis:**
- **Savings:** ~3 tokens (removes "**Summary:**" line)
- **Concern:** Very long heading for complex reports (20+ test categories)
- **Compromise:** Only for simple reports?

**Recommendation:** Skip this optimization. Summary line is semantically distinct from heading.

---

### 4. Nested List Density for PASS ✓ RECOMMENDED

**Current (verbose mode):**
```markdown
## Passes

- tests/examples.py::test_invalid_input[-False]
- tests/examples.py::test_invalid_input[x-True]
- tests/examples.py::test_simple
- tests/examples.py::test_validation_pass
- tests/examples.py::test_critical_path
```

**Proposed:**
```markdown
## Passes

- tests/examples.py
  - test_invalid_input[-False]
  - test_invalid_input[x-True]
  - test_simple
  - test_validation_pass
  - test_critical_path
```

**Analysis:**
- Removes repeated file path prefix: `tests/examples.py::` appears 5× (24 chars × 5 = 120 chars)
- Nested list adds: 1 parent + 5 children with 2-space indent
- **Net savings:** ~100 chars ≈ 25-30 tokens for 5 tests

**Real-world benefit:** Scales dramatically with larger test suites
- 50 tests in same file: ~500 chars = 125 tokens saved
- Multiple files: groups naturally

---

### 5. Nested List Density for SKIPPED/XFAIL ✓ RECOMMENDED

**Current:**
```markdown
### tests/examples.py::test_future_feature SKIPPED

**Reason:** Not implemented yet

### tests/examples.py::test_known_bug XFAIL

**Reason:** Bug #123
```

**Proposed:**
```markdown
## Skipped

- tests/examples.py
  - test_future_feature (Not implemented yet)

## Expected Failures (xfail)

- tests/examples.py
  - test_known_bug (Bug #123)
```

**Analysis:**
- Removes heading per test (3 lines → 1 line per test)
- Removes `**Reason:**` label (saves 2 tokens × N)
- Inlines reason in parentheses
- Groups by file path

**Savings per item:**
- Before: 5 lines, ~18 tokens
- After: 1 line, ~6 tokens
- **Net: 12 tokens per SKIPPED/XFAIL**

---

### 6. Section Heading Optimization

**Current:**
```markdown
## Failures
## Skipped
```

**Tokens:** `##` = 1 token, ` Failures` = 2 tokens, total = 3 tokens per heading

**Analysis:** Section headings are essential for structure. No optimization without semantic loss.

---

## Real-World Test Suite Patterns

**Progress display scaling:**
- 10 tests: `.Fsx... [100%]` (1 line, ~8 tokens)
- 100 tests: 5-6 lines of dots/letters (~40 tokens)
- 1000 tests: 50+ lines (~400 tokens)
- **Markdown:** 0 tokens (no progress display)

**Traceback depth:**
- Simple tests: 3-5 lines per failure
- Integration tests: 10-20 lines per failure (multiple call frames)
- Deep stacks: 50+ lines (framework internals)

**Session header:**
- Pytest always includes: platform, Python version, rootdir, plugins (~5 lines = 30 tokens)
- **Markdown:** 0 tokens

**Test summary footer:**
- Pytest: 2-3 lines (short test summary + final summary)
- **Markdown:** 1 line (consolidated)

---

## Optimization Strategy

### Phase 1: Low-Hanging Fruit (Immediate)

1. **Remove XFAIL tracebacks** (33 tokens per XFAIL)
2. **Remove bold markup on Summary/Reason** (6-8 tokens)
3. **Nested lists for SKIPPED/XFAIL** (12 tokens per item)

**Expected impact:** 50-80 token reduction for typical report

### Phase 2: Structural Improvements (Medium-term)

4. **Nested lists for PASS** (25-30 tokens per 5 tests)
5. **CommonMark fence safety** (use 4 backticks)

**Expected impact:** Scales with test count

### Phase 3: Format Validation (Ongoing)

6. **Benchmark automation** (script created: `scripts/benchmark.py`)
7. **Add regression test:** markdown default MUST NOT exceed pytest default

---

## Token Budget Analysis

**Target:** Markdown default ≤ Tuned pytest (180 tokens)

**Current:** 228 tokens

**Gap:** 48 tokens

**Proposed savings:**
- XFAIL traceback removal: ~33 tokens (1 XFAIL in examples.py)
- Bold markup: ~6 tokens
- SKIPPED nested list: ~12 tokens (1 SKIPPED)
- **Total: ~51 tokens**

**Projected:** 228 - 51 = **177 tokens** ✓ Under target

---

## Recommendations

1. ✅ **Implement Phase 1 optimizations immediately**
2. ✅ **Add benchmark to CI/CD** (fail if markdown > pytest)
3. ✅ **Test on diverse test suites** before finalizing
4. ⚠️ **Skip heading count integration** (marginal benefit, semantic loss)
5. ✅ **Document trade-offs** in design-decisions.md

---

## Open Questions

1. Should XFAIL have its own section or remain in Failures?
   - Current: Mixed in Failures (with XFAIL label)
   - Proposed: Separate "Expected Failures" section (clearer)

2. What verbosity level should be the baseline for "equivalent pytest"?
   - Default pytest (381 tokens) - includes headers, full output
   - Tuned pytest (180 tokens) - minimal, requires flags
   - **Recommendation:** Default pytest (fair comparison)

3. Should we preserve file path in nested lists when only one file?
   - Example: If all tests in `tests/examples.py`, show file path or omit?
   - **Recommendation:** Always show (consistency)
