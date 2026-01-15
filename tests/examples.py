"""Example test suite demonstrating pytest-markdown-report output."""

import sys
import warnings
from typing import Never

import pytest


def validate(input_str: str) -> bool:
    """Validate input string."""
    return len(input_str) > 0


class Parser:
    """Example parser class."""

    def extract_tokens(self, data: list[str]) -> str:
        """Extract tokens from data."""
        return data[0]  # Will fail on empty list


parser = Parser()


# Parametrized test with failure
@pytest.mark.parametrize(("input_data", "expected"), [("", False), ("x", True)])
def test_invalid_input(input_data: str, expected: bool) -> None:  # noqa: FBT001
    """Test input validation."""
    assert validate(input_data) == expected


# Test with fixture and failure
@pytest.fixture
def empty_data() -> list[str]:
    """Provide empty data."""
    return []


def test_edge_case(empty_data: list[str]) -> None:
    """Test edge case with empty data."""
    result = parser.extract_tokens(empty_data)
    assert result is not None


# Skipped test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature() -> None:
    """Test future feature."""


# xfail test
@pytest.mark.xfail(reason="Bug #123", strict=True)
def test_known_bug() -> Never:
    """Test known bug."""
    msg = "Known issue"
    raise ValueError(msg)


# Passing tests
def test_simple() -> None:
    """Simple passing test."""
    assert 1 + 1 == 2


def test_validation_pass() -> None:
    """Test validation with valid input."""
    assert validate("valid")


def test_critical_path() -> None:
    """Test critical functionality."""
    result = {"status": "success", "timestamp": 123456}
    assert result["status"] == "success"
    assert "timestamp" in result


def test_with_output() -> None:
    """Test that passes but prints output."""
    sys.stdout.write("Debug: processing started\n")
    sys.stderr.write("Status: OK\n")
    assert True


@pytest.mark.filterwarnings("default")
def test_with_warning() -> None:
    """Test that generates a warning."""
    warnings.warn("This is a test warning", UserWarning, stacklevel=2)
    assert True


@pytest.fixture
def broken_fixture() -> None:
    """Fixture that fails during setup."""
    msg = "Fixture setup failed"
    raise RuntimeError(msg)


def test_setup_error(broken_fixture: None) -> None:
    """Test with setup error that uses broken_fixture."""
    _fixture = broken_fixture
    assert True
