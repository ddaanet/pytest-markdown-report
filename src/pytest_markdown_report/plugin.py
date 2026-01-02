"""Core plugin implementation for pytest-markdown-report."""
from pathlib import Path


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
        self._tw_replaced = False

    def pytest_runtest_logstart(self, nodeid, location):
        """Unregister terminal reporter before first test runs."""
        if not self._tw_replaced:
            terminal_reporter = self.config.pluginmanager.get_plugin("terminalreporter")
            if terminal_reporter:
                # Unregister the terminal reporter to suppress its output
                self.config.pluginmanager.unregister(terminal_reporter)
                self._tw_replaced = True

    def pytest_runtest_logreport(self, report):
        """Collect test reports."""
        if report.when == "call" or (report.when == "setup" and report.outcome == "skipped"):
            self.reports.append(report)

    def pytest_sessionfinish(self, session):
        """Generate markdown report at session end."""
        # Categorize reports
        for report in self.reports:
            if report.skipped:
                self.skipped.append(report)
            elif hasattr(report, "wasxfail"):
                if report.outcome == "passed":
                    self.xpassed.append(report)
                else:
                    self.xfailed.append(report)
            elif report.passed:
                self.passed.append(report)
            elif report.failed:
                self.failed.append(report)

        # Generate report
        lines = []

        if self.quiet:
            lines.extend(self._generate_quiet())
        else:
            lines.extend(self._generate_summary())
            if self.failed or self.xfailed or self.xpassed:
                lines.extend(self._generate_failures())
            if self.verbosity > 0:
                lines.extend(self._generate_passes())

        # Output to stdout
        report_text = "\n".join(lines) + "\n"
        print(report_text, end="")

        # Also write to file if specified
        if self.markdown_path:
            self.markdown_path.write_text(report_text)

    def _generate_summary(self):
        """Generate summary line."""
        total_passed = len(self.passed)
        total_failed = len(self.failed) + len(self.xpassed)
        total_skipped = len(self.skipped) + len(self.xfailed)

        return [
            "# Test Report",
            "",
            f"**Summary**: {total_passed}/{total_passed + total_failed + total_skipped} passed | "
            f"{total_failed} failed | {total_skipped} skipped",
            "",
        ]

    def _generate_quiet(self):
        """Generate quiet mode output."""
        total_passed = len(self.passed)
        total_failed = len(self.failed) + len(self.xpassed)
        total_skipped = len(self.skipped) + len(self.xfailed)

        lines = [
            f"**Summary**: {total_passed}/{total_passed + total_failed + total_skipped} passed | "
            f"{total_failed} failed | {total_skipped} skipped",
        ]

        if self.rerun_cmd and total_failed > 0:
            lines.extend(["", f"Re-run failed: `{self.rerun_cmd}`"])

        return lines

    def _generate_failures(self):
        """Generate failures section."""
        lines = ["## Failures", ""]

        for report in self.failed:
            lines.extend(self._format_failure(report, "✗"))

        for report in self.xpassed:
            lines.extend(self._format_xpass(report))

        for report in self.skipped:
            lines.extend(self._format_skip(report))

        for report in self.xfailed:
            lines.extend(self._format_xfail(report))

        return lines

    def _format_failure(self, report, symbol="✗"):
        """Format a failed test."""
        lines = [f"### {report.nodeid} {symbol}"]

        # Extract error type
        if report.longrepr:
            error_type = self._extract_error_type(report)
            if error_type:
                lines.append(f"**Error**: {error_type}")

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
        lines = [f"### {report.nodeid} ⊘"]
        if hasattr(report, "longrepr") and report.longrepr:
            reason = str(report.longrepr[2]) if isinstance(report.longrepr, tuple) else str(report.longrepr)
            lines.append(f"**Reason**: {reason}")
        lines.append("")
        return lines

    def _format_xfail(self, report):
        """Format an expected failure."""
        lines = [f"### {report.nodeid} ⚠"]

        error_type = self._extract_error_type(report)
        parts = ["**Expected to fail**"]
        if error_type:
            parts.append(f"**Error**: {error_type}")
        lines.append(" | ".join(parts))

        if report.longreprtext:
            lines.extend(["```python", report.longreprtext.strip(), "```", ""])
        else:
            lines.append("")

        return lines

    def _extract_error_type(self, report):
        """Extract error type from report."""
        if not report.longreprtext:
            return None

        # Look for "Error:" pattern in traceback
        for line in report.longreprtext.split("\n"):
            if line.startswith("E       ") and "Error" in line:
                # Extract error type
                error = line[8:].strip()
                if ":" in error:
                    return error.split(":")[0]
                return error

        return None

    def _generate_passes(self):
        """Generate passes section (verbose mode only)."""
        if not self.passed:
            return []

        lines = ["## Passes"]
        for report in self.passed:
            lines.append(f"- {report.nodeid} ✓")
        lines.append("")

        return lines
