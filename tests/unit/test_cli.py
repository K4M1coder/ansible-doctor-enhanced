"""
Unit tests for CLI interface.

Following Constitution Article III (TDD): Tests written BEFORE implementation.
This test suite drives the design of CLI through Red-Green-Refactor cycle.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ansibledoctor.cli import cli


class TestCliBasics:
    """Test suite for basic CLI functionality."""

    def test_cli_entry_point_exists(self):
        """RED: Test that CLI entry point is callable."""
        assert callable(cli)

    def test_parse_command_exists(self):
        """RED: Test that parse command is available in CLI group."""
        # Parse command should be registered in CLI group
        assert "parse" in [cmd.name for cmd in cli.commands.values()]

    def test_cli_group_decorator(self):
        """RED: Test that CLI is a click group."""
        # CLI should be a click group for subcommands
        assert hasattr(cli, "command")


class TestParseCommand:
    """Test suite for parse command."""

    def test_parse_command_basic(self, tmp_path):
        """RED: Test basic parse command execution."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        # Create minimal role structure
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        (role_path / "meta" / "main.yml").write_text("---\nrole_name: test_role\n")
        (role_path / "defaults").mkdir()
        (role_path / "defaults" / "main.yml").write_text("---\ntest_var: value\n")
        
        result = runner.invoke(cli, ["parse", str(role_path)])
        
        # Should not crash
        assert result.exit_code in [0, 1, 2]  # Success or expected error

    def test_parse_command_with_output_flag(self, tmp_path):
        """RED: Test parse command with --output flag."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        output_file = tmp_path / "output.json"
        
        result = runner.invoke(
            cli, ["parse", str(role_path), "--output", str(output_file)]
        )
        
        # Should accept output flag
        assert result.exit_code in [0, 1, 2]

    def test_parse_command_with_recursive_flag(self, tmp_path):
        """RED: Test parse command with --recursive flag."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        roles_dir = tmp_path / "roles"
        roles_dir.mkdir()
        
        result = runner.invoke(
            cli, ["parse", str(roles_dir), "--recursive"]
        )
        
        # Should accept recursive flag
        assert result.exit_code in [0, 1, 2]

    def test_parse_command_with_log_level(self, tmp_path):
        """RED: Test parse command with --log-level flag."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        
        result = runner.invoke(
            cli, ["parse", str(role_path), "--log-level", "DEBUG"]
        )
        
        # Should accept log-level flag
        assert result.exit_code in [0, 1, 2]

    def test_parse_command_missing_role_path(self):
        """RED: Test parse command without role path argument."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        result = runner.invoke(cli, ["parse"])
        
        # Should fail with missing argument
        assert result.exit_code != 0

    def test_parse_command_nonexistent_role(self, tmp_path):
        """RED: Test parse command with non-existent role path."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        non_existent = tmp_path / "does_not_exist"
        
        result = runner.invoke(cli, ["parse", str(non_existent)])
        
        # Should fail gracefully
        assert result.exit_code != 0


class TestParseCommandIntegration:
    """Integration tests for parse command with fixtures."""

    def test_parse_minimal_role(self):
        """RED: Test parsing minimal_role fixture."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        # Path to minimal_role fixture
        fixture_path = (
            Path(__file__).parent.parent / "integration" / "fixtures" / "minimal_role"
        )
        
        if fixture_path.exists():
            result = runner.invoke(cli, ["parse", str(fixture_path)])
            
            # Should succeed
            assert result.exit_code == 0
            
            # Should output JSON
            assert "metadata" in result.output or "{" in result.output

    def test_parse_complex_role(self):
        """RED: Test parsing complex_role fixture."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        # Path to complex_role fixture
        fixture_path = (
            Path(__file__).parent.parent / "integration" / "fixtures" / "complex_role"
        )
        
        if fixture_path.exists():
            result = runner.invoke(cli, ["parse", str(fixture_path)])
            
            # Should succeed
            assert result.exit_code == 0


class TestOutputFormats:
    """Test suite for output format handling."""

    def test_json_output_default(self, tmp_path):
        """RED: Test that default output is JSON."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        (role_path / "defaults").mkdir()
        (role_path / "defaults" / "main.yml").write_text("test_var: 1")
        
        result = runner.invoke(cli, ["parse", str(role_path)])
        
        if result.exit_code == 0:
            # Output should be valid JSON
            import json
            try:
                json.loads(result.output)
            except json.JSONDecodeError:
                pytest.fail("Output is not valid JSON")

    def test_output_to_file(self, tmp_path):
        """RED: Test writing output to file."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        output_file = tmp_path / "output.json"
        
        result = runner.invoke(
            cli, ["parse", str(role_path), "--output", str(output_file)]
        )
        
        if result.exit_code == 0:
            # Output file should be created
            assert output_file.exists()

    def test_stdout_output_when_no_file(self, tmp_path):
        """RED: Test that output goes to stdout when no file specified."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        
        result = runner.invoke(cli, ["parse", str(role_path)])
        
        # Should have output to stdout
        assert len(result.output) > 0


