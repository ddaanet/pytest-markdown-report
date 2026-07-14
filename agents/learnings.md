# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

**Test naming with # noqa for readability:**
- Anti-pattern: Renaming tests to satisfy linters when capital letters improve readability
- Correct pattern: Use `# noqa: N802` (functions) or `# noqa: N806` (variables) to preserve meaningful names
- Rationale: Test names like `test_rA_flag_shows_everything` and `actual_vrN` mirror pytest flags (`-rA`, `-vrN`), making tests self-documenting. Sacrificing readability for linter compliance reduces code clarity. Selective noqa preserves intent.

## Commit Gate A: stale session → invoke /handoff --commit
- Anti-pattern: Writing session.md directly during `/commit` when Gate A detects staleness
- Correct pattern: Invoke `/handoff --commit` which runs full handoff protocol then tail-calls `/commit`. Commit still happens, no user intervention needed.
- Rationale: `/handoff` runs learnings consolidation, invalidation checks, jobs.md, session size checks. The `--commit` flag chains commit after handoff completes.
