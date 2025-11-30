"""Unit tests for CLI templates subcommand (T252).

TDD RED phase: Write tests FIRST before implementing templates subcommand.
Tests CLI interface for listing, validating, and showing templates.
"""

import pytest
from click.testing import CliRunner

from ansibledoctor.cli import cli


class TestTemplatesSubcommand:
    """Test suite for 'templates' CLI subcommand (T252)."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_templates_command_exists(self, runner):
        """Test that templates command is registered."""
        result = runner.invoke(cli, ["templates", "--help"])
        assert result.exit_code == 0
        assert "templates" in result.output.lower()

    def test_templates_list_shows_available_formats(self, runner):
        """Test 'templates list' shows all available template formats."""
        result = runner.invoke(cli, ["templates", "list"])

        assert result.exit_code == 0
        # Should list all 3 formats
        assert "markdown" in result.output.lower()
        assert "html" in result.output.lower()
        assert "rst" in result.output.lower()

    def test_templates_show_displays_default_template(self, runner):
        """Test 'templates show <format>' displays default template content."""
        result = runner.invoke(cli, ["templates", "show", "markdown"])

        # Should succeed (or fail gracefully if template not found)
        # Exit code 0 for success, 1 for template not found
        assert result.exit_code in [0, 1]

        # If successful, should contain Jinja2 template syntax
        if result.exit_code == 0:
            assert (
                "{{" in result.output and "}}" in result.output
            ) or "role" in result.output.lower()

    def test_templates_show_invalid_format(self, runner):
        """Test 'templates show' with invalid format shows error."""
        result = runner.invoke(cli, ["templates", "show", "invalid"])

        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "not found" in result.output.lower()

    def test_templates_validate_accepts_valid_template(self, runner, tmp_path):
        """Test 'templates validate <path>' accepts valid Jinja2 template."""
        # Create a valid template file
        template_file = tmp_path / "test_template.j2"
        template_file.write_text(
            """
# {{ role.name }}

## Description
{{ role.metadata.description }}

## Variables
{% for var in role.variables %}
- {{ var.name }}: {{ var.description }}
{% endfor %}
"""
        )

        result = runner.invoke(cli, ["templates", "validate", str(template_file)])

        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_templates_validate_rejects_invalid_template(self, runner, tmp_path):
        """Test 'templates validate' rejects template with Jinja2 syntax errors."""
        # Create an invalid template with syntax errors
        template_file = tmp_path / "invalid_template.j2"
        template_file.write_text(
            """
# {{ role.name }

## Variables
{% for var in role.variables %}
- {{ var.name }}: {{ var.description
{% endfor %}
"""
        )  # Missing closing }} and incorrect for loop

        result = runner.invoke(cli, ["templates", "validate", str(template_file)])

        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "error" in result.output.lower()
