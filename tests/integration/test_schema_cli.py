"""Integration tests for schema CLI commands.

Tests the schema command group including validate, export, convert, and docs commands.
"""

import json

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
    """Test the 'schema export' command."""

    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    def test_export_config_to_stdout(self, cli_runner):
        """Test exporting config schema to stdout (default JSON Schema)."""
        result = cli_runner.invoke(schema, ["export", "config"])
        assert result.exit_code == 0

        # Parse output as JSON
        schema_data = json.loads(result.output)
        assert "$schema" in schema_data
        assert "properties" in schema_data
        assert "output_format" in schema_data["properties"]

    def test_export_config_json_schema_format(self, cli_runner):
        """Test exporting config schema as JSON Schema format."""
        result = cli_runner.invoke(schema, ["export", "config", "--format", "json-schema"])
        assert result.exit_code == 0

        schema_data = json.loads(result.output)
        assert schema_data["$schema"] == "https://json-schema.org/draft/2020-12/schema"

    def test_export_config_openapi_format(self, cli_runner):
        """Test exporting config schema in OpenAPI format."""
        result = cli_runner.invoke(schema, ["export", "config", "--format", "openapi"])
        assert result.exit_code == 0

        schema_data = json.loads(result.output)
        assert "openapi" in schema_data
        assert "components" in schema_data
        assert "schemas" in schema_data["components"]

    def test_export_to_file(self, cli_runner, tmp_path):
        """Test exporting schema to a file."""
        output_file = tmp_path / "schema.json"
        result = cli_runner.invoke(schema, ["export", "config", "--output", str(output_file)])
        assert result.exit_code == 0
        assert "exported to" in result.output.lower()

        # Verify file was created
        assert output_file.exists()

        # Verify file contains valid JSON Schema
        with open(output_file) as f:
            schema_data = json.load(f)
        assert "$schema" in schema_data
        assert "properties" in schema_data

    def test_export_role_not_implemented(self, cli_runner):
        """Test that role export shows not implemented message."""
        result = cli_runner.invoke(schema, ["export", "role"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output.lower()


class TestSchemaConvertCommand:
    """Test the 'schema convert' command."""

    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def sample_yaml_file(self, tmp_path):
        """Create a sample YAML file for testing."""
        yaml_file = tmp_path / "input.yml"
        yaml_file.write_text(
            """
output_format: markdown
output_dir: docs/
recursive: true
theme:
  primary_color: "#007acc"
"""
        )
        return yaml_file

    @pytest.fixture
    def sample_json_file(self, tmp_path):
        """Create a sample JSON file for testing."""
        json_file = tmp_path / "input.json"
        json_file.write_text('{"output_format": "markdown", "recursive": true}')
        return json_file

    def test_convert_yaml_to_json_stdout(self, cli_runner, sample_yaml_file):
        """Test converting YAML to JSON and output to stdout.

        T055: CLI convert command - stdout output
        """
        result = cli_runner.invoke(schema, ["convert", str(sample_yaml_file), "--to", "json"])

        assert result.exit_code == 0
        # Output should be valid JSON
        data = json.loads(result.output)
        assert data["output_format"] == "markdown"
        assert data["recursive"] is True

    def test_convert_yaml_to_json_with_pretty(self, cli_runner, sample_yaml_file):
        """Test converting with pretty formatting.

        T055: CLI convert command - pretty flag
        """
        result = cli_runner.invoke(
            schema, ["convert", str(sample_yaml_file), "--to", "json", "--pretty"]
        )

        assert result.exit_code == 0
        # Pretty output should have indentation
        assert "  " in result.output or "\t" in result.output
        # Should still be valid JSON
        data = json.loads(result.output)
        assert "output_format" in data

    def test_convert_to_file(self, cli_runner, sample_yaml_file, tmp_path):
        """Test converting to output file.

        T056: CLI convert command - file output
        """
        output_file = tmp_path / "output.json"

        result = cli_runner.invoke(
            schema, ["convert", str(sample_yaml_file), "--to", "json", "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify output file content
        data = json.loads(output_file.read_text())
        assert data["output_format"] == "markdown"

    def test_convert_json_to_yaml(self, cli_runner, sample_json_file):
        """Test converting JSON to YAML.

        T055: CLI convert command - JSON to YAML
        """
        result = cli_runner.invoke(schema, ["convert", str(sample_json_file), "--to", "yaml"])

        assert result.exit_code == 0
        # Output should contain YAML syntax
        assert "output_format:" in result.output
        assert "recursive:" in result.output

    def test_convert_to_xml(self, cli_runner, sample_json_file):
        """Test converting to XML.

        T055: CLI convert command - XML output
        """
        result = cli_runner.invoke(schema, ["convert", str(sample_json_file), "--to", "xml"])

        assert result.exit_code == 0
        # Output should contain XML syntax
        assert "<?xml" in result.output
        assert "<root>" in result.output
        assert "</root>" in result.output

    def test_convert_to_mermaid(self, cli_runner, sample_yaml_file):
        """Test converting to Mermaid diagram.

        T055: CLI convert command - Mermaid output
        """
        result = cli_runner.invoke(schema, ["convert", str(sample_yaml_file), "--to", "mermaid"])

        assert result.exit_code == 0
        # Output should contain Mermaid syntax
        assert "graph" in result.output.lower()

    def test_convert_missing_file(self, cli_runner, tmp_path):
        """Test error handling for missing input file."""
        missing_file = tmp_path / "missing.yml"

        result = cli_runner.invoke(schema, ["convert", str(missing_file), "--to", "json"])

        # Click should catch file not exists
        assert result.exit_code != 0


class TestSchemaDocsCommand:
    """Test the 'schema docs' command (placeholder)."""

    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    def test_docs_command_succeeds(self, cli_runner):
        """Test that docs command executes successfully."""
        result = cli_runner.invoke(schema, ["docs", "config"])
        assert result.exit_code == 0
        # Output should contain Markdown documentation
        assert "# Configuration Schema" in result.output or "## Properties" in result.output
