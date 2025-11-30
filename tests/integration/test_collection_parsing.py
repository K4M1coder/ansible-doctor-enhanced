"""
Integration tests for comprehensive collection parsing.

Tests parsing of collections with all possible plugin types and galaxy.yml fields
to ensure complete feature coverage.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.plugin import PluginType
from ansibledoctor.parser.collection_parser import CollectionParser


@pytest.fixture
def comprehensive_collection_path(tmp_path):
    """
    Path to the comprehensive collection fixture.

    Collection with ALL plugin types:
    - modules
    - filters
    - lookups
    - tests
    - inventory
    - callbacks
    """
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "collections"
    return fixtures_dir / "comprehensive_collection"


class TestComprehensiveCollectionParsing:
    """Test parsing collections with all plugin types."""

    def test_parse_collection_with_all_plugin_types(self, comprehensive_collection_path):
        """
        Test parsing collection with all 6 plugin types.

        Verifies:
        - All plugin types are discovered
        - Each plugin type has at least one plugin
        - No plugin types are missing
        """
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        assert isinstance(collection, AnsibleCollection)
        assert collection.metadata.namespace == "comprehensive"
        assert collection.metadata.name == "test"

        # Verify all 6 plugin types are present
        assert PluginType.MODULE in collection.plugins
        assert PluginType.FILTER in collection.plugins
        assert PluginType.LOOKUP in collection.plugins
        assert PluginType.TEST in collection.plugins
        assert PluginType.INVENTORY in collection.plugins
        assert PluginType.CALLBACK in collection.plugins

    def test_module_plugin_discovery(self, comprehensive_collection_path):
        """Test module plugin is discovered correctly."""
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        modules = collection.plugins[PluginType.MODULE]
        assert len(modules) == 1
        assert "test_module" in modules

    def test_filter_plugin_discovery(self, comprehensive_collection_path):
        """Test filter plugin is discovered correctly."""
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        filters = collection.plugins[PluginType.FILTER]
        assert len(filters) == 1
        assert "test_filter" in filters

    def test_lookup_plugin_discovery(self, comprehensive_collection_path):
        """Test lookup plugin is discovered correctly."""
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        lookups = collection.plugins[PluginType.LOOKUP]
        assert len(lookups) == 1
        assert "test_lookup" in lookups

    def test_test_plugin_discovery(self, comprehensive_collection_path):
        """Test test plugin is discovered correctly."""
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        tests = collection.plugins[PluginType.TEST]
        assert len(tests) == 1
        assert "test_test" in tests

    def test_inventory_plugin_discovery(self, comprehensive_collection_path):
        """Test inventory plugin is discovered correctly."""
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        inventory = collection.plugins[PluginType.INVENTORY]
        assert len(inventory) == 1
        assert "test_inventory" in inventory

    def test_callback_plugin_discovery(self, comprehensive_collection_path):
        """Test callback plugin is discovered correctly."""
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        callbacks = collection.plugins[PluginType.CALLBACK]
        assert len(callbacks) == 1
        assert "test_callback" in callbacks

    def test_role_discovery_in_comprehensive_collection(self, comprehensive_collection_path):
        """Test role discovery in comprehensive collection."""
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        assert len(collection.roles) == 1
        assert "app" in collection.roles

    def test_comprehensive_collection_json_export(self, comprehensive_collection_path):
        """
        Test comprehensive collection can be exported to JSON.

        Verifies:
        - All plugin types are in JSON output
        - All data is serializable
        - No data loss in serialization
        """
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        json_data = collection.model_dump(mode="json")

        # Verify metadata
        assert json_data["metadata"]["namespace"] == "comprehensive"
        assert json_data["metadata"]["name"] == "test"
        assert json_data["metadata"]["version"] == "1.0.0"

        # Verify all plugin types present in JSON
        assert "module" in json_data["plugins"]
        assert "filter" in json_data["plugins"]
        assert "lookup" in json_data["plugins"]
        assert "test" in json_data["plugins"]
        assert "inventory" in json_data["plugins"]
        assert "callback" in json_data["plugins"]

        # Verify role
        assert len(json_data["roles"]) == 1
        assert "app" in json_data["roles"]


class TestEdgeCasesAndValidation:
    """Test edge cases in collection parsing."""

    def test_collection_with_no_plugins(self, tmp_path):
        """
        Test parsing collection with no plugins directory.

        Verifies parser handles missing plugins/ gracefully.
        """
        collection_path = tmp_path / "no_plugins"
        collection_path.mkdir()
        (collection_path / "roles").mkdir()

        galaxy_yml = collection_path / "galaxy.yml"
        galaxy_yml.write_text(
            """---
namespace: test
name: no_plugins
version: 1.0.0
authors:
  - "Test Author"
dependencies: {}
"""
        )

        parser = CollectionParser()
        collection = parser.parse(collection_path)

        assert collection.metadata.namespace == "test"
        assert len(collection.plugins) == 0

    def test_collection_with_no_roles(self, tmp_path):
        """
        Test parsing collection with no roles directory.

        Verifies parser handles missing roles/ gracefully.
        """
        collection_path = tmp_path / "no_roles"
        collection_path.mkdir()
        (collection_path / "plugins").mkdir()

        galaxy_yml = collection_path / "galaxy.yml"
        galaxy_yml.write_text(
            """---
namespace: test
name: no_roles
version: 1.0.0
authors:
  - "Test Author"
dependencies: {}
"""
        )

        parser = CollectionParser()
        collection = parser.parse(collection_path)

        assert collection.metadata.namespace == "test"
        assert len(collection.roles) == 0

    def test_collection_with_empty_dependencies(self, comprehensive_collection_path):
        """
        Test parsing collection with empty dependencies dict.

        Verifies empty dependencies are handled correctly.
        """
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        assert collection.metadata.dependencies == {}

    def test_plugin_type_count_verification(self, comprehensive_collection_path):
        """
        Verify exact plugin type count matches PluginType enum.

        Ensures all plugin types defined in PluginType enum are tested.
        """
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        # Should have exactly 6 plugin types (as defined in PluginType enum)
        expected_types = {
            PluginType.MODULE,
            PluginType.FILTER,
            PluginType.LOOKUP,
            PluginType.TEST,
            PluginType.INVENTORY,
            PluginType.CALLBACK,
        }

        actual_types = set(collection.plugins.keys())
        assert actual_types == expected_types
