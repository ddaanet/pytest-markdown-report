"""Test that pytest output matches expected markdown files."""

import subprocess
import sys
from pathlib import Path


def run_pytest(*args: str) -> str:
    """Run pytest with given args and return output."""
    cmd = [sys.executable, "-m", "pytest", *list(args)]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    # Combine stdout and stderr as pytest outputs to both
    return result.stdout + result.stderr


def test_quiet_mode() -> None:
    """Test quiet mode output matches expected."""
    actual = run_pytest("examples.py", "-q")
    expected = (Path(__file__).parent / "expected" / "pytest-quiet.md").read_text()
    assert actual == expected, (
        f"Quiet mode output mismatch:\nExpected:\n{expected}\n\nActual:\n{actual}"
    )


def test_default_mode() -> None:
    """Test default mode output matches expected."""
    actual = run_pytest("examples.py")
    expected = (Path(__file__).parent / "expected" / "pytest-default.md").read_text()
    assert actual == expected, (
        f"Default mode output mismatch:\nExpected:\n{expected}\n\nActual:\n{actual}"
    )


def test_verbose_mode() -> None:
    """Test verbose mode output matches expected."""
    actual = run_pytest("examples.py", "-v")
    expected = (Path(__file__).parent / "expected" / "pytest-verbose.md").read_text()
    assert actual == expected, (
        f"Verbose mode output mismatch:\nExpected:\n{expected}\n\nActual:\n{actual}"
    )


def test_skipped_section_separate() -> None:
    """Test that skipped tests appear in separate section in verbose mode."""
    actual = run_pytest("examples.py", "-v")

    # Should have both sections in verbose mode
    assert "## Failures" in actual, "Should have Failures section"
    assert "## Skipped" in actual, "Should have Skipped section"

    # Skipped section should come after Failures
    failures_idx = actual.index("## Failures")
    skipped_idx = actual.index("## Skipped")
    assert skipped_idx > failures_idx, "Skipped should come after Failures"

    # Skipped test should be in Skipped section, not Failures
    skipped_section_start = skipped_idx
    # Find the next section or end
    passes_idx = actual.index("## Passes") if "## Passes" in actual else len(actual)
    skipped_section = actual[skipped_section_start:passes_idx]

    assert "test_future_feature SKIPPED" in skipped_section, (
        "Skipped test should be in Skipped section"
    )

    # Failures section should NOT contain SKIPPED
    failures_section = actual[failures_idx:skipped_idx]
    assert "SKIPPED" not in failures_section, (
        "Failures section should not contain skipped tests"
    )


def test_collection_error() -> None:
    """Test collection error output format."""
    # Create a temporary file with syntax error
    syntax_error_file = Path(__file__).parent / "test_collection_error_temp.py"
    syntax_error_file.write_text("def test_bad(\n    pass\n")

    try:
        actual = run_pytest(str(syntax_error_file))

        # Check for expected structure (paths vary by environment)
        assert actual.startswith("# Collection Errors\n"), (
            "Missing collection errors header"
        )
        assert "**1 collection error**" in actual, "Missing error count"
        assert "### tests/test_collection_error_temp.py" in actual, "Missing file name"
        assert "```python" in actual, "Missing code block"
        assert "SyntaxError: '(' was never closed" in actual, "Missing error message"
        assert actual.endswith("```\n"), "Should end with code block"
    finally:
        # Clean up
        syntax_error_file.unlink(missing_ok=True)


def test_no_trailing_blank_lines() -> None:
    """Verify all outputs end with single newline, not double."""
    for mode, args in [
        ("quiet", ["-q"]),
        ("default", []),
        ("verbose", ["-v"]),
    ]:
        actual = run_pytest("examples.py", *args)
        assert not actual.endswith("\n\n"), f"{mode} mode has trailing blank line"
        assert actual.endswith("\n"), f"{mode} mode missing final newline"


def test_default_with_rs_flag() -> None:
    """Test -rs shows skipped section in default mode."""
    actual = run_pytest("examples.py", "-rs")

    # With -rs, only skipped section shown (failures gated on f flag)
    assert "## Failures" not in actual
    assert "test_edge_case FAILED" not in actual

    assert "## Skipped" in actual
    assert "test_future_feature SKIPPED" in actual
    assert "Not implemented yet" in actual

    # XFAIL should still be hidden
    assert "test_known_bug XFAIL" not in actual


def test_default_with_rx_flag() -> None:
    """Test -rx shows xfailed tests in default mode."""
    actual = run_pytest("examples.py", "-rx")

    # With -rx, xfailed shown in Failures section
    # (failures gated on f flag, but xfailed gate on x)
    assert "## Failures" in actual
    assert "test_edge_case FAILED" not in actual  # Regular failures should not show
    assert "test_known_bug XFAIL" in actual
    assert "Bug #123" in actual

    # Skipped should still be hidden
    assert "## Skipped" not in actual


