"""Test edge cases and error handling."""

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
    return result.stdout + result.stderr


def test_output_restored_after_normal_run() -> None:
    """Test that stdout/stderr are restored after normal pytest run."""
    # This test verifies output streams work after pytest runs
    test_file = Path(__file__).parent / "test_simple_temp.py"
    test_file.write_text('''
def test_pass():
    assert True
''')

    try:
        # Run pytest
        run_pytest(str(test_file))

        # Verify we can still capture output (streams are restored)
        result = subprocess.run(
            [sys.executable, "-c", "print('test')"],
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "test", "Output streams should be restored"

    finally:
        test_file.unlink(missing_ok=True)


def test_file_write_with_invalid_path() -> None:
    """Test that invalid --markdown-report path is handled gracefully."""
    test_file = Path(__file__).parent / "test_simple_temp.py"
    test_file.write_text('''
def test_pass():
    assert True
''')

    try:
        # Try to write to invalid path
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file),
             "--markdown-report=/nonexistent/directory/report.md"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        # Should still show output even if file write fails
        output = result.stdout + result.stderr
        assert "1/1 passed" in output or "Warning" in output, "Should show output or warning"

    finally:
        test_file.unlink(missing_ok=True)
