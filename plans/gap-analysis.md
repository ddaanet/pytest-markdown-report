# Gap Analysis: Why Markdown > Tuned Pytest

**Current:** Markdown default (228) vs Tuned pytest (180) = **48 token gap**

**User challenge:** Why are we worse than tuned pytest? That should not be.

---

## Line-by-Line Comparison

### Tuned Pytest (-q --tb=short --no-header) - 180 tokens, 13 lines

```
..Fsx...                                                                 [100%]
=================================== FAILURES ===================================
________________________________ test_edge_case ________________________________
tests/examples.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/examples.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
=========================== short test summary info ============================
FAILED tests/examples.py::test_edge_case - IndexError: list index out of range
1 failed, 5 passed, 1 skipped, 1 xfailed in 0.01s
```

**Content:**
- Progress display: 1 line
- FAILURES section: title + separator + traceback (10 lines)
- Short summary: title + failure line + counts (3 lines)
- **NO details for SKIPPED or XFAILED tests**

### Markdown Default - 228 tokens, 33 lines

```
# Test Report

**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail

## Failures

### tests/examples.py::test_edge_case FAILED

```python
tests/examples.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/examples.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```

### tests/examples.py::test_known_bug XFAIL

**Reason:** Bug #123

```python
tests/examples.py:55: in test_known_bug
    raise ValueError(msg)
E   ValueError: Known issue
```

## Skipped

### tests/examples.py::test_future_feature SKIPPED

**Reason:** Not implemented yet
```

**Content:**
- Title heading: 1 line
- Summary: 1 line
- FAILURES section: heading + 1 failure with traceback (9 lines)
- **XFAIL section: heading + traceback + reason (7 lines)** ← Tuned pytest shows NOTHING
- **SKIPPED section: heading + reason (5 lines)** ← Tuned pytest shows NOTHING
- Plus many blank lines for spacing

---

## Core Issue: Information Asymmetry

**Tuned pytest shows:**
- Failure tracebacks ONLY
- Summary counts (no details for skip/xfail)

**Markdown shows:**
- Failure tracebacks
- **XFAIL with full traceback** (tuned pytest: nothing)
- **SKIPPED with reason** (tuned pytest: nothing)

**The 48-token gap comes from showing information tuned pytest omits.**

---

## Overhead Breakdown

Where markdown adds tokens vs tuned pytest:

| Item | Tokens | Removable? |
|------|--------|------------|
| `# Test Report` heading | 3 | YES |
| `**Summary:**` label | 3 | YES (planned) |
| `## Failures` heading | 3 | MAYBE |
| `## Skipped` heading | 3 | MAYBE |
| `### test FAILED` heading | ~4 per test | PARTIAL |
| `**Reason:**` labels (×2) | 6 | YES (planned) |
| XFAIL traceback section | 33 | YES (planned) |
| SKIPPED detail section | ~15 | NO (information loss) |
| Code fences (````python`/``````) | 3 per block | NO (needed for rendering) |
| Blank lines (11 total) | ~11 | PARTIAL (some required for markdown) |
| Progress display | 0 | N/A (not shown) |

**Total identifiable overhead:** ~84 tokens

**Planned cuts (Phase 1):**
- XFAIL traceback: 33 tokens
- Bold labels: 9 tokens (Summary + 2× Reason)
- **Subtotal: 42 tokens**

**Still needed: 6 more tokens**

---

## Additional Cuts to Beat Tuned Pytest

**Option A: Remove title heading**
```
# Test Report  ← REMOVE THIS (saves 3 tokens)
```
Start directly with Summary line.

**Option B: Remove section headings when trivial**
```
## Failures  ← Could remove when only 1 section? (saves 3 tokens)
## Skipped  ← Could remove (saves 3 tokens)
```

**Option C: Flatten SKIPPED to single line**

Current (5 lines):
```
## Skipped

### tests/examples.py::test_future_feature SKIPPED

**Reason:** Not implemented yet
```

Proposed (1 line):
```
**Skipped:** tests/examples.py::test_future_feature (Not implemented yet)
```

Saves ~10 tokens

**Option D: Remove blank lines aggressively**

Some blank lines are for visual spacing, not markdown requirements. Could reduce from 11 to ~6.
Saves ~5 tokens.

---

## Recommendation: Aggressive Phase 1

To beat tuned pytest (180 tokens), we need **54 tokens of cuts**, not just 42.

**Revised Phase 1:**

1. **Remove XFAIL tracebacks** (33 tokens)
2. **Remove bold markup** (9 tokens)
3. **Remove `# Test Report` heading** (3 tokens)
4. **Remove section headings** (6 tokens for ## Failures, ## Skipped)
5. **Flatten SKIPPED format** (10 tokens)

**Total: 61 tokens**

**Result:** 228 - 61 = **167 tokens** ✓ Beats tuned pytest by 13 tokens

---

## Trade-offs

**What we lose:**
- Top-level document title
- Section structure (headings)
- Multi-line SKIPPED format

**What we keep:**
- Summary line
- Full failure tracebacks
- XFAIL reasons (without tracebacks)
- SKIPPED reasons (inline)
- Fenced code blocks for proper rendering

**New format would look like:**

```markdown
Summary: 5/8 passed, 1 failed, 1 skipped, 1 xfail

### tests/examples.py::test_edge_case FAILED

```python
tests/examples.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/examples.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```

### tests/examples.py::test_known_bug XFAIL

Reason: Bug #123

### tests/examples.py::test_future_feature SKIPPED

Reason: Not implemented yet
```

This is flatter, more compact, but still structured and readable.

---

## Question for User

**Do we accept these trade-offs to beat tuned pytest?**

OR

**Do we argue that showing XFAIL/SKIPPED details justifies being slightly larger than a format that omits them?**

The honest answer: Tuned pytest is hyper-minimal by design (`-q` flag means "quiet"). Beating it requires us to be equally aggressive with structure.