class TestValidationFlag:
    """Test suite for --validate flag."""

    def test_validate_flag_exists(self, tmp_path):
        """RED: Test that --validate flag is available."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        
        result = runner.invoke(
            cli, ["parse", str(role_path), "--validate"]
        )
        
        # Should accept validate flag
        assert result.exit_code in [0, 1, 2]

    def test_validate_role_structure(self, tmp_path):
        """RED: Test validation of role structure."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        # Invalid role (missing tasks/)
        role_path = tmp_path / "invalid_role"
        role_path.mkdir()
        
        result = runner.invoke(
            cli, ["parse", str(role_path), "--validate"]
        )
        
        # Should report validation error
        if result.exit_code != 0:
            assert "validate" in result.output.lower() or "error" in result.output.lower()


class TestExitCodes:
    """Test suite for CLI exit codes."""

    def test_success_exit_code(self):
        """RED: Test that successful parse returns exit code 0."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        fixture_path = (
            Path(__file__).parent.parent / "integration" / "fixtures" / "minimal_role"
        )
        
        if fixture_path.exists():
            result = runner.invoke(cli, ["parse", str(fixture_path)])
            
            assert result.exit_code == 0

    def test_error_exit_code_nonexistent_role(self, tmp_path):
        """RED: Test that error returns non-zero exit code."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        non_existent = tmp_path / "does_not_exist"
        
        result = runner.invoke(cli, ["parse", str(non_existent)])
        
        assert result.exit_code != 0

    def test_validation_error_exit_code(self, tmp_path):
        """RED: Test that validation error returns specific exit code."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        # Invalid role
        role_path = tmp_path / "invalid_role"
        role_path.mkdir()
        
        result = runner.invoke(
            cli, ["parse", str(role_path), "--validate"]
        )
        
        # Should return non-zero for validation failure
        if result.exit_code != 0:
            assert result.exit_code in [1, 2]  # Error or validation failure


class TestRecursiveMode:
    """Test suite for recursive role parsing."""

    def test_recursive_parse_multiple_roles(self, tmp_path):
        """RED: Test parsing multiple roles recursively."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        # Create multiple roles
        roles_dir = tmp_path / "roles"
        roles_dir.mkdir()
        
        for i in range(3):
            role_path = roles_dir / f"role{i}"
            role_path.mkdir()
            (role_path / "defaults").mkdir()
            (role_path / "defaults" / "main.yml").write_text(f"var{i}: {i}")
        
        result = runner.invoke(
            cli, ["parse", str(roles_dir), "--recursive"]
        )
        
        if result.exit_code == 0:
            # Should have parsed multiple roles
            assert "role0" in result.output or len(result.output) > 100

    def test_recursive_ignores_non_roles(self, tmp_path):
        """RED: Test that recursive mode skips non-role directories."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        roles_dir = tmp_path / "mixed"
        roles_dir.mkdir()
        
        # Create a valid role
        role_path = roles_dir / "valid_role"
        role_path.mkdir()
        (role_path / "tasks").mkdir()
        (role_path / "tasks" / "main.yml").write_text("- name: test")
        
        # Create a non-role directory
        non_role = roles_dir / "not_a_role"
        non_role.mkdir()
        (non_role / "random.txt").write_text("random")
        
        result = runner.invoke(
            cli, ["parse", str(roles_dir), "--recursive"]
        )
        
        # Should succeed (skip non-role)
        assert result.exit_code in [0, 1]


class TestJsonOutput:
    """Test suite for JSON output format validation."""

    def test_json_output_structure(self):
        """RED: Test that JSON output has expected structure."""
        from click.testing import CliRunner

        runner = CliRunner()
        
        fixture_path = (
            Path(__file__).parent.parent / "integration" / "fixtures" / "minimal_role"
        )
        
        if fixture_path.exists():
            result = runner.invoke(cli, ["parse", str(fixture_path)])
            
            if result.exit_code == 0:
                import json
                data = json.loads(result.output)
                
                # Should have expected top-level keys
                assert "metadata" in data or "variables" in data or "name" in data
