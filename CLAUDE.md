# Agent Instructions

Pytest plugin (`src/pytest_markdown_report/plugin.py`) replacing pytest's console
output with token-efficient markdown for LLM/TDD agents.

- **dev/architecture.md** - Plugin internals and implementation details
- **dev/design-decisions.md** - Design rationale and trade-offs

## Environment

Use `pytest` directly (not `uv run` or `.venv/bin/pytest`).

## Testing

**Output Verification**: Always run `just test` after making changes to verify output format matches expectations. This automated test suite validates quiet/default/verbose modes and collection error handling.

**Token Count Verification**: Do not guess token counts. Always use `edify tokens --model sonnet <file>` to verify actual token usage.

## Commands

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
just release            # patch bump (--dry-run / --rollback / minor|major); publishes to PyPI + GitHub
```
