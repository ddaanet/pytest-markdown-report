# Design: Session Log Extraction

Two-part design separating generic extraction (claudeutils) from workflow-specific processing (project-local).

---

## Part 1: claudeutils session-log (Generic Primitive)

### Purpose
Extract raw session data from Claude Code logs. No workflow assumptions. Pure data extraction.

### Command Interface

```bash
# Extract session as JSON (primary format)
claudeutils session-log <session-id> --format json

# Extract as markdown (human-readable)
claudeutils session-log <session-id> --format markdown

# Auto-detect current session from cwd
claudeutils session-log --current

# Filter by time range
claudeutils session-log <session-id> --after "2026-01-10T10:00:00"

# Expand subagent sessions inline
claudeutils session-log <session-id> --expand-agents
```

### Output Schema (JSON)

```json
{
  "session_id": "abc123",
  "project_path": "/path/to/project",
  "started": "2026-01-10T10:00:00Z",
  "ended": "2026-01-10T10:30:00Z",
  "summary": {
    "tool_calls": {"Read": 10, "Edit": 5, "Write": 1, "Bash": 8, "Task": 2},
    "user_messages": 5,
    "assistant_messages": 12,
    "files_touched": ["src/foo.py", "tests/test_foo.py"]
  },
  "timeline": [
    {
      "timestamp": "2026-01-10T10:05:00Z",
      "type": "tool_use",
      "tool": "Read",
      "input": {"file_path": "/path/to/file.py"},
      "result_summary": "200 lines read"
    },
    {
      "timestamp": "2026-01-10T10:06:00Z",
      "type": "tool_use",
      "tool": "Bash",
      "input": {"command": "pytest tests/ -v"},
      "exit_code": 1,
      "result_summary": "Output: 500 chars"
    },
    {
      "timestamp": "2026-01-10T10:07:00Z",
      "type": "tool_use",
      "tool": "Edit",
      "input": {"file_path": "/path/to/file.py", "old_string": "...", "new_string": "..."},
      "result_summary": "Edit applied"
    },
    {
      "timestamp": "2026-01-10T10:08:00Z",
      "type": "user_message",
      "content": "Don't batch update tests",
      "has_tool_results": false
    },
    {
      "timestamp": "2026-01-10T10:09:00Z",
      "type": "tool_use",
      "tool": "Task",
      "input": {"subagent_type": "general-purpose", "model": "haiku", "prompt": "..."},
      "subagent_id": "def456",
      "subagent_session": null
    }
  ],
  "files": {
    "src/foo.py": {"reads": 2, "edits": 1},
    "tests/test_foo.py": {"reads": 1, "edits": 1, "writes": 0}
  },
  "user_interventions": [
    {
      "timestamp": "2026-01-10T10:08:00Z",
      "type": "message",
      "content": "Don't batch update tests"
    },
    {
      "timestamp": "2026-01-10T10:10:00Z",
      "type": "tool_denial",
      "tool": "Edit",
      "file": "README.md"
    }
  ]
}
```

### Output Format (Markdown)

```markdown
# Session Log: {session_id}

**Project:** {project_path}
**Duration:** {started} → {ended}

## Summary
- Tool calls: Read(10), Edit(5), Write(1), Bash(8), Task(2)
- Files touched: 3
- User interventions: 2

## Timeline

### 10:05:00 - Read
`/path/to/file.py` (200 lines)

### 10:06:00 - Bash
`pytest tests/ -v`
Exit code: 1

### 10:07:00 - Edit
`/path/to/file.py` lines 45-47

### 10:08:00 - User
> Don't batch update tests

### 10:09:00 - Task (haiku)
"Fix type errors"

## Files
| File | Reads | Edits | Writes |
|------|-------|-------|--------|
| src/foo.py | 2 | 1 | 0 |
| tests/test_foo.py | 1 | 1 | 0 |

## User Interventions
| Time | Type | Detail |
|------|------|--------|
| 10:08 | message | "Don't batch update tests" |
| 10:10 | tool_denial | Edit README.md |
```