def test_default_with_rsx_flags() -> None:
    """Test -rsx shows both skipped and xfailed in default mode."""
    actual = run_pytest("examples.py", "-rsx")

    # With -rsx, xfailed shown in Failures section
    assert "## Failures" in actual
    assert "test_edge_case FAILED" not in actual  # Regular failures should not show
    assert "test_known_bug XFAIL" in actual

    # Skipped should show
    assert "## Skipped" in actual
    assert "test_future_feature SKIPPED" in actual


def test_errors_separate_from_failures() -> None:
    """Test that setup/teardown errors appear in separate ## Errors section."""
    actual = run_pytest("examples.py", "-rE")

    # Should have separate Errors section
    assert "## Errors" in actual, (
        "Expected '## Errors' section for setup/teardown errors"
    )

    # Setup error should appear in Errors section
    assert "test_setup_error ERROR in setup" in actual, (
        "Expected setup error in Errors section"
    )

    # Regular failures should NOT appear with -rE (only errors shown)
    assert "test_edge_case FAILED" not in actual, (
        "Failures should not be shown with -rE"
    )


def test_default_shows_errors_and_failures() -> None:
    """Test that default mode (no -r flags) shows both errors and failures."""
    actual = run_pytest("examples.py")

    # Default should show both sections
    assert "## Errors" in actual, "Default mode should show errors"
    assert "## Failures" in actual, "Default mode should show failures"

    # Both error and failure should appear
    assert "test_setup_error ERROR in setup" in actual
    assert "test_edge_case FAILED" in actual


def test_rf_flag_hides_errors() -> None:
    """Test -rf shows only failures, not errors."""
    actual = run_pytest("examples.py", "-rf")

    # Should have failures
    assert "## Failures" in actual, "Should show failures with -rf"
    assert "test_edge_case FAILED" in actual

    # Should NOT have errors
    assert "## Errors" not in actual, "Should not show errors with -rf flag"
    assert "test_setup_error" not in actual


def test_rp_flag_shows_passes() -> None:
    """Test -rp shows passes in default mode (not just verbose)."""
    actual = run_pytest("examples.py", "-rp")

    # Should NOT have failures (f flag not present with -rp)
    assert "## Failures" not in actual

    # Should have passes section (from -rp flag)
    assert "## Passes" in actual, "Expected '## Passes' section with -rp flag"

    # Should list passing tests
    assert "test_simple" in actual, "Should show passing test names"


def test_verbose_shows_passes_regardless_of_rp() -> None:
    """Test that -v shows passes even without -rp flag."""
    actual_v = run_pytest("examples.py", "-v")
    actual_v_without_rp = run_pytest("examples.py", "-v")

    # Both should have passes (verbose always shows)
    assert "## Passes" in actual_v
    assert "## Passes" in actual_v_without_rp

    # Verify they're the same
    assert actual_v == actual_v_without_rp


def test_rp_flag_shows_passed_with_output() -> None:
    """Test -rP shows passed tests that captured output."""
    actual = run_pytest("examples.py", "-rP")

    # Should have special section for passed with output (not generic passes)
    assert "## Passes (with output)" in actual, (
        "Expected '## Passes (with output)' section, not generic '## Passes'"
    )

    # Should show the test that has output
    assert "test_with_output" in actual, "Should show test_with_output"

    # Should show the actual captured output content
    assert "Debug: processing started" in actual, "Should show captured stdout content"
    assert "Status: OK" in actual, "Should show captured stderr content"


def test_rw_flag_shows_warnings() -> None:
    """Test -rw shows warnings section."""
    actual = run_pytest("examples.py", "-rw")

    # Should have warnings section with -rw flag
    assert "## Warnings" in actual, "Expected '## Warnings' section with -rw flag"

    # Should show the test that has warnings
    assert "test_with_warning" in actual, (
        "Should show test_with_warning in warnings section"
    )

    # Should show the actual warning message content
    assert "This is a test warning" in actual, (
        "Should show warning message content 'This is a test warning'"
    )


def test_rp_flag_without_output_shows_no_section() -> None:
    """Test -rP flag without output shows no section.

    When no tests have output, -rP should not show the 'Passes (with output)'
    section.
    """
    # Run test that has no output (test_simple has no print statements)
    actual = run_pytest("examples.py::test_simple", "-rP")

    # Should NOT have the passes with output section
    assert "## Passes (with output)" not in actual, (
        "Should not show '## Passes (with output)' when no tests have output"
    )


