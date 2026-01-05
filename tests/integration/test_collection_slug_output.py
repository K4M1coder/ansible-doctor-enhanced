"""Integration tests for collection slug output paths.

Verifies that the CLI correctly generates output paths using collection slugs
and respects the --legacy-output flag.
"""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from ansibledoctor.cli.collection import collection
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.galaxy import GalaxyMetadata


@pytest.fixture
def runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_collection():
    """Create a mock AnsibleCollection."""
    metadata = GalaxyMetadata(
        namespace="my_namespace",
        name="my_collection",
        version="1.0.0",
        authors=["Author"],
        dependencies={},
    )
    return AnsibleCollection(
        metadata=metadata,
        roles=[],
        plugins={},
    )


@patch("ansibledoctor.cli.collection.CollectionParser")
@patch("ansibledoctor.parser.plugin_discovery.PluginDiscovery")
@patch("ansibledoctor.generator.collection_generator.CollectionDocumentationGenerator")
def test_generate_default_slug_output(
    mock_generator_cls, mock_discovery_cls, mock_parser_cls, runner, mock_collection, tmp_path
):
    """Test that generate command uses slug-based output path by default."""
    # Setup mocks
    mock_parser_instance = Mock()
    mock_parser_instance.parse.return_value = mock_collection
    mock_parser_cls.return_value = mock_parser_instance

    mock_discovery_instance = Mock()
    mock_discovery_instance.discover_plugins.return_value = []
    mock_discovery_cls.return_value = mock_discovery_instance

    mock_generator_instance = Mock()
    mock_generator_cls.return_value = mock_generator_instance

    # Create dummy collection dir
    collection_dir = tmp_path / "my_collection"
    collection_dir.mkdir()

    # Run command
    result = runner.invoke(collection, ["generate", str(collection_dir)])

    assert result.exit_code == 0

    # Verify generator was called with correct output path
    # Expected: collection_dir / docs / lang / en / collection_my-namespace.my-collection / README.md
    expected_slug = "collection_my-namespace.my-collection"
    expected_path = collection_dir / "docs" / "lang" / "en" / expected_slug / "README.md"

    mock_generator_instance.generate.assert_called_once()
    call_args = mock_generator_instance.generate.call_args
    assert call_args.kwargs["output_path"] == expected_path


@patch("ansibledoctor.cli.collection.CollectionParser")
@patch("ansibledoctor.parser.plugin_discovery.PluginDiscovery")
@patch("ansibledoctor.generator.collection_generator.CollectionDocumentationGenerator")
def test_generate_legacy_output(
    mock_generator_cls, mock_discovery_cls, mock_parser_cls, runner, mock_collection, tmp_path
):
    """Test that generate command uses legacy output path with flag."""
    # Setup mocks
    mock_parser_instance = Mock()
    mock_parser_instance.parse.return_value = mock_collection
    mock_parser_cls.return_value = mock_parser_instance

    mock_discovery_instance = Mock()
    mock_discovery_instance.discover_plugins.return_value = []
    mock_discovery_cls.return_value = mock_discovery_instance

    mock_generator_instance = Mock()
    mock_generator_cls.return_value = mock_generator_instance

    # Create dummy collection dir
    collection_dir = tmp_path / "my_collection"
    collection_dir.mkdir()

    # Run command with --legacy-output
    result = runner.invoke(collection, ["generate", str(collection_dir), "--legacy-output"])

    assert result.exit_code == 0

    # Verify generator was called with legacy output path
    # Expected: collection_dir / docs / README.md
    expected_path = collection_dir / "docs" / "README.md"

    mock_generator_instance.generate.assert_called_once()
    call_args = mock_generator_instance.generate.call_args
    assert call_args.kwargs["output_path"] == expected_path


@patch("ansibledoctor.cli.collection.CollectionParser")
@patch("ansibledoctor.parser.plugin_discovery.PluginDiscovery")
@patch("ansibledoctor.generator.collection_generator.CollectionDocumentationGenerator")
def test_generate_custom_output_dir_slug(
    mock_generator_cls, mock_discovery_cls, mock_parser_cls, runner, mock_collection, tmp_path
):
    """Test that generate command respects custom output dir with slug structure."""
    # Setup mocks
    mock_parser_instance = Mock()
    mock_parser_instance.parse.return_value = mock_collection
    mock_parser_cls.return_value = mock_parser_instance

    mock_discovery_instance = Mock()
    mock_discovery_instance.discover_plugins.return_value = []
    mock_discovery_cls.return_value = mock_discovery_instance

    mock_generator_instance = Mock()
    mock_generator_cls.return_value = mock_generator_instance

    # Create dummy collection dir
    collection_dir = tmp_path / "my_collection"
    collection_dir.mkdir()

    # Custom output dir
    output_dir = "build/docs"

    # Run command
    result = runner.invoke(
        collection, ["generate", str(collection_dir), "--output-dir", output_dir]
    )

    assert result.exit_code == 0

    # Verify generator was called with correct output path
    # Expected: collection_dir / build / docs / lang / en / collection_my-namespace.my-collection / README.md
    # Note: "docs" prefix from build_context_path is stripped because output_dir is custom
    expected_slug = "collection_my-namespace.my-collection"
    expected_path = collection_dir / "build" / "docs" / "lang" / "en" / expected_slug / "README.md"

    mock_generator_instance.generate.assert_called_once()
    call_args = mock_generator_instance.generate.call_args
    assert call_args.kwargs["output_path"] == expected_path
