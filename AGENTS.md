# AGENTS.md

This file provides guidance to AI coding agents when working with code in this
repository.

## Developer Documentation

- `dev/architecture.md` - Plugin internals and implementation details
- `dev/design-decisions.md` - Design rationale and trade-offs

## Commands

### Installation

```bash
pip install .
```

### Environment Notes

Use `pytest` directly (not `uv run` or `.venv/bin/pytest`).

Use `/commit-commands:commit` to commit changes.

### Running Tests

```bash
# Verify output expectations (automated test suite) - recommended
just test

# Pass additional pytest args to just test
just test --lf          # Re-run only failed tests
just test -v            # Verbose output
just test --pdb         # Drop into debugger on failures
```

## Agent Guidelines

### Persistent vs Temporary Information

**CRITICAL**: AGENTS.md is for persistent, long-lived information only.

- **Do put in AGENTS.md**: Architecture, commands, design principles, testing guidelines
- **Do NOT put in AGENTS.md**: Current plans, active tasks, session-specific context,
  implementation details

**Current plans and tasks belong in:**

- `plans/` directory - Implementation plans, code reviews, specifications
- `session.md` - Current session context, handoff notes, temporary analysis

**REMEMBER Directive**: When you see "REMEMBER:" in user messages, add the content to
this AGENTS.md file ONLY if it's persistent information (architecture, commands,
guidelines). If it's about current work or plans, put it in `session.md` or `plans/`
instead.

### Context Management

1. **session.md** is the primary context file for:
   - Current work state (what's in progress)
   - Handoff notes for next agent
   - Recent decisions with rationale
   - Known blockers

2. **Size discipline**: Keep session.md under ~100 lines
   - When it grows beyond this, archive completed work to `plans/archive/` or delete
   - Preserve only: current state, next actions, recent decisions, blockers

3. **Flushing strategy**:
   - After completing a feature/fix: summarize outcome in 1-2 lines, delete details
   - After multi-day work: archive full context to `plans/archive/{date}-session.md`
   - Keep session.md focused on "what does the next agent need to know?"

4. **When to create agents/ directory**: Not needed until project has:
   - Multiple specialized agent roles
   - Sustained multi-week development
   - Context files exceeding 200+ lines regularly
   - Reference: `claudeutils/agents/` for full architecture example

**Handoff Protocol**: When told "handoff", immediately update `session.md` with:
- Completed tasks this session
- Pending tasks remaining
- Any blockers or gotchas

Avoid churn: do not update session.md during the session, only at handoff.

### Opus Orchestration

**Model selection:**
- Simple mechanical tasks → write a script if shorter than prompting haiku (saves opus output tokens)
- Simple cognitive tasks → use haiku
- Use sonnet when it can be prompted in fewer tokens than haiku
- Sonnet writing a script instead of delegating to haiku is also valid

**Sub-agent usage:**
- Use sub-agents to distill inputs; be concise in all outputs
- Sub-agents write dense, comprehensive, structured factual reports to file for reference
- Remind sub-agents to prefer specialized tools (Read, Write, Edit, Glob, Grep) over Bash equivalents
- For file access outside current directory, remind sub-agents to combine all access in a single multi-line script (one approval instead of many)

**Workflow:**
- Write design to `plans/` before validation (cheaper to update a file than re-output)
- Temporary exploratory files go to `tmp/`
- Once you have enough information to evaluate options for open issues, start user validation conversation

### Testing Guidelines

**Output Verification**: Always run `pytest tests/test_output_expectations.py -v` after
making changes to verify output format matches expectations. This automated test suite
validates quiet/default/verbose modes and collection error handling.

**Token Count Verification**: Do not guess token counts. Always use
`claudeutils tokens sonnet <file>` to verify actual token usage.

## Documentation Organization

**File naming conventions:**

**Root-level files** (UPPERCASE.md):

- `AGENTS.md` - Persistent agent guidance (this file)
- `README.md` - Project overview and user documentation

**Session context** (lowercase-dash.md):

- `session.md` - Current session notes and handoff context

**Developer documentation** (`dev/`):

- `dev/architecture.md` - Plugin internals and implementation details
- `dev/design-decisions.md` - Design rationale and trade-offs

**Plans directory** (`plans/`):

- Implementation plans (phase-N-*.md)
- Code reviews (code-review.md, code-review-YYYY-MM-DD.md)
- Specifications and design documents

**Directory structure:**

```
pytest-markdown-report/
├── AGENTS.md              # Persistent agent guidance
├── README.md              # User documentation
├── session.md             # Current session context
├── dev/                   # Developer documentation
│   ├── architecture.md    # Plugin internals
│   └── design-decisions.md # Design rationale
├── plans/                 # Implementation plans and reviews
│   └── *.md               # Plan files
└── src/                   # Source code
```