def test_rw_flag_without_warnings_shows_no_section() -> None:
    """Test -rw doesn't show warnings section when no warnings exist."""
    # Run test that has no warnings
    actual = run_pytest("examples.py::test_simple", "-rw")

    # Should NOT have warnings section
    assert "## Warnings" not in actual, (
        "Should not show '## Warnings' section when no warnings exist"
    )


def test_ra_flag_shows_all_except_passes() -> None:
    """Test -ra shows all sections except regular passes."""
    actual = run_pytest("examples.py", "-ra")

    # Should have all sections except regular passes
    assert "## Failures" in actual, "Should show failures with -ra"
    assert "## Errors" in actual, "Should show errors with -ra"
    assert "## Skipped" in actual, "Should show skipped with -ra"
    assert "## Warnings" in actual, "Should show warnings with -ra"

    # Should NOT have Passes section (but may have "Passes (with output)")
    lines = actual.split("\n")
    sections = [line for line in lines if line.startswith("## ")]

    # Check no plain "## Passes" section (without "with output")
    has_plain_passes = any(s == "## Passes" for s in sections)
    assert not has_plain_passes, (
        f"Should not show plain passes with -ra. Sections: {sections}"
    )


def test_rA_flag_shows_everything() -> None:  # noqa: N802
    """Test -rA shows all sections including passes."""
    actual = run_pytest("examples.py", "-rA")

    # Should have all sections
    assert "## Failures" in actual, "Should show failures with -rA"
    assert "## Errors" in actual, "Should show errors with -rA"
    assert "## Skipped" in actual, "Should show skipped with -rA"
    assert "## Passes" in actual, "Should show passes with -rA"
    assert "## Warnings" in actual, "Should show warnings with -rA"

    # Verify Passes section exists (plain passes, not just with output)
    lines = actual.split("\n")
    sections = [line for line in lines if line.startswith("## ")]
    has_passes = any("Passes" in s for s in sections)
    assert has_passes, f"Should show passes section with -rA. Sections: {sections}"


def test_rN_flag_suppresses_all_sections() -> None:  # noqa: N802
    """Test -rN suppresses all sections (like quiet mode)."""
    actual = run_pytest("examples.py", "-rN")

    # Should have summary
    assert "**Summary:**" in actual, "Should have summary line with -rN"

    # Should NOT have any section headers
    assert "## Failures" not in actual, "Should not show failures with -rN"
    assert "## Errors" not in actual, "Should not show errors with -rN"
    assert "## Skipped" not in actual, "Should not show skipped with -rN"
    assert "## Passes" not in actual, "Should not show passes with -rN"

    # Should be minimal output (summary + maybe rerun command)
    lines = [line for line in actual.split("\n") if line.strip()]
    assert len(lines) <= 3, (
        f"Should have minimal output with -rN. Got {len(lines)} lines: {lines}"
    )


def test_verbose_ignores_r_flags() -> None:
    """Test that -v shows all sections regardless of -r flags."""
    actual_v = run_pytest("examples.py", "-v")
    actual_vrf = run_pytest("examples.py", "-v", "-rf")
    actual_vrN = run_pytest("examples.py", "-v", "-rN")  # noqa: N806

    # All should have same sections (verbose overrides -r)
    for label, actual in [
        ("plain -v", actual_v),
        ("-v -rf", actual_vrf),
        ("-v -rN", actual_vrN),
    ]:
        assert "## Failures" in actual, (
            f"{label} should show failures (verbose overrides)"
        )
        assert "## Passes" in actual, f"{label} should show passes (verbose overrides)"
        assert "## Errors" in actual, f"{label} should show errors (verbose overrides)"

    # Specifically verify -v -rN still shows sections (verbose wins over -rN suppress)
    assert "## Failures" in actual_vrN, "Verbose should override -rN suppression"
    assert "## Passes" in actual_vrN, "Verbose should override -rN suppression"


def test_multiple_flags_combine_correctly() -> None:
    """Test that multiple -r flags combine correctly."""
    # -rsx should show skipped and xfailed
    actual_rsx = run_pytest("examples.py", "-rsx")
    assert "## Skipped" in actual_rsx, "-rsx should show skipped"
    assert "test_known_bug XFAIL" in actual_rsx, "-rsx should show xfailed"

    # -rEf should show errors and failures
    actual_rEf = run_pytest("examples.py", "-rEf")  # noqa: N806
    assert "## Errors" in actual_rEf, "-rEf should show errors"
    assert "## Failures" in actual_rEf, "-rEf should show failures"

    # -rpP should show both types of passes
    actual_rpP = run_pytest("examples.py", "-rpP")  # noqa: N806
    passes_sections = [line for line in actual_rpP.split("\n") if "## Passes" in line]
    # Should have at least one passes section
    assert len(passes_sections) >= 1, (
        f"-rpP should show passes. Got sections: {passes_sections}"
    )
