# Architecture

Plugin internals for pytest-markdown-report.

## Plugin Registration Flow

The plugin uses pytest's standard plugin registration mechanism and suppresses default
output:

1. `pytest_load_initial_conftests()` sets `--tb=short` as the default traceback style
2. `pytest_addoption()` registers CLI options (`--markdown-report`,
   `--markdown-rerun-cmd`)
3. `pytest_configure()` instantiates `MarkdownReport`, registers it with the plugin
   manager, and redirects stdout/stderr to suppress any remaining pytest output
4. `pytest_unconfigure()` cleans up the plugin registration

## Output Suppression Mechanism

The plugin completely suppresses pytest's console output using stream redirection:

1. **Stream Redirection**: Redirects `sys.stdout` and `sys.stderr` to a capture buffer
   in `_redirect_output()` (called from `pytest_configure()`) to suppress pytest's
   default output
2. **Output Restoration**: Restores the original streams in `_restore_output()` (called
   from `pytest_sessionfinish()`) before printing the markdown report

## Report Generation Pipeline

The `MarkdownReport` class orchestrates report generation:

1. **Output Redirection** (`_redirect_output`): Captures pytest's stdout/stderr to
   suppress default output
2. **Collection Phase** (`pytest_runtest_logreport`): Captures test reports from all
   phases (call, setup, teardown) when outcome is non-passing
3. **Categorization** (`pytest_sessionfinish`): Sorts reports into
   passed/failed/skipped/xfailed/xpassed buckets
4. **Formatting** (`pytest_sessionfinish`): Generates markdown based on verbosity and -r flags:
   - **Quiet mode (-q)**: Summary + optional rerun command
   - **Default mode**: Summary + failures (respects -r flags for skipped/xfail sections)
   - **Verbose mode (-v)**: Summary + all sections (failures, skipped, xfail, passes)
5. **Output Restoration** (`pytest_sessionfinish`): Restores stdout/stderr and prints
   markdown report to console, optionally saves to file

## Report Categorization Logic

Test outcomes are categorized and displayed in separate sections:

- `failed`: Test assertion failures (call phase) → **## Failures** section
- `errors`: Setup/teardown/collection errors → **## Errors** section
- `xfailed`: Expected failures (`@pytest.mark.xfail` that fail) → **## Failures** section
- `xpassed`: Unexpected passes (xfail tests that pass) → **## Failures** section (always shown)
- `skipped`: Tests marked skip or conditional skips → **## Skipped** section
- `passed`: Successful tests → **## Passes** section
- `passed_with_output`: Passing tests with captured output → **## Passes (with output)** section
- `warnings`: Pytest warnings → **## Warnings** section

**Display modes:**
- **Default mode**: Respects -r flags (defaults to fEX: failures + errors + xpassed)
- **Verbose mode (-v)**: Always shows all sections regardless of -r flags
- **Quiet mode (-q)**: Shows only summary line

**Available -r flags:**
- `f` = failed tests (default: shown)
- `E` = errors in setup/teardown (default: shown)
- `s` = skipped tests
- `x` = xfailed tests
- `X` = xpassed tests (default: shown)
- `p` = passed tests
- `P` = passed tests with captured output
- `w` = pytest warnings
- `a` = all except passes (shortcut for fEsxXw)
- `A` = all including passes (shortcut for fEsxXpPw)
- `N` = none (suppress all sections except summary)

**Examples:**
```bash
pytest                       # Default: failures + errors + xpassed
pytest -rs                   # Add skipped section
pytest -rx                   # Add xfailed section
pytest -rsx                  # Show skipped + xfailed
pytest -rp                   # Add passes
pytest -ra                   # Show all except passes
pytest -rA                   # Show everything
pytest -rN                   # Summary only (like -q)
pytest -rf                   # Only failures (hide errors)
pytest -rE                   # Only errors (hide failures)
```

**Section order:** Summary → Errors → Failures → Skipped → Warnings → Passes → Passes (with output)

## Resource Management

The plugin manages output streams to ensure clean operation:

- **Output redirection**: Redirects `sys.stdout` and `sys.stderr` during test execution
- **Idempotent restoration**: `_restore_output()` can be called multiple times safely
- **Crash recovery**: `pytest_unconfigure()` calls `_restore_output()` to handle
  interrupts (Ctrl+C)
- **Buffer cleanup**: StringIO buffer explicitly closed to prevent memory leaks
- **Error handling**: File I/O errors handled gracefully without crashing
