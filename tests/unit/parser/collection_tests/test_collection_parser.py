"""Test suite for CollectionParser class.

Tests the main entry point that orchestrates galaxy.yml parsing and collection structure discovery.
"""

from pathlib import Path

import pytest

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.plugin import PluginType
from ansibledoctor.parser.collection_parser import CollectionParser


class TestCollectionParserValidCollection:
    """Test CollectionParser with valid collection structure."""

    def test_parse_returns_ansible_collection_model(self, tmp_path):
        """Test that parse() returns an AnsibleCollection model."""
        # Create minimal valid collection
        collection_dir = tmp_path / "test_namespace.test_collection"
        collection_dir.mkdir()

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

        parser = CollectionParser()
        result = parser.parse(collection_dir)

        assert isinstance(result, AnsibleCollection)
        assert result.metadata.namespace == "test_namespace"
        assert result.metadata.name == "test_collection"
        assert "sample_role" in result.roles
        assert PluginType.MODULE in result.plugins


class TestCollectionParserPathValidation:
    """Test CollectionParser path validation."""

    def test_raises_error_for_nonexistent_path(self):
        """Test that parse() raises error for non-existent collection path."""
        parser = CollectionParser()

        with pytest.raises(ParsingError, match="collection directory does not exist"):
            parser.parse(Path("/nonexistent/path"))

    def test_raises_error_for_file_instead_of_directory(self, tmp_path):
        """Test that parse() raises error when path is a file, not a directory."""
        file_path = tmp_path / "not_a_directory.txt"
        file_path.write_text("content")

        parser = CollectionParser()

        with pytest.raises(ParsingError, match="Path must be a directory"):
            parser.parse(file_path)


class TestCollectionParserGalaxyIntegration:
    """Test CollectionParser integration with GalaxyMetadataParser."""

    def test_raises_error_for_missing_galaxy_yml(self, tmp_path):
        """Test that parse() raises error when galaxy.yml is missing."""
        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        parser = CollectionParser()

        with pytest.raises(ParsingError, match="galaxy.yml not found"):
            parser.parse(collection_dir)

    def test_raises_error_for_invalid_galaxy_yml(self, tmp_path):
        """Test that parse() raises error for malformed galaxy.yml."""
        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        galaxy_file = collection_dir / "galaxy.yml"
        galaxy_file.write_text("invalid: yaml: {unclosed")

        parser = CollectionParser()

        with pytest.raises(ParsingError):
            parser.parse(collection_dir)


class TestCollectionParserStructureIntegration:
    """Test CollectionParser integration with CollectionStructureWalker."""

    def test_handles_collection_without_roles(self, tmp_path):
        """Test that parse() handles collections with no roles gracefully."""
        collection_dir = tmp_path / "test_namespace.test_collection"
        collection_dir.mkdir()

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

        parser = CollectionParser()
        result = parser.parse(collection_dir)

        assert isinstance(result, AnsibleCollection)
        assert result.roles == []

    def test_handles_collection_without_plugins(self, tmp_path):
        """Test that parse() handles collections with no plugins gracefully."""
        collection_dir = tmp_path / "test_namespace.test_collection"
        collection_dir.mkdir()

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

        parser = CollectionParser()
        result = parser.parse(collection_dir)

        assert isinstance(result, AnsibleCollection)
        assert result.plugins == {}


class TestCollectionParserErrorHandling:
    """Test CollectionParser error handling and logging."""

    def test_provides_actionable_error_message_for_missing_galaxy(self, tmp_path):
        """Test that error messages include actionable suggestions."""
        collection_dir = tmp_path / "test_collection"
        collection_dir.mkdir()

        parser = CollectionParser()

        with pytest.raises(ParsingError) as exc_info:
            parser.parse(collection_dir)

        assert "galaxy.yml" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()

    def test_logs_successful_parse(self, tmp_path, caplog):
        """Test that successful parsing is logged."""
        import logging

        caplog.set_level(logging.INFO)

        collection_dir = tmp_path / "test_namespace.test_collection"
        collection_dir.mkdir()

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

        parser = CollectionParser()
        _ = parser.parse(collection_dir)

        assert "Successfully parsed collection" in caplog.text
        assert "test_namespace.test_collection" in caplog.text


class TestCollectionParserCompleteIntegration:
    """Test CollectionParser with complete collection structure."""

    def test_parses_collection_with_all_components(self, tmp_path):
        """Test parsing a collection with roles, multiple plugin types, and full metadata."""
        collection_dir = tmp_path / "community.example"
        collection_dir.mkdir()

        # Create galaxy.yml with dependencies
        galaxy_file = collection_dir / "galaxy.yml"
        galaxy_file.write_text(
            """
namespace: community
name: example
version: 2.1.0
authors:
  - John Doe <john@example.com>
  - Jane Smith
dependencies:
  ansible.posix: ">=1.0.0"
  community.general: "*"
"""
        )

        # Create multiple roles
        for role_name in ["web_server", "database", "monitoring"]:
            role_dir = collection_dir / "roles" / role_name
            role_dir.mkdir(parents=True)
            (role_dir / "meta").mkdir()
            (role_dir / "meta" / "main.yml").write_text("---\n")

        # Create multiple plugin types
        plugins_dir = collection_dir / "plugins"

        # Modules
        (plugins_dir / "modules").mkdir(parents=True)
        (plugins_dir / "modules" / "example_module.py").write_text('"""Example module."""\n')

        # Filters
        (plugins_dir / "filters").mkdir(parents=True)
        (plugins_dir / "filters" / "example_filter.py").write_text('"""Example filter."""\n')

        # Lookups
        (plugins_dir / "lookups").mkdir(parents=True)
        (plugins_dir / "lookups" / "example_lookup.py").write_text('"""Example lookup."""\n')

        parser = CollectionParser()
        result = parser.parse(collection_dir)

        # Verify metadata
        assert result.metadata.fqcn == "community.example"
        assert result.metadata.version == "2.1.0"
        assert len(result.metadata.authors) == 2
        assert "ansible.posix" in result.metadata.dependencies

        # Verify roles
        assert len(result.roles) == 3
        assert "web_server" in result.roles
        assert "database" in result.roles
        assert "monitoring" in result.roles

        # Verify plugins
        assert PluginType.MODULE in result.plugins
        assert PluginType.FILTER in result.plugins
        assert PluginType.LOOKUP in result.plugins
        assert len(result.plugins[PluginType.MODULE]) >= 1
