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

## Validate release credentials before mutating, not after
- Anti-pattern: Checking `UV_PUBLISH_TOKEN`/upstream/`gh auth` only on the dry-run path, while the real path pushes and tags before reaching `uv publish`. A late failure strands a *public* tag with no artifact — recoverable only by deleting a published tag.
- Correct pattern: Every credential and remote the external phase needs is a precondition, checked before the version bump.
- Rationale: The push/tag/publish sequence has no transaction. Ordering is the only safety property available, so fail before the first irreversible step.

## `uv version` returns "name X.Y.Z", not "X.Y.Z"
- Anti-pattern: `version=$(uv version)` then matching `dist/*${version}*` — the pattern becomes `*pytest-markdown-report 0.2.0*` and never matches `pytest_markdown_report-0.2.0.tar.gz` (underscores, no space). Cleanup silently no-ops.
- Correct pattern: `uv version --short` for filenames/tags/globs; plain `uv version` only for human-facing messages.
- Rationale: Silent no-op, not an error. Stale artifacts accumulate in `dist/`, and bare `uv publish` globs all of `dist/` — so a dry-run's leftovers get published as a real release of a version that never existed.

## Careful agent behavior can itself create the hazard
- Observed: running `just release --dry-run` *to be safe* left 0.3.0 wheels in `dist/` that the next publish would have uploaded. Caution generated the artifact; it didn't prevent it.
- Correct pattern: after any dry-run or aborted release, inspect `dist/` before the real one. Don't assume self-reverting tooling actually reverted — verify.
