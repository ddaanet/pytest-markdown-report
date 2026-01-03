"""Core plugin implementation for pytest-markdown-report."""
import io
import re
import sys
from pathlib import Path
import pytest


def escape_markdown(text):
    """Escape markdown special characters in user-provided text.

    Only escapes inline formatting characters that can have real impact:
    - [ ] : Link references
    - * : Bold/italic
    - _ : Italic (particularly important for code like variable_names)
    """
    special_chars = r'[]*_'
    return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    """Set traceback style before loading plugins."""
    # Set --tb=short as default if not specified
    if not any(arg.startswith("--tb") for arg in args):
        args.insert(0, "--tb=short")


def pytest_addoption(parser):
    """Add command-line options."""
    group = parser.getgroup("markdown-report")
    group.addoption(
        "--markdown-report",
        action="store",
        dest="markdown_report_path",
        metavar="path",
        default=None,
        help="Also save markdown test report to specified file",
    )
    group.addoption(
        "--markdown-rerun-cmd",
        action="store",
        dest="markdown_rerun_cmd",
        metavar="cmd",
        default="pytest --lf",
        help="Command to suggest for rerunning failed tests (empty to disable)",
    )


def pytest_configure(config):
    """Register the plugin."""
    # Always register markdown reporter
    config._markdown_report = MarkdownReport(config)
    config.pluginmanager.register(config._markdown_report)

    # Redirect stdout/stderr to suppress pytest output
    config._markdown_report._redirect_output()


def pytest_unconfigure(config):
    """Unregister the plugin."""
    markdown_report = getattr(config, "_markdown_report", None)
    if markdown_report:
        del config._markdown_report
        config.pluginmanager.unregister(markdown_report)


