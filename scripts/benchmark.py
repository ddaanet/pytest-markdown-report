#!/usr/bin/env python3
"""Benchmark pytest output formats for token efficiency.

Usage:
    ./scripts/benchmark.py tests/examples.py
    ./scripts/benchmark.py tests/examples.py tests/test_edge_cases.py
"""

import subprocess
import sys
from pathlib import Path


def run_pytest(test_module: str, *args: str, disable_plugin: bool = False) -> str:
    """Run pytest and capture output."""
    # Find pytest in venv
    venv_pytest = Path(".venv/bin/pytest")
    pytest_cmd = str(venv_pytest) if venv_pytest.exists() else "pytest"

    env = {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"} if disable_plugin else {}
    cmd = [pytest_cmd, test_module, *args]

    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        env={**subprocess.os.environ, **env} if env else None,
    )
    return result.stdout + result.stderr


def count_tokens(content: str) -> int:
    """Count tokens using claudeutils."""
    # Write to temp file
    temp_path = Path("tmp/benchmark_temp.txt")
    temp_path.parent.mkdir(exist_ok=True)
    temp_path.write_text(content)

    # Count tokens
    result = subprocess.run(
        ["claudeutils", "tokens", "sonnet", str(temp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    # Parse output: "path: N tokens"
    for line in result.stdout.split("\n"):
        if "tokens" in line and str(temp_path) in line:
            return int(line.split()[-2])

    raise ValueError(f"Could not parse token count from: {result.stdout}")


def benchmark_format(name: str, output: str) -> dict:
    """Benchmark a single output format."""
    tokens = count_tokens(output)
    lines = output.count("\n")
    return {
        "name": name,
        "tokens": tokens,
        "lines": lines,
        "output": output,
    }


def main() -> None:
    """Run benchmark comparisons for different pytest output formats."""
    if len(sys.argv) < 2:
        sys.exit(1)

    test_modules = sys.argv[1:]

    # Define formats to benchmark
    formats = [
        ("1. Default pytest", [], True),
        (
            "2. Tuned pytest (-q --tb=short --no-header)",
            ["-q", "--tb=short", "--no-header"],
            True,
        ),
        ("3. Verbose tuned pytest (-v --tb=short)", ["-v", "--tb=short"], True),
        ("4. Markdown default", [], False),
        ("5. Markdown verbose (-v)", ["-v"], False),
        ("6. Markdown quiet (-q)", ["-q"], False),
    ]

    results = []

    for name, args, disable_plugin in formats:
        output = run_pytest(
            test_modules[0], *args, *test_modules[1:], disable_plugin=disable_plugin
        )
        result = benchmark_format(name, output)
        results.append(result)

        # Save to file
        test_file = test_modules[0].replace("/", "-").replace(".py", "")
        name_prefix = name.split(".")[0].strip()
        filename = f"tmp/{name_prefix}-{test_file}.txt"
        Path(filename).write_text(output)

    # Print results table

    baseline = results[0]["tokens"]
    tuned_baseline = results[1]["tokens"]

    for result in results:
        tokens = result["tokens"]

        # Calculate percentages
        (
            f"{((tokens - baseline) / baseline * 100):+.0f}%"
            if tokens != baseline
            else "baseline"
        )
        (
            f"{((tokens - tuned_baseline) / tuned_baseline * 100):+.0f}%"
            if tokens != tuned_baseline
            else "baseline"
        )

    # Check if markdown is larger than pytest
    markdown_default = results[3]["tokens"]
    pytest_default = results[0]["tokens"]

    if markdown_default > pytest_default:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
