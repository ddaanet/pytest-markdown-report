# pytest-markdown-report

Token-efficient markdown test reports for LLM-based TDD agents. Replaces pytest's default console output with markdown-formatted results.

## Installation

Add to the development dependencies of your project.

```bash
pip install pytest-markdown-report
```

```bash
uv add --dev pytest-markdown-report
```

```bash
poetry add --group dev pytest
```

## Usage

Once installed, the plugin automatically replaces pytest's console output with markdown format:

```bash
# Markdown output to console (default behavior)
pytest

# Also save to file
pytest --markdown-report=report.md
```

### Verbosity Modes

**Default**: Summary + failures
```bash
pytest
```

**Verbose (`-v`)**: Add passed test list
```bash
pytest -v
```

**Quiet (`-q`)**: Summary + rerun suggestion only
```bash
pytest -q
```

### Options

**Save to file**:
```bash
pytest --markdown-report=report.md
```

**Custom rerun command**:
```bash
pytest --markdown-rerun-cmd="just test --lf"
```

**Disable rerun suggestion**:
```bash
pytest --markdown-rerun-cmd=""
```

## Output Format

### Default Mode
```markdown
# Test Report

**Summary**: 2/5 passed | 3 failed | 0 skipped

## Failures

### test_validation.py::test_invalid_input[empty] ✗
**Error**: AssertionError
```python
>       assert validate(input) == expected
E       AssertionError: assert True == False

test_validation.py:42: AssertionError
```
```

### Verbose Mode (-v)
Adds passed test list after failures:
```markdown
## Passes
- test_feature.py::test_critical_path ✓
- test_basic.py::test_simple ✓
```

### Quiet Mode (-q)
```markdown
**Summary**: 2/5 passed | 3 failed | 0 skipped

Re-run failed: `just test --lf`
```

## Design Goals

- **Token efficiency**: ~40% reduction vs verbose markdown
- **Agent-friendly**: Full tracebacks with assertion introspection
- **TDD workflow**: Minimal noise during green phase, detailed failures for debugging
- **Configurable**: Adapt rerun commands to your workflow (`just`, custom recipes)

## Edge Cases

**Parametrized tests**: Parameter values in test name `[empty]`

**Skipped tests**: `⊘` symbol with skip reason, no traceback

**xfail**: `⚠` symbol distinguishes expected failures

**Captured output**: Included under failures when present

## Integration

The plugin automatically formats all pytest output as markdown. Use with role-specific agents:

```bash
# Implementation agent sees failures only (console)
pytest

# Review agent sees all passes (console + file)
pytest -v --markdown-report=review.md --markdown-rerun-cmd="just role-review"

# Minimal output for CI/CD pipelines
pytest -q
```

**Note**: Use `pytest --durations=N` separately for performance analysis (this will also be in markdown format).

## License

MIT
