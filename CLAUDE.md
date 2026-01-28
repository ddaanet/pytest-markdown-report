# Agent Instructions

@agent-core/fragments/workflows-terminology.md

---

## Documentation Structure

**Progressive discovery:** Don't preload all documentation. Read specific guides only when needed.

### Core Instructions
- **CLAUDE.md** (this file) - Agent instructions, workflows, communication rules

### Architecture & Design
- **dev/architecture.md** - Plugin internals and implementation details
- **dev/design-decisions.md** - Design rationale and trade-offs

### Current Work
- @session.md - Current session handoff context (update only on handoff)

---

## Communication Rules

@agent-core/fragments/communication.md

@agent-core/fragments/token-economy.md

**Additional communication rules:**
- **Use /commit skill** - Always invoke `/commit` skill when committing; it handles multi-line message format correctly
- **No estimates unless requested** - Do NOT make estimates, predictions, or extrapolations unless explicitly requested by the user. Report measured data only.

@agent-core/fragments/error-handling.md

@agent-core/fragments/bash-strict-mode.md

@agent-core/fragments/tmp-directory.md

## Session Management

@agent-core/fragments/execute-rule.md

@agent-core/fragments/delegation.md

@agent-core/fragments/tool-batching.md

---

## Project-Specific Rules

### Context Management

**session.md discipline:**
- Primary context file for current work state, handoffs, decisions, blockers
- Keep under ~100 lines - archive completed work to `plans/archive/`
- **Handoff protocol**: Update only at handoff (avoid mid-session churn)

**Information hierarchy:**
- **CLAUDE.md** - Persistent, long-lived information (architecture, commands, guidelines)
- **session.md** - Current session context, handoff notes, temporary analysis
- **plans/** - Implementation plans, code reviews, specifications

**When to create agents/ directory**: Not needed until project has multiple specialized roles, sustained multi-week development, or context files exceeding 200+ lines regularly.

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

# Test
just test               # Verify output expectations
just test --lf          # Re-run only failed tests
just test -v            # Verbose output
just test --pdb         # Drop into debugger on failures
```
