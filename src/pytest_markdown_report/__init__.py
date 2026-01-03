"""pytest-markdown-report: Token-efficient markdown test reports for LLM agents."""
from pytest_markdown_report.plugin import (
    pytest_addoption,
    pytest_configure,
    pytest_load_initial_conftests,
    pytest_unconfigure,
)

__all__ = ["pytest_addoption", "pytest_configure", "pytest_load_initial_conftests", "pytest_unconfigure"]
