"""Unit tests for PluginDiscovery parser (T091-T095).

Tests plugin discovery from collection plugins/ directory, including:
- Discovering Python files in plugin directories
- Extracting plugin names from filenames
- Detecting plugin types from directory paths
- Handling empty plugin directories
- Validation filtering for invalid plugins
"""

from pathlib import Path

from ansibledoctor.models.plugin import PluginType
from ansibledoctor.parser.plugin_discovery import PluginDiscovery


class TestPluginDiscovery:
    """Test PluginDiscovery parser for scanning collection plugins."""

    def test_discovers_python_modules_in_plugins_directory(self, tmp_path: Path) -> None:
        """Test: Discover Python modules in plugins/modules/ directory (T091)."""
        # Setup: Create collection with plugins/modules/
        collection_dir = tmp_path / "namespace" / "collection"
        modules_dir = collection_dir / "plugins" / "modules"
        modules_dir.mkdir(parents=True)

        # Create sample module files
        (modules_dir / "my_module.py").write_text(
            '"""My module.\n\nDESCRIPTION:\nExample module.\n"""'
        )
        (modules_dir / "another_module.py").write_text('"""Another module."""')
        (modules_dir / "__init__.py").write_text("")  # Should be discovered

        # Execute: Discover plugins
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: Found all Python files (including __init__.py)
        assert len(plugins) == 3
        plugin_names = [p.name for p in plugins]
        assert "my_module" in plugin_names
        assert "another_module" in plugin_names
        assert "__init__" in plugin_names

        # All should be MODULE type
        for plugin in plugins:
            assert plugin.type == PluginType.MODULE

    def test_extracts_plugin_name_from_filename(self, tmp_path: Path) -> None:
        """Test: Extract plugin name from filename (remove .py extension) (T092)."""
        # Setup: Create plugin file
        collection_dir = tmp_path / "namespace" / "collection"
        filters_dir = collection_dir / "plugins" / "filters"
        filters_dir.mkdir(parents=True)
        (filters_dir / "custom_filter.py").write_text('"""Custom filter."""')

        # Execute: Discover plugins
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: Name extracted correctly (no .py extension)
        assert len(plugins) == 1
        plugin = plugins[0]
        assert plugin.name == "custom_filter"
        assert plugin.type == PluginType.FILTER
        assert plugin.path == filters_dir / "custom_filter.py"

    def test_detects_plugin_type_from_directory_path(self, tmp_path: Path) -> None:
        """Test: Detect plugin type from directory path (T093)."""
        # Setup: Create plugins in multiple directories
        collection_dir = tmp_path / "namespace" / "collection"
        plugins_root = collection_dir / "plugins"

        # Create different plugin types
        type_map = {
            "modules": "example_module.py",
            "filters": "example_filter.py",
            "lookups": "example_lookup.py",
            "tests": "example_test.py",
            "inventory": "example_inventory.py",
            "callbacks": "example_callback.py",
        }

        for dirname, filename in type_map.items():
            plugin_dir = plugins_root / dirname
            plugin_dir.mkdir(parents=True)
            (plugin_dir / filename).write_text(f'"""{dirname} plugin."""')

        # Execute: Discover all plugins
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: Correct types detected
        assert len(plugins) == 6

        # Build map of name -> type for verification
        plugin_map = {p.name: p.type for p in plugins}
        assert plugin_map["example_module"] == PluginType.MODULE
        assert plugin_map["example_filter"] == PluginType.FILTER
        assert plugin_map["example_lookup"] == PluginType.LOOKUP
        assert plugin_map["example_test"] == PluginType.TEST
        assert plugin_map["example_inventory"] == PluginType.INVENTORY
        assert plugin_map["example_callback"] == PluginType.CALLBACK

    def test_handles_empty_plugin_directories(self, tmp_path: Path) -> None:
        """Test: Handle empty plugin directories (return empty list) (T094)."""
        # Setup: Create empty plugins/ directory structure
        collection_dir = tmp_path / "namespace" / "collection"
        plugins_root = collection_dir / "plugins"

        # Create empty directories
        (plugins_root / "modules").mkdir(parents=True)
        (plugins_root / "filters").mkdir(parents=True)
        (plugins_root / "lookups").mkdir(parents=True)

        # Execute: Discover plugins
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: Empty list returned (no plugins found)
        assert plugins == []

    def test_handles_missing_plugins_directory(self, tmp_path: Path) -> None:
        """Test: Handle missing plugins/ directory (return empty list) (T094)."""
        # Setup: Collection without plugins/ directory
        collection_dir = tmp_path / "namespace" / "collection"
        collection_dir.mkdir(parents=True)

        # Execute: Discover plugins
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: Empty list returned
        assert plugins == []

    def test_discovers_plugins_in_nested_subdirectories(self, tmp_path: Path) -> None:
        """Test: Discover plugins in nested subdirectories (T091)."""
        # Setup: Create nested plugin structure (modules/subdir/plugin.py)
        collection_dir = tmp_path / "namespace" / "collection"
        modules_dir = collection_dir / "plugins" / "modules"
        nested_dir = modules_dir / "network" / "cisco"
        nested_dir.mkdir(parents=True)

        # Create plugin in nested directory
        (nested_dir / "ios_command.py").write_text('"""IOS command module."""')

        # Execute: Discover plugins
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: Found nested plugin
        assert len(plugins) == 1
        plugin = plugins[0]
        assert plugin.name == "ios_command"
        assert plugin.type == PluginType.MODULE
        assert plugin.path == nested_dir / "ios_command.py"

    def test_validation_filters_invalid_plugins(self, tmp_path: Path) -> None:
        """Test: Validation filters invalid plugins (parse all, filter invalid) (T095).

        Per TC-002: Parse all Python files, let validation filter invalid ones.
        Invalid plugins (non-Python files, broken syntax) should be discovered
        but may be filtered by validation logic later.
        """
        # Setup: Create mix of valid and potentially invalid files
        collection_dir = tmp_path / "namespace" / "collection"
        modules_dir = collection_dir / "plugins" / "modules"
        modules_dir.mkdir(parents=True)

        # Valid Python file
        (modules_dir / "valid_module.py").write_text('"""Valid module."""')

        # Python file with syntax error (still discovered, validation filters later)
        (modules_dir / "broken_module.py").write_text('"""Broken."""\ndef ( invalid')

        # Non-Python file (should NOT be discovered - only .py files)
        (modules_dir / "readme.txt").write_text("Not a Python file")
        (modules_dir / "config.yaml").write_text("---\nkey: value")

        # Execute: Discover plugins (only .py files)
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: Only Python files discovered (validation happens later)
        # Both valid_module.py and broken_module.py should be discovered
        assert len(plugins) == 2
        plugin_names = [p.name for p in plugins]
        assert "valid_module" in plugin_names
        assert "broken_module" in plugin_names

        # Non-Python files NOT discovered
        assert "readme" not in plugin_names
        assert "config" not in plugin_names

    def test_multiple_plugin_types_in_same_collection(self, tmp_path: Path) -> None:
        """Test: Discover multiple plugin types in same collection (T091)."""
        # Setup: Create collection with modules and filters
        collection_dir = tmp_path / "namespace" / "collection"
        plugins_root = collection_dir / "plugins"

        # Modules
        modules_dir = plugins_root / "modules"
        modules_dir.mkdir(parents=True)
        (modules_dir / "module_a.py").write_text('"""Module A."""')
        (modules_dir / "module_b.py").write_text('"""Module B."""')

        # Filters
        filters_dir = plugins_root / "filters"
        filters_dir.mkdir(parents=True)
        (filters_dir / "filter_x.py").write_text('"""Filter X."""')
        (filters_dir / "filter_y.py").write_text('"""Filter Y."""')
        (filters_dir / "filter_z.py").write_text('"""Filter Z."""')

        # Execute: Discover all plugins
        discovery = PluginDiscovery(collection_dir)
        plugins = discovery.discover_plugins()

        # Verify: All plugins found with correct types
        assert len(plugins) == 5

        modules = [p for p in plugins if p.type == PluginType.MODULE]
        filters = [p for p in plugins if p.type == PluginType.FILTER]

        assert len(modules) == 2
        assert len(filters) == 3

        module_names = [m.name for m in modules]
        assert "module_a" in module_names
        assert "module_b" in module_names

        filter_names = [f.name for f in filters]
        assert "filter_x" in filter_names
        assert "filter_y" in filter_names
        assert "filter_z" in filter_names