class MarkdownReport:
    """Generate token-efficient markdown test reports."""

    def __init__(self, config):
        self.config = config
        markdown_path = config.getoption("markdown_report_path")
        self.markdown_path = Path(markdown_path) if markdown_path else None
        self.rerun_cmd = config.getoption("markdown_rerun_cmd")
        self.verbosity = config.option.verbose
        self.quiet = config.option.verbose < 0

        self.reports = []
        self.passed = []
        self.failed = []
        self.skipped = []
        self.xfailed = []
        self.xpassed = []
        self.collection_errors = []

        # For output redirection
        self._original_stdout = None
        self._original_stderr = None
        self._capture_buffer = None

    def _redirect_output(self):
        """Redirect stdout/stderr to suppress pytest output."""
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._capture_buffer = io.StringIO()
        sys.stdout = self._capture_buffer
        sys.stderr = self._capture_buffer

    def _restore_output(self):
        """Restore original stdout/stderr."""
        if self._original_stdout:
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr

    def pytest_collectreport(self, report):
        """Capture collection errors."""
        if report.failed:
            self.collection_errors.append(report)

    def pytest_runtest_logreport(self, report):
        """Collect test reports."""
        if report.when == "call" or (report.when == "setup" and report.outcome == "skipped"):
            self.reports.append(report)

    def pytest_sessionfinish(self, session):
        """Generate markdown report at session end."""
        # Restore output before generating report
        self._restore_output()

        # Categorize reports
        for report in self.reports:
            # Check wasxfail first, as xfail tests also have skipped=True
            if hasattr(report, "wasxfail"):
                if report.outcome == "passed":
                    self.xpassed.append(report)
                else:
                    self.xfailed.append(report)
            elif report.skipped:
                self.skipped.append(report)
            elif report.passed:
                self.passed.append(report)
            elif report.failed:
                self.failed.append(report)

        # Generate report
        lines = []

        # Collection errors take priority
        if self.collection_errors:
            lines.extend(self._generate_collection_errors())
        elif self.quiet:
            lines.extend(self._generate_quiet())
        else:
            lines.extend(self._generate_summary())
            if self.failed or self.xfailed or self.xpassed:
                lines.extend(self._generate_failures())
            if self.verbosity > 0:
                lines.extend(self._generate_passes())

        # Output to stdout
        # Remove trailing empty line if present
        if lines and lines[-1] == "":
            lines = lines[:-1]
        report_text = "\n".join(lines) + "\n"
        print(report_text, end="")

        # Also write to file if specified
        if self.markdown_path:
            self.markdown_path.write_text(report_text)

    def _generate_collection_errors(self):
        """Generate collection errors report."""
        lines = ["# Collection Errors", ""]

        error_count = len(self.collection_errors)
        plural = "error" if error_count == 1 else "errors"
        lines.append(f"**{error_count} collection {plural}**")
        lines.append("")

        for report in self.collection_errors:
            # Get the file path from the report
            if hasattr(report, 'nodeid') and report.nodeid:
                lines.append(f"### {report.nodeid}")
            elif hasattr(report, 'fspath'):
                lines.append(f"### {report.fspath}")
            else:
                lines.append("### Collection Error")
            lines.append("")

            # Add error details
            if report.longreprtext:
                lines.extend(["```python", report.longreprtext.strip(), "```", ""])

        return lines

    def _generate_summary(self):
        """Generate summary line."""
        total_passed = len(self.passed)
        total_failed = len(self.failed) + len(self.xpassed)
        total_skipped = len(self.skipped)
        total_xfailed = len(self.xfailed)

        # Build summary parts
        parts = [f"{total_passed}/{total_passed + total_failed + total_skipped + total_xfailed} passed"]
        if total_failed > 0:
            parts.append(f"{total_failed} failed")
        if total_skipped > 0:
            parts.append(f"{total_skipped} skipped")
        if total_xfailed > 0:
            parts.append(f"{total_xfailed} xfail")

        return [
            "# Test Report",
            "",
            f"**Summary:** {', '.join(parts)}",
            "",
        ]

    def _generate_quiet(self):
        """Generate quiet mode output."""
        total_passed = len(self.passed)
        total_failed = len(self.failed) + len(self.xpassed)
        total_skipped = len(self.skipped)
        total_xfailed = len(self.xfailed)

        # Build summary parts
        parts = [f"{total_passed}/{total_passed + total_failed + total_skipped + total_xfailed} passed"]
        if total_failed > 0:
            parts.append(f"{total_failed} failed")
        if total_skipped > 0:
            parts.append(f"{total_skipped} skipped")
        if total_xfailed > 0:
            parts.append(f"{total_xfailed} xfail")

        lines = [f"**Summary:** {', '.join(parts)}"]

        if self.rerun_cmd and total_failed > 0:
            lines.extend(["", f"Re-run failed: `{self.rerun_cmd}`"])

        return lines

    def _generate_failures(self):
        """Generate failures section."""
        lines = ["## Failures", ""]

        for report in self.failed:
            lines.extend(self._format_failure(report))

        for report in self.skipped:
            lines.extend(self._format_skip(report))

        for report in self.xfailed:
            lines.extend(self._format_xfail(report))

        return lines

    def _format_failure(self, report, symbol="FAILED"):
        """Format a failed test."""
        lines = [f"### {report.nodeid} {symbol}", ""]

        # Add traceback
        if report.longreprtext:
            lines.extend(["```python", report.longreprtext.strip(), "```", ""])

        return lines

    def _format_xpass(self, report):
        """Format an unexpected pass."""
        lines = [f"### {report.nodeid} ⚠ XPASS"]
        lines.append("**Unexpected pass** (expected to fail)")
        lines.append("")
        return lines

    def _format_skip(self, report):
        """Format a skipped test."""
        lines = [f"### {report.nodeid} SKIPPED", ""]
        if hasattr(report, "longrepr") and report.longrepr:
            reason = str(report.longrepr[2]) if isinstance(report.longrepr, tuple) else str(report.longrepr)
            # Remove "Skipped: " prefix if present
            if reason.startswith("Skipped: "):
                reason = reason[9:]
            lines.append(f"**Reason:** {escape_markdown(reason)}")
            lines.append("")
        return lines

    def _format_xfail(self, report):
        """Format an expected failure."""
        lines = [f"### {report.nodeid} XFAIL", ""]

        # Extract xfail reason from wasxfail attribute
        if hasattr(report, "wasxfail") and report.wasxfail:
            # wasxfail contains the reason string
            reason = str(report.wasxfail)
            if reason:
                lines.append(f"**Reason:** {escape_markdown(reason)}")
                lines.append("")

        if report.longreprtext:
            lines.extend(["```python", report.longreprtext.strip(), "```", ""])

        return lines

    def _generate_passes(self):
        """Generate passes section (verbose mode only)."""
        if not self.passed:
            return []

        lines = ["## Passes", ""]
        for report in self.passed:
            lines.append(f"- {report.nodeid}")
        lines.append("")

        return lines