### Implementation

**Data Source:** `~/.claude/projects/{encoded_path}/sessions/{session_id}.json`

**Phases:**
1. **Session parsing** (~150 LOC) - Read JSON, extract messages
2. **Timeline construction** (~100 LOC) - Order tool calls, extract parameters
3. **File aggregation** (~50 LOC) - Summarize per-file operations
4. **Output formatting** (~100 LOC) - JSON and markdown renderers

**Total:** ~400 LOC, 15 tests

### What This Does NOT Do
- Parse test output (pytest, jest, etc.)
- Detect TDD cycles
- Categorize user feedback
- Make workflow judgments

---

## Part 2: Project-Specific Processing (pytest-md example)

### Purpose
Transform generic session data into workflow-specific analysis. Lives in project repo, not claudeutils.

### Location
`scripts/process-session.py` or similar project-local script.

### Inputs
1. Generic session JSON from `claudeutils session-log`
2. Structured session log from `plans/session-log-{date}.md` (written by execute:tdd skill)
3. TDD plan document

### Processing Steps

```python
# Pseudocode for project-specific processor

def process_tdd_session(session_json, session_log_md, plan_md):
    # 1. Parse structured log (project-specific format)
    cycles = parse_session_log(session_log_md)

    # 2. Cross-reference with raw timeline
    for cycle in cycles:
        cycle.tool_calls = find_tool_calls_in_range(session_json, cycle.timestamp)

    # 3. Compare against plan
    planned_cycles = parse_plan(plan_md)
    compliance = compare_execution_to_plan(cycles, planned_cycles)

    # 4. Output analysis-ready markdown
    return render_analysis_input(cycles, compliance)
```

### Structured Session Log Format (execute:tdd output)

```markdown
### Cycle X.Y: [name] [timestamp]
- Status: RED_VERIFIED | GREEN_VERIFIED | STOP_CONDITION | REGRESSION
- Test command: `[exact command run]`
- RED result: [FAIL as expected | PASS unexpected | N/A for regression]
- GREEN result: [PASS | FAIL - reason]
- Regression check: [N/N passed | N failures - list]
- Files modified: [list with line ranges]
- Stop condition: [none | description]
- Decision made: [none | description with rationale]
```

### Output (for review:analysis skill)

```markdown
# Session Analysis Input

## Execution Summary
- Cycles planned: 7
- Cycles completed: 5
- Cycles skipped: 2 (1.3, 1.4)

## Cycle Details
| Cycle | Status | RED | GREEN | Regression | Notes |
|-------|--------|-----|-------|------------|-------|
| 1.1 | complete | ✓ | ✓ | 26/26 | - |
| 1.2 | complete | ✓ | ✓ | 26/26 | - |
| 1.3 | skipped | - | - | - | Already works |

## Deviations
- Cycle 1.5 executed before 1.3, 1.4 (order violation)
- 11 tests batch-updated (TDD violation)

## Raw Session Data
[Link to full session JSON or inline summary]
```

---

## Integration

```
execute:tdd (Haiku)
    ↓ writes
plans/session-log-{date}.md (structured)
    +
~/.claude/projects/.../sessions/*.json (raw)
    ↓ extracted by
claudeutils session-log --format json (generic)
    ↓ processed by
scripts/process-session.py (project-specific)
    ↓ consumed by
review:analysis (Sonnet)
    ↓ produces
Analysis + recommendations
    ↓ consumed by
review:updates (Opus)
```

---

## Open Questions

1. **Subagent expansion:** Inline or separate extractions? (claudeutils decision)

2. **Diff inclusion:** Should claudeutils include Edit diffs in output, or just metadata? (Diffs can be large)

3. **Streaming sessions:** How to handle sessions still in progress?

---

## Implementation Priority

**claudeutils (generic):** Implement first, independently useful for any Claude Code project.

**Project processor:** Implement per-project as needed. pytest-md can be reference implementation.
