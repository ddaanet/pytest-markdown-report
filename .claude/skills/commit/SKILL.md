---
name: commit
description: Create a git commit following project conventions.
---

# Skill: commit

## Project Commit Message Style

- Short, dense, structured
- Omit needless words
- Omit numbers (test counts, line counts, task counts, etc.)
- Imperative mood

**Good:** `Add handoff skill for session.md updates`
**Bad:** `Add handoff skill that updates session.md with 3 sections for completed tasks, pending tasks, and blockers`

**Good:** `Fix error categorization in plugin`
**Bad:** `Fix error categorization - updated 4 files, 127 lines changed, all 14 tests pass`

## Technical Note

Use double-quoted multi-line string, not heredoc (heredocs fail in sandbox):
```bash
git commit -m "First line

Body here"
```
Escape `$` and backticks in message if present.

---

Now invoke `/commit-commands:commit` applying the style above.
