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
# Run all tests with markdown console output (default behavior)
pytest

# Run tests verbosely (includes passed tests in report)
pytest -v

# Run tests quietly (summary + rerun suggestion only, no live progress)
pytest -q

# Run a single test
pytest test_example.py::test_simple

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
1. `pytest_addoption()` registers CLI options (`--markdown-report`, `--markdown-rerun-cmd`)
2. `pytest_cmdline_preparse()` adds `-p no:terminal` to disable pytest's terminal reporter
3. `pytest_configure()` instantiates `MarkdownReport`, registers it with the plugin manager, and redirects stdout/stderr to suppress any remaining pytest output
4. `pytest_unconfigure()` cleans up the plugin registration

### Output Suppression Mechanism
The plugin completely replaces pytest's console output using a two-pronged approach:
1. **Terminal Reporter Suppression**: Uses `-p no:terminal` flag to prevent pytest's terminal reporter from loading
2. **Stream Redirection**: Redirects `sys.stdout` and `sys.stderr` to a capture buffer in `pytest_configure()` to suppress any remaining pytest output, then restores the original streams in `pytest_sessionfinish()` to display the markdown report

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
- `skipped`: Tests marked with `@pytest.mark.skip` or conditional skips
- `xfailed`: Expected failures (`@pytest.mark.xfail` that fail as expected)
- `xpassed`: Unexpected passes (xfail tests that pass, counted as failures in summary)
- `failed`: Regular test failures
- `passed`: Successful tests

### Error Extraction
`_extract_error_type()` parses longreprtext to find lines starting with "E       " that contain "Error" to extract the exception type (e.g., "AssertionError", "ValueError").

## Key Design Decisions

**Token Efficiency**: The plugin minimizes token usage by:
- Showing only failures by default (not passed tests)
- Using symbols (✗, ✓, ⊘, ⚠) instead of verbose status text
- Condensing summary to single line format

**Verbosity Modes**: Three modes controlled by pytest's `-v`/`-q` flags allow adaptation to different agent workflows (implementation vs. review).

**Rerun Integration**: The `--markdown-rerun-cmd` option enables custom workflow integration (e.g., `just` recipes) while defaulting to `pytest --lf`.
