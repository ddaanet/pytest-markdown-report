# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

`pytest-markdown-report` is a pytest plugin that replaces pytest's default console output with token-efficient markdown test reports optimized for LLM-based TDD agents. The plugin completely suppresses pytest's standard terminal output and displays markdown-formatted results instead, with live test progress during execution and configurable verbosity levels.

## Commands

### Installation
```bash
pip install .
```

### Running Tests
```bash
# Verify output expectations (automated test suite) - recommended
just test

# Pass additional pytest args to just test
just test --lf          # Re-run only failed tests
just test -vv           # Very verbose output
just test --pdb         # Drop into debugger on failures

# Run example tests with markdown console output (default behavior)
pytest tests/test_example.py

# Run tests verbosely (includes passed tests in report)
pytest tests/test_example.py -v

# Run tests quietly (summary + rerun suggestion only, no live progress)
pytest tests/test_example.py -q

# Run a single test
pytest tests/test_example.py::test_simple

# Re-run only failed tests
pytest --lf

# Also save markdown report to a file
pytest --markdown-report=report.md

# Custom rerun command in report
pytest --markdown-rerun-cmd="just test --lf"
```

## Architecture

### Plugin Registration Flow
The plugin uses pytest's standard plugin registration mechanism and suppresses default output:
1. `pytest_load_initial_conftests()` sets `--tb=short` as the default traceback style
2. `pytest_addoption()` registers CLI options (`--markdown-report`, `--markdown-rerun-cmd`)
3. `pytest_configure()` instantiates `MarkdownReport`, registers it with the plugin manager, and redirects stdout/stderr to suppress any remaining pytest output
4. `pytest_unconfigure()` cleans up the plugin registration

### Output Suppression Mechanism
The plugin completely suppresses pytest's console output using stream redirection:
1. **Stream Redirection**: Redirects `sys.stdout` and `sys.stderr` to a capture buffer in `_redirect_output()` (called from `pytest_configure()`) to suppress pytest's default output
2. **Output Restoration**: Restores the original streams in `_restore_output()` (called from `pytest_sessionfinish()`) before printing the markdown report

### Report Generation Pipeline
The `MarkdownReport` class orchestrates report generation:

1. **Output Redirection** (`_redirect_output`): Captures pytest's stdout/stderr to suppress default output
2. **Collection Phase** (`pytest_runtest_logreport`): Captures test reports during the "call" phase (or "setup" for skipped tests)
3. **Categorization** (`pytest_sessionfinish`): Sorts reports into passed/failed/skipped/xfailed/xpassed buckets
4. **Formatting** (`pytest_sessionfinish`): Generates markdown based on verbosity mode:
   - **Quiet mode**: Summary + optional rerun command
   - **Default mode**: Summary + failures section
   - **Verbose mode**: Summary + failures + passes list
5. **Output Restoration** (`pytest_sessionfinish`): Restores stdout/stderr and prints markdown report to console, optionally saves to file

### Report Categorization Logic
Test outcomes are categorized with specific handling:
- `skipped`: Tests marked with `@pytest.mark.skip` or conditional skips (displays reason)
- `xfailed`: Expected failures (`@pytest.mark.xfail` that fail as expected, displays reason from decorator)
- `xpassed`: Unexpected passes (xfail tests that pass, counted as failures in summary)
- `failed`: Regular test failures (displays full traceback in code block)
- `passed`: Successful tests (only shown in verbose mode)

## Key Design Decisions

**Token Efficiency**: The plugin minimizes token usage by:
- Showing only failures by default (not passed tests)
- Using text labels (FAILED, SKIPPED, XFAIL) instead of Unicode symbols (saves 1 token per status vs ✗, ⊘, ⚠)
- Condensing summary to single line format with comma separators
- Using `--tb=short` by default for concise tracebacks
- Placing colons inside bold markers (`**Label:**` vs `**Label**:` saves 1 token per label)
- Note: Current implementation escapes markdown special characters in reasons, which adds ~11% token overhead (see session.md for analysis)

**Verbosity Modes**: Three modes controlled by pytest's `-v`/`-q` flags allow adaptation to different agent workflows (implementation vs. review).

**Rerun Integration**: The `--markdown-rerun-cmd` option enables custom workflow integration (e.g., `just` recipes) while defaulting to `pytest --lf`.

## Agent Guidelines

**Output Verification**: Always run `pytest tests/test_output_expectations.py -v` after making changes to verify output format matches expectations. This automated test suite validates quiet/default/verbose modes and collection error handling.

**Token Count Verification**: Do not guess token counts. Always use `claudeutils tokens sonnet <file>` to verify actual token usage.

**REMEMBER Directive**: When you see "REMEMBER:" in user messages, add the content to this AGENTS.md file in this section.

**Handoff Protocol**: When asked to handoff to another agent, write context for the following agent to `session.md` in the repository root.
