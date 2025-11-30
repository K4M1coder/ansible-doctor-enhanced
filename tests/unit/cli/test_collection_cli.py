"""Test suite for collection CLI commands.

Tests the collection parse command with various options and error scenarios.
"""

import json
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from ansibledoctor.cli.collection import collection
from ansibledoctor.exceptions import ParsingError
from ansibledoctor.models.plugin import PluginType


@pytest.fixture
def runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_collection_data():
    """Create mock collection data for testing."""
    return {
        "fqcn": "test_namespace.test_collection",
        "version": "1.0.0",
        "namespace": "test_namespace",
        "name": "test_collection",
        "authors": ["Test Author"],
        "dependencies": {},
        "roles": ["sample_role"],
        "plugins": {"module": ["sample_module"]},
    }


class TestCollectionParseCommandBasic:
    """Test basic collection parse command functionality."""

    def test_command_exists(self, runner):
        """Test that the collection command group exists."""
        result = runner.invoke(collection, ["--help"])
        assert result.exit_code == 0
        assert "collection" in result.output.lower()

    def test_parse_subcommand_exists(self, runner):
        """Test that the parse subcommand exists."""
        result = runner.invoke(collection, ["parse", "--help"])
        assert result.exit_code == 0
        assert "parse" in result.output.lower()

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_parse_requires_collection_path_argument(self, mock_parser, runner):
        """Test that parse command requires collection path argument."""
        result = runner.invoke(collection, ["parse"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "required" in result.output.lower()


class TestCollectionParseCommandOutput:
    """Test collection parse command output options."""

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_parse_outputs_json_to_stdout_by_default(
        self, mock_parser, runner, mock_collection_data, tmp_path
    ):
        """Test that parse command outputs JSON to stdout by default."""
        # Setup mock
        mock_instance = Mock()
        mock_collection = Mock()
        mock_collection.metadata.fqcn = "test_namespace.test_collection"
        mock_collection.metadata.version = "1.0.0"
        mock_collection.metadata.namespace = "test_namespace"
        mock_collection.metadata.name = "test_collection"
        mock_collection.metadata.authors = ["Test Author"]
        mock_collection.metadata.dependencies = {}
        mock_collection.roles = ["sample_role"]
        mock_collection.plugins = {PluginType.MODULE: ["sample_module"]}
        mock_instance.parse.return_value = mock_collection
        mock_parser.return_value = mock_instance

        # Create test collection directory
        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        result = runner.invoke(collection, ["parse", str(collection_dir)])

        assert result.exit_code == 0
        assert "test_namespace.test_collection" in result.output
        # Should be valid JSON - extract JSON part (may have logs before it)
        try:
            # Find JSON by looking for the first '{'
            json_start = result.output.find("{")
            if json_start >= 0:
                json_output = result.output[json_start:]
                output_data = json.loads(json_output)
                assert output_data["fqcn"] == "test_namespace.test_collection"
            else:
                pytest.fail("No JSON found in output")
        except json.JSONDecodeError as e:
            pytest.fail(f"Output is not valid JSON: {e}")

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_parse_outputs_to_file_with_output_option(self, mock_parser, runner, tmp_path):
        """Test that parse command can output to a file."""
        # Setup mock
        mock_instance = Mock()
        mock_collection = Mock()
        mock_collection.metadata.fqcn = "test_namespace.test_collection"
        mock_collection.metadata.version = "1.0.0"
        mock_collection.metadata.namespace = "test_namespace"
        mock_collection.metadata.name = "test_collection"
        mock_collection.metadata.authors = ["Test Author"]
        mock_collection.metadata.dependencies = {}
        mock_collection.roles = []
        mock_collection.plugins = {}
        mock_instance.parse.return_value = mock_collection
        mock_parser.return_value = mock_instance

        # Create test directories
        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()
        output_file = tmp_path / "output.json"

        result = runner.invoke(
            collection, ["parse", str(collection_dir), "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify file content
        with open(output_file) as f:
            data = json.load(f)
            assert data["fqcn"] == "test_namespace.test_collection"

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_parse_pretty_prints_json_with_pretty_flag(self, mock_parser, runner, tmp_path):
        """Test that --pretty flag produces indented JSON."""
        # Setup mock
        mock_instance = Mock()
        mock_collection = Mock()
        mock_collection.metadata.fqcn = "test_namespace.test_collection"
        mock_collection.metadata.version = "1.0.0"
        mock_collection.metadata.namespace = "test_namespace"
        mock_collection.metadata.name = "test_collection"
        mock_collection.metadata.authors = ["Test Author"]
        mock_collection.metadata.dependencies = {}
        mock_collection.roles = []
        mock_collection.plugins = {}
        mock_instance.parse.return_value = mock_collection
        mock_parser.return_value = mock_instance

        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        result = runner.invoke(collection, ["parse", str(collection_dir), "--pretty"])

        assert result.exit_code == 0
        # Extract JSON part (may have logs before it)
        json_start = result.output.find("{")
        assert json_start >= 0, "No JSON found in output"
        json_output = result.output[json_start:]
        # Pretty-printed JSON has indentation (multiple spaces or newlines)
        assert "  " in json_output or "\n" in json_output
        # Should still be valid JSON
        json.loads(json_output)


class TestCollectionParseCommandValidation:
    """Test collection parse command validation mode."""

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_validate_flag_parses_but_produces_no_output(self, mock_parser, runner, tmp_path):
        """Test that --validate flag parses collection but produces no JSON output."""
        # Setup mock
        mock_instance = Mock()
        mock_collection = Mock()
        mock_instance.parse.return_value = mock_collection
        mock_parser.return_value = mock_instance

        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        result = runner.invoke(collection, ["parse", str(collection_dir), "--validate"])

        assert result.exit_code == 0
        # Should not contain JSON output
        with pytest.raises(json.JSONDecodeError):
            json.loads(result.output)
        # Should indicate validation success
        assert "valid" in result.output.lower() or "success" in result.output.lower()

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_validate_flag_exits_with_error_on_invalid_collection(
        self, mock_parser, runner, tmp_path
    ):
        """Test that --validate flag exits with error code for invalid collections."""
        # Setup mock to raise ParsingError
        mock_instance = Mock()
        mock_instance.parse.side_effect = ParsingError("Invalid collection")
        mock_parser.return_value = mock_instance

        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        result = runner.invoke(collection, ["parse", str(collection_dir), "--validate"])

        assert result.exit_code != 0


class TestCollectionParseCommandErrorHandling:
    """Test collection parse command error handling."""

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_parse_handles_nonexistent_collection_path(self, mock_parser, runner):
        """Test that parse command handles non-existent collection paths gracefully."""
        mock_instance = Mock()
        mock_instance.parse.side_effect = ParsingError("Collection directory does not exist")
        mock_parser.return_value = mock_instance

        result = runner.invoke(collection, ["parse", "/nonexistent/path"])

        assert result.exit_code != 0
        assert "error" in result.output.lower() or "does not exist" in result.output.lower()

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_parse_handles_missing_galaxy_yml(self, mock_parser, runner, tmp_path):
        """Test that parse command handles missing galaxy.yml gracefully."""
        mock_instance = Mock()
        mock_instance.parse.side_effect = ParsingError("galaxy.yml not found")
        mock_parser.return_value = mock_instance

        collection_dir = tmp_path / "invalid_collection"
        collection_dir.mkdir()

        result = runner.invoke(collection, ["parse", str(collection_dir)])

        assert result.exit_code != 0
        assert "galaxy.yml" in result.output.lower()

    @patch("ansibledoctor.cli.collection.CollectionParser")
    def test_parse_provides_actionable_error_messages(self, mock_parser, runner, tmp_path):
        """Test that error messages include actionable suggestions."""
        mock_instance = Mock()
        mock_instance.parse.side_effect = ParsingError("Invalid namespace format in galaxy.yml")
        mock_parser.return_value = mock_instance

        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        result = runner.invoke(collection, ["parse", str(collection_dir)])

        assert result.exit_code != 0
        # Error message should be descriptive
        assert len(result.output) > 20


class TestCollectionParseCommandIntegration:
    """Test collection parse command with real (non-mocked) parsing."""

    def test_parse_real_collection_end_to_end(self, runner, tmp_path):
        """Test parsing a real collection directory end-to-end."""
        # Create a minimal valid collection
        collection_dir = tmp_path / "test_namespace.test_collection"
        collection_dir.mkdir()

        # Create galaxy.yml
        galaxy_file = collection_dir / "galaxy.yml"
        galaxy_file.write_text(
            """
namespace: test_namespace
name: test_collection
version: 1.0.0
authors:
  - Test Author
dependencies: {}
"""
        )

        # Create roles directory
        (collection_dir / "roles" / "sample_role").mkdir(parents=True)
        (collection_dir / "roles" / "sample_role" / "meta").mkdir()
        (collection_dir / "roles" / "sample_role" / "meta" / "main.yml").write_text("---\n")

        # Create plugins directory
        (collection_dir / "plugins" / "modules").mkdir(parents=True)
        (collection_dir / "plugins" / "modules" / "sample_module.py").write_text(
            '"""Sample module."""\n'
        )

        result = runner.invoke(collection, ["parse", str(collection_dir)])

        assert result.exit_code == 0

        # Extract JSON part (may have logs before it)
        json_start = result.output.find("{")
        assert json_start >= 0, "No JSON found in output"
        json_output = result.output[json_start:]

        # Verify JSON output
        output_data = json.loads(json_output)
        assert output_data["fqcn"] == "test_namespace.test_collection"
        assert output_data["version"] == "1.0.0"
        assert "sample_role" in output_data["roles"]
        assert "module" in output_data["plugins"]
        assert "sample_module" in output_data["plugins"]["module"]
