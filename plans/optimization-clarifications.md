# Optimization Clarifications

**Date:** 2026-01-09

These clarifications address ambiguities in the Opus consultation.

---

## 1. Empty Lines Between List Items

**Opus claim:** "Remove empty lines between list items in Passes section"

**Reality check:**

Current output (lines 37-41 of verbose mode):
```markdown
## Passes

- tests/examples.py::test_invalid_input[-False]
- tests/examples.py::test_invalid_input[x-True]
- tests/examples.py::test_simple
- tests/examples.py::test_validation_pass
- tests/examples.py::test_critical_path
```

**Clarification:** We do NOT currently produce empty lines between list items. This optimization is **NOT APPLICABLE** - the format is already optimal for markdown lists.

---

## 2. "Expected Failures" vs "XFail" Heading

**Opus suggestion:** Shorten "Expected Failures" to "XFail"

**Token count verification:**
```
## Expected Failures = 11 tokens
## XFail            = 11 tokens
```

**Clarification:** Both headings have **identical token counts**. No savings from this change.

**Additional consideration:**
- "Expected Failures" is clearer to users unfamiliar with pytest terminology
- "XFail" is more concise visually but doesn't save tokens
- **Recommendation:** Keep "Expected Failures" (or current "Failures" with XFAIL label) for clarity

---

## 3. Dropping Section Headings for Single-Item Sections

**Opus suggestion:** Remove section heading when only one item in that section

**Current format (single skipped test):**
```markdown
## Skipped

### tests/examples.py::test_future_feature SKIPPED

**Reason:** Not implemented yet
```

**Proposed format:**
```markdown
### tests/examples.py::test_future_feature SKIPPED

**Reason:** Not implemented yet
```

**Clarification:** This means removing the `## Skipped` heading line when there's only one skipped test.

**Token savings:** ~3-4 tokens per single-item section (heading + blank line)

**Trade-offs:**
- **Pro:** Token savings, less visual clutter
- **Con:** Inconsistent structure (sometimes have section, sometimes don't)
- **Con:** Harder to scan for section types
- **Con:** Parser complexity - need conditional logic based on count

**Example impact:**

Current structure (consistent):
```markdown
## Failures
<failures>

## Skipped
<single skip>

## Passes
<passes>
```

Proposed structure (conditional):
```markdown
## Failures
<failures>

### test.py::test_foo SKIPPED
<single skip - no section heading>

## Passes
<passes>
```

**Recommendation:** **SKIP this optimization**. Savings too small (3-4 tokens) for structural inconsistency introduced. Consistent section structure is more valuable for parsing and navigation.

---

## 4. Rerun Command Shortening

**Opus suggestion:** "Re-run failed" → "Rerun"

**Token savings:** 1 token (maybe 2)

**Clarification from user:** Loss of clarity not worth flat 1 token saving.

**Current format:**
```markdown
**Re-run failed:** `pytest --lf`
```

**Proposed format:**
```markdown
**Rerun:** `pytest --lf`
```

**Analysis:**
- "Re-run failed" is explicit about what will be rerun
- "Rerun" is ambiguous (rerun all? rerun what?)
- Savings: 1-2 tokens maximum
- This appears only in quiet mode and when failures exist

**Recommendation:** **SKIP this optimization**. User is correct - clarity more valuable than 1 token.

---

## Summary of Clarifications

| Optimization | Opus Claim | Reality | Recommendation |
|--------------|------------|---------|----------------|
| Empty lines in lists | Remove them | **Don't exist** | N/A - already optimal |
| XFail heading | Shorter = fewer tokens | **Same tokens (11)** | Keep current |
| Drop single-item sections | Saves 3-4 tokens | True | **SKIP** - inconsistent structure |
| Rerun shortening | Save 1 token | True | **SKIP** - clarity matters |

**Net result:** None of these four optimizations should be implemented.

**Focus remains on Phase 1:**
1. XFAIL traceback removal (~33 tokens)
2. Bold markup removal (~6-8 tokens)

**Total projected savings:** ~39-41 tokens → 228 - 40 = **188 tokens** (beats tuned pytest at 180)
