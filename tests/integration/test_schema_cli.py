"""Integration tests for schema CLI commands.

Tests the schema command group including validate, export, convert, and docs commands.
"""


import pytest
from click.testing import CliRunner

from ansibledoctor.cli.schema import schema


class TestSchemaValidateCommand:
    """Test the 'schema validate' command."""

    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def valid_config_path(self, tmp_path):
        """Create a valid configuration file."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
output_format: markdown
output_dir: docs
verbose: false
include_index: true
index_style: tree
"""
        )
        return config_file

    @pytest.fixture
    def invalid_config_path(self, tmp_path):
        """Create an invalid configuration file."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
output_format: pdf
verbose: "not_a_boolean"
unknown_field: value
"""
        )
        return config_file

    def test_validate_valid_config(self, cli_runner, valid_config_path):
        """Test validation of a valid configuration file."""
        result = cli_runner.invoke(schema, ["validate", str(valid_config_path)])
        assert result.exit_code == 0
        assert "Validation Report:" in result.output

    def test_validate_invalid_config(self, cli_runner, invalid_config_path):
        """Test validation of an invalid configuration file."""
        result = cli_runner.invoke(schema, ["validate", str(invalid_config_path)])
        assert result.exit_code == 1
        assert "Validation Report:" in result.output
        assert "ERROR:" in result.output

    def test_validate_with_verbose_flag(self, cli_runner, invalid_config_path):
        """Test validation with verbose output."""
        result = cli_runner.invoke(schema, ["validate", str(invalid_config_path), "--verbose"])
        assert result.exit_code == 1
        assert "Suggestion:" in result.output  # Verbose shows suggestions

    def test_validate_with_strict_flag(self, cli_runner, tmp_path):
        """Test validation with strict mode (warnings as errors)."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
output_format: markdown
unknown_field: value
"""
        )
        result = cli_runner.invoke(schema, ["validate", str(config_file), "--strict"])
        assert result.exit_code == 1  # Warning treated as error

    def test_validate_nonexistent_file(self, cli_runner, tmp_path):
        """Test validation of a non-existent file."""
        nonexistent = tmp_path / "nonexistent.yml"
        result = cli_runner.invoke(schema, ["validate", str(nonexistent)])
        assert result.exit_code != 0  # Should fail


class TestSchemaExportCommand:
    """Test the 'schema export' command (placeholder)."""

    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    def test_export_not_implemented(self, cli_runner):
        """Test that export command shows not implemented message."""
        result = cli_runner.invoke(schema, ["export", "config"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output.lower()


class TestSchemaConvertCommand:
    """Test the 'schema convert' command (placeholder)."""

    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    def test_convert_not_implemented(self, cli_runner, tmp_path):
        """Test that convert command shows not implemented message."""
        input_file = tmp_path / "input.yml"
        input_file.write_text("key: value")
        result = cli_runner.invoke(schema, ["convert", str(input_file), "--to", "json"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output.lower()


class TestSchemaDocsCommand:
    """Test the 'schema docs' command (placeholder)."""

    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    def test_docs_not_implemented(self, cli_runner):
        """Test that docs command shows not implemented message."""
        result = cli_runner.invoke(schema, ["docs", "config"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output.lower()
