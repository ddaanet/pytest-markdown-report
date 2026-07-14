# Agent Instructions

---

## Documentation Structure

**Progressive discovery:** Don't preload all documentation. Read specific guides only when needed.

### Core Instructions
- **CLAUDE.md** (this file) - Agent instructions, workflows, project rules

### Architecture & Design

Pytest plugin (`src/pytest_markdown_report/plugin.py`) replacing pytest's console output with token-efficient markdown for LLM/TDD agents.

- **dev/architecture.md** - Plugin internals and implementation details
- **dev/design-decisions.md** - Design rationale and trade-offs

### Current Work
- @agents/session.md - Current session handoff context (update only on handoff)
- @agents/learnings.md - Accumulated learnings (append-only, soft limit 80 lines)

---

## Project-Specific Rules

### Context Management

**session.md discipline:**
- Primary context file for current work state, handoffs, decisions, blockers
- Keep under ~100 lines - archive completed work to `plans/archive/`
- **Handoff protocol**: Update only at handoff (avoid mid-session churn)

**Information hierarchy:**
- **CLAUDE.md** - Persistent, long-lived information (architecture, commands, guidelines)
- **agents/session.md** - Current session context, handoff notes, temporary analysis
- **agents/learnings.md** - Accumulated learnings and insights
- **plans/** - Implementation plans, code reviews, specifications

### Opus Orchestration

**Model selection:**
- Simple mechanical tasks → write script if shorter than prompting haiku
- Simple cognitive tasks → haiku
- Use sonnet when promptable in fewer tokens than haiku

**Sub-agent usage:**
- Use sub-agents to distill inputs; be concise in all outputs
- Sub-agents write dense, comprehensive, structured factual reports to file for reference
- Remind sub-agents to prefer specialized tools (Read, Write, Edit, Glob, Grep) over Bash equivalents

**Workflow:**
- Write designs to `plans/` before validation (cheaper to update file than re-output)
- Temporary exploratory files go to `tmp/`

### Environment

Use `pytest` directly (not `uv run` or `.venv/bin/pytest`).

### Testing

**Output Verification**: Always run `just test` after making changes to verify output format matches expectations. This automated test suite validates quiet/default/verbose modes and collection error handling.

**Token Count Verification**: Do not guess token counts. Always use `claudeutils tokens sonnet <file>` to verify actual token usage.

### Commands

```bash
# Install
pip install .

# Dev loop (format + check + test)
just dev

# Test
just test               # Verify output expectations
just test --lf          # Re-run only failed tests
just test -v            # Verbose output
just test --pdb         # Drop into debugger on failures

# Quality gates
just check              # ruff + docformatter + mypy
just benchmark          # Token-efficiency benchmark vs default pytest output
just release            # patch bump (--dry-run / --rollback / minor|major); blocked inside Claude Code
```
