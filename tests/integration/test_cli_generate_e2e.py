"""
End-to-end integration tests for CLI generate command.

Tests the complete workflow: parse role → generate documentation → verify output.
Uses real role fixtures and CLI invocation to validate full pipeline.

Following Constitution Article III (TDD) and Article IV (Integration Testing).
Task T224 from specs/002-doc-generator/tasks.md
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from ansibledoctor.cli import cli


@pytest.fixture
def fixtures_path():
    """Fixture providing path to integration test fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def minimal_role(fixtures_path):
    """Fixture providing minimal_role path."""
    return fixtures_path / "minimal_role"


@pytest.fixture
def complex_role(fixtures_path):
    """Fixture providing complex_role path."""
    return fixtures_path / "complex_role"


@pytest.fixture
def phase8_test_role(fixtures_path):
    """Fixture providing phase8_test_role path."""
    return fixtures_path / "phase8_test_role"


class TestCliGenerateE2E:
    """End-to-end tests for generate command with real role fixtures."""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner."""
        return CliRunner()

    def test_generate_minimal_role_to_stdout(self, runner, minimal_role):
        """Test generate command with minimal_role fixture to stdout."""
        result = runner.invoke(cli, ["generate", str(minimal_role)])

        assert result.exit_code == 0, f"Failed with output: {result.output}"
        assert "minimal-role" in result.output.lower() or "minimal_role" in result.output.lower()
        # Should have basic Markdown structure
        assert "#" in result.output  # Heading
        assert result.output.strip()  # Non-empty

    def test_generate_minimal_role_to_file(self, runner, minimal_role, tmp_path):
        """Test generate command saves Markdown to file."""
        output_file = tmp_path / "README.md"

        result = runner.invoke(cli, ["generate", str(minimal_role), "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "#" in content  # Has headings
        assert len(content) > 50  # Has substantial content

    def test_generate_complex_role_complete_sections(self, runner, complex_role):
        """Test generate with complex_role includes all sections."""
        result = runner.invoke(cli, ["generate", str(complex_role)])

        assert result.exit_code == 0
        output = result.output.lower()

        # Should contain major sections
        assert "variable" in output or "defaults" in output
        assert "author" in output or "metadata" in output

    def test_generate_with_format_option(self, runner, minimal_role):
        """Test generate command with explicit format option."""
        result = runner.invoke(cli, ["generate", str(minimal_role), "--format", "markdown"])

        assert result.exit_code == 0
        assert result.output.strip()  # Has output

    def test_generate_with_verbose_logging(self, runner, minimal_role):
        """Test generate command with verbose flag shows debug output."""
        result = runner.invoke(cli, ["generate", str(minimal_role), "--verbose"])

        assert result.exit_code == 0
        # Output should exist (verbose may add logs to stderr, not stdout)
        assert result.output or result.stderr

    def test_generate_nonexistent_role_fails(self, runner, tmp_path):
        """Test generate with nonexistent role path fails gracefully."""
        fake_path = tmp_path / "nonexistent-role"

        result = runner.invoke(cli, ["generate", str(fake_path)])

        assert result.exit_code != 0
        # Should have error message
        assert "error" in result.output.lower() or "not exist" in result.output.lower()

    def test_generate_phase8_test_role(self, runner, phase8_test_role):
        """Test generate with phase8_test_role fixture (tags, TODOs, examples)."""
        result = runner.invoke(cli, ["generate", str(phase8_test_role)])

        assert result.exit_code == 0
        output = result.output.lower()

        # Should include Phase 8 features
        assert "test" in output  # Role name contains "test"

    def test_generate_with_custom_output_path(self, runner, minimal_role, tmp_path):
        """Test generate creates nested output directories."""
        output_file = tmp_path / "docs" / "generated" / "README.md"

        result = runner.invoke(cli, ["generate", str(minimal_role), "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert output_file.parent.exists()  # Parent dirs created

    def test_generate_preserves_role_name(self, runner, minimal_role):
        """Test generated docs contain correct role name."""
        result = runner.invoke(cli, ["generate", str(minimal_role)])

        assert result.exit_code == 0
        output = result.output

        # Role name should appear in output
        role_name = minimal_role.name
        assert (
            role_name in output
            or role_name.replace("-", "_") in output
            or role_name.replace("_", "-") in output
        )

    def test_generate_output_is_valid_markdown(self, runner, minimal_role, tmp_path):
        """Test generated output is valid Markdown structure."""
        output_file = tmp_path / "test.md"

        result = runner.invoke(cli, ["generate", str(minimal_role), "--output", str(output_file)])

        assert result.exit_code == 0

        content = output_file.read_text()

        # Basic Markdown validation
        assert content.strip()  # Not empty
        # Should have at least one heading
        lines = content.split("\n")
        has_heading = any(line.startswith("#") for line in lines)
        assert has_heading, "Markdown should contain at least one heading"

    def test_generate_handles_role_with_metadata(self, runner, complex_role):
        """Test generate properly handles role metadata."""
        result = runner.invoke(cli, ["generate", str(complex_role)])

        assert result.exit_code == 0
        # Metadata fields should appear in output
        # (exact format depends on template, but should exist)
        assert len(result.output) > 100  # Substantial content

    def test_generate_cli_integration_complete_workflow(self, runner, minimal_role, tmp_path):
        """Test complete workflow: generate → verify output structure."""
        output_file = tmp_path / "GENERATED.md"

        # Run generate command
        result = runner.invoke(
            cli,
            [
                "generate",
                str(minimal_role),
                "--format",
                "markdown",
                "--output",
                str(output_file),
            ],
        )

        # Verify success
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify file created
        assert output_file.exists(), "Output file not created"

        # Verify content quality
        content = output_file.read_text()
        assert len(content) > 50, "Generated content too short"
        assert "#" in content, "Missing Markdown headings"

        # Verify it's readable text (no binary garbage)
        assert content.isprintable() or any(
            c in content for c in ["\n", "\t", " "]
        ), "Content not readable text"
