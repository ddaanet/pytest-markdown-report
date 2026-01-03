"""Example test suite demonstrating pytest-markdown-report output."""
import pytest


def validate(input_str):
    """Example validation function."""
    return len(input_str) > 0


class Parser:
    """Example parser class."""
    
    def extract_tokens(self, data):
        """Extract tokens from data."""
        return data[0]  # Will fail on empty list


parser = Parser()


# Parametrized test with failure
@pytest.mark.parametrize("input,expected", [("", False), ("x", True)])
def test_invalid_input(input, expected):
    """Test input validation."""
    assert validate(input) == expected


# Test with fixture and failure
@pytest.fixture
def empty_data():
    """Provide empty data."""
    return []


def test_edge_case(empty_data):
    """Test edge case with empty data."""
    result = parser.extract_tokens(empty_data)
    assert result is not None


# Skipped test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Test future feature."""
    pass


# xfail test
@pytest.mark.xfail(reason="Bug #123", strict=True)
def test_known_bug():
    """Test known bug."""
    raise ValueError("Known issue")


# Passing tests
def test_simple():
    """Simple passing test."""
    assert 1 + 1 == 2


def test_validation_pass():
    """Test validation with valid input."""
    assert validate("valid") == True


def test_critical_path():
    """Test critical functionality."""
    result = {"status": "success", "timestamp": 123456}
    assert result["status"] == "success"
    assert "timestamp" in result
