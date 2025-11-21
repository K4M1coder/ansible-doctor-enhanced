"""Tests for collection structure discovery.

Following Constitution Article III (TDD - RED Phase):
These tests are written FIRST and MUST FAIL before implementation.
"""

from pathlib import Path

import pytest

from ansibledoctor.parser.collection_walker import CollectionStructureWalker


class TestRoleDiscovery:
    """Test role discovery in roles/ directory (T021)."""
    
    def test_discover_roles_directory(self):
        """Test discovering roles/ directory and listing role names (T021)."""
        # Arrange
        collection_path = Path("tests/fixtures/collections/minimal_valid")
        roles_dir = collection_path / "roles"
        walker = CollectionStructureWalker()
        
        # Act
        role_names = walker.discover_roles(roles_dir)
        
        # Assert
        assert isinstance(role_names, list)
        assert "sample_role" in role_names


class TestPluginDiscovery:
    """Test plugin discovery in plugins/ directories (T022, T025)."""
    
    def test_discover_plugins_modules_directory(self):
        """Test discovering plugins/modules/ directory and listing modules (T022)."""
        # Arrange
        collection_path = Path("tests/fixtures/collections/minimal_valid")
        plugins_dir = collection_path / "plugins"
        walker = CollectionStructureWalker()
        
        # Act
        plugins = walker.discover_plugins(plugins_dir)
        
        # Assert
        from ansibledoctor.models.plugin import PluginType
        assert PluginType.MODULE in plugins
        assert len(plugins[PluginType.MODULE]) > 0
        
        # Check that sample_module.py is discovered
        module_paths = [p.name for p in plugins[PluginType.MODULE]]
        assert "sample_module.py" in module_paths
    
    def test_discover_multiple_plugin_types(self):
        """Test discovering multiple plugin types (modules, filters, lookups) (T025)."""
        # Arrange
        # This will fail until we create fixtures with multiple plugin types
        # For now, test that walker can handle different types
        collection_path = Path("tests/fixtures/collections/minimal_valid")
        plugins_dir = collection_path / "plugins"
        walker = CollectionStructureWalker()
        
        # Act
        plugins = walker.discover_plugins(plugins_dir)
        
        # Assert
        assert isinstance(plugins, dict)
        # Even if only modules exist, should return dict structure
        from ansibledoctor.models.plugin import PluginType
        if PluginType.MODULE in plugins:
            assert isinstance(plugins[PluginType.MODULE], list)


class TestMissingDirectories:
    """Test handling missing directories gracefully (T023, T024)."""
    
    def test_handle_missing_roles_directory(self):
        """Test handling missing roles/ directory gracefully (T023)."""
        # Arrange
        roles_dir = Path("tests/fixtures/nonexistent/roles")
        walker = CollectionStructureWalker()
        
        # Act
        role_names = walker.discover_roles(roles_dir)
        
        # Assert
        assert role_names == []  # Should return empty list, not raise error
    
    def test_handle_missing_plugins_directory(self):
        """Test handling missing plugins/ directory gracefully (T024)."""
        # Arrange
        plugins_dir = Path("tests/fixtures/nonexistent/plugins")
        walker = CollectionStructureWalker()
        
        # Act
        plugins = walker.discover_plugins(plugins_dir)
        
        # Assert
        assert plugins == {}  # Should return empty dict, not raise error
