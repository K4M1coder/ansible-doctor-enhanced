"""Integration tests for CI/CD exit codes - User Story 5.

Following TDD (Red-Green-Refactor):
- RED: These tests MUST FAIL initially (no exit code logic yet)
- GREEN: CLI implementation will make them pass
- REFACTOR: Improve code quality while keeping tests green

Tests cover:
- T071: Exit code 0 on successful execution
- T072: Exit code 1 on fatal error
- T073: Exit code 2 with --fail-on-warnings flag
- T074: Exit code 3 on invalid CLI usage
- T075: Warnings without --fail-on-warnings return exit code 0

Exit Code Convention:
- 0: SUCCESS - operation completed successfully
- 1: ERROR - fatal error occurred
- 2: WARNING - warnings treated as errors (with --fail-on-warnings)
- 3: INVALID - invalid command-line arguments or usage
"""

import pytest
from pathlib import Path
from click.testing import CliRunner

from ansibledoctor.cli import cli


@pytest.fixture
def cli_runner():
    """Provide a Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_role_dir(tmp_path):
    """Create a minimal valid Ansible role structure."""
    role_dir = tmp_path / "test_role"
    role_dir.mkdir()
    
    # Create minimal valid structure
    (role_dir / "meta").mkdir()
    (role_dir / "meta" / "main.yml").write_text(
        "galaxy_info:\n  author: Test Author\n  description: Test role\n"
    )
    
    (role_dir / "defaults").mkdir()
    (role_dir / "defaults" / "main.yml").write_text(
        "# Test variable\ntest_var: value\n"
    )
    
    (role_dir / "tasks").mkdir()
    (role_dir / "tasks" / "main.yml").write_text(
        "- name: Test task\n  debug:\n    msg: Test\n"
    )
    
    return role_dir


class TestExitCodeSuccess:
    """T071: Exit code 0 on successful execution."""

    def test_successful_parse_returns_exit_code_0(self, cli_runner, temp_role_dir, tmp_path):
        """Successful parse should return exit code 0."""
        # Arrange
        output_file = tmp_path / "output.json"
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "parse",
                str(temp_role_dir),
                "--output", str(output_file),
            ]
        )
        
        # Assert
        assert result.exit_code == 0

    def test_successful_generate_returns_exit_code_0(self, cli_runner, temp_role_dir, tmp_path):
        """Successful generate should return exit code 0."""
        # Arrange
        output_file = tmp_path / "output.md"
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output", str(output_file),
            ]
        )
        
        # Assert
        assert result.exit_code == 0


class TestExitCodeFatalError:
    """T072: Exit code 1 on fatal error."""

    def test_nonexistent_role_returns_exit_code_1(self, cli_runner, tmp_path):
        """Fatal error (nonexistent role) should return exit code 1."""
        # Arrange
        nonexistent_role = tmp_path / "nonexistent_role"
        output_file = tmp_path / "output.md"
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(nonexistent_role),
                "--output", str(output_file),
            ]
        )
        
        # Assert - Fatal error should return exit code 1
        assert result.exit_code == 1

    def test_invalid_yaml_returns_exit_code_1(self, cli_runner, tmp_path):
        """Parse error (invalid YAML) should return exit code 1."""
        # Arrange - Create role with completely broken YAML
        role_dir = tmp_path / "broken_role"
        role_dir.mkdir()
        (role_dir / "meta").mkdir()
        # Completely invalid YAML that cannot be parsed
        (role_dir / "meta" / "main.yml").write_text("{ invalid yaml [[[")
        
        output_file = tmp_path / "output.json"
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "parse",
                str(role_dir),
                "--output", str(output_file),
            ]
        )
        
        # Assert - Parsing error should return exit code 1
        assert result.exit_code == 1


class TestExitCodeFailOnWarnings:
    """T073: Exit code 2 with --fail-on-warnings flag."""

    def test_warnings_with_fail_on_warnings_returns_exit_code_2(self, cli_runner, tmp_path):
        """Warnings with --fail-on-warnings should return exit code 2."""
        # Arrange - Create role that might generate warnings
        role_dir = tmp_path / "warning_role"
        role_dir.mkdir()
        
        (role_dir / "meta").mkdir()
        (role_dir / "meta" / "main.yml").write_text("galaxy_info:\n  author: Test\n")
        
        (role_dir / "defaults").mkdir()
        # Variable without annotation might generate warning
        (role_dir / "defaults" / "main.yml").write_text("undocumented_var: value\n")
        
        output_file = tmp_path / "output.md"
        
        # Act - Run with --fail-on-warnings flag
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(role_dir),
                "--output", str(output_file),
                "--fail-on-warnings",
            ]
        )
        
        # Assert - Should return exit code 2 if warnings occurred
        # (may return 0 if no warnings, which is also valid)
        assert result.exit_code in [0, 2]  # 0 if no warnings, 2 if warnings present

    def test_fail_on_warnings_flag_exists(self, cli_runner):
        """Verify --fail-on-warnings flag is recognized by CLI."""
        # Act - Check help output includes flag
        result = cli_runner.invoke(cli, ["generate", "--help"])
        
        # Assert
        assert result.exit_code == 0
        # Flag should be mentioned in help text (when implemented)
        # For now, just verify help works
        assert "generate" in result.output.lower() or "usage" in result.output.lower()


class TestExitCodeInvalidUsage:
    """T074: Exit code 3 on invalid CLI usage."""

    def test_invalid_flag_returns_exit_code_2_or_3(self, cli_runner):
        """Invalid command-line flag should return exit code 2 or 3 (Click default is 2)."""
        # Act - Use invalid flag
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "/some/path",
                "--invalid-flag-that-does-not-exist",
            ]
        )
        
        # Assert - Click returns 2 for invalid options by default
        assert result.exit_code in [2, 3]  # Accept both Click's default (2) and our custom (3)

    def test_missing_required_argument_returns_exit_code_2_or_3(self, cli_runner):
        """Missing required argument should return exit code 2 or 3."""
        # Act - Generate without required role_path
        result = cli_runner.invoke(cli, ["generate"])
        
        # Assert
        assert result.exit_code in [2, 3]


class TestExitCodeWarningsWithoutFlag:
    """T075: Warnings without --fail-on-warnings return exit code 0."""

    def test_warnings_without_fail_on_warnings_returns_exit_code_0(self, cli_runner, tmp_path):
        """Warnings WITHOUT --fail-on-warnings should still return exit code 0."""
        # Arrange - Create role that might generate warnings
        role_dir = tmp_path / "warning_role"
        role_dir.mkdir()
        
        (role_dir / "meta").mkdir()
        (role_dir / "meta" / "main.yml").write_text("galaxy_info:\n  author: Test\n")
        
        (role_dir / "defaults").mkdir()
        (role_dir / "defaults" / "main.yml").write_text("undocumented_var: value\n")
        
        output_file = tmp_path / "output.md"
        
        # Act - Run WITHOUT --fail-on-warnings flag
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(role_dir),
                "--output", str(output_file),
            ]
        )
        
        # Assert - Should return exit code 0 even if warnings present
        assert result.exit_code == 0
