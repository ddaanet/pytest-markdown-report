"""Debug plugin for pytest to inspect test report attributes."""

import builtins
import contextlib

from _pytest.reports import TestReport


class DebugPlugin:
    """Plugin for debugging pytest test reports."""

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Handle test report log event."""
        if report.when == "call" and "test_with_warning" in report.nodeid:
            if hasattr(report, "sections"):
                pass
            if hasattr(report, "longreprtext"):
                pass
            # Check for any attribute with "warn" in it
            warn_attrs = [attr for attr in dir(report) if "warn" in attr.lower()]
            for attr in warn_attrs:
                with contextlib.suppress(builtins.BaseException):
                    getattr(report, attr)


pytest_plugins = [DebugPlugin()]
