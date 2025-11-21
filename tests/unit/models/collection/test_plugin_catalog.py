"""Unit tests for PluginCatalog.

Following Constitution Article III (TDD): Write tests FIRST (RED phase).
"""

from pathlib import Path

import pytest

from ansibledoctor.models.plugin import Plugin, PluginCatalog, PluginType


class TestPluginCatalog:
    """Tests for PluginCatalog grouping and listing functionality."""
    
    def test_catalog_groups_plugins_by_type(self) -> None:
        """Test that PluginCatalog groups plugins by PluginType."""
        plugins = [
            Plugin(name="mod1", type=PluginType.MODULE, path=Path("/mod1.py")),
            Plugin(name="mod2", type=PluginType.MODULE, path=Path("/mod2.py")),
            Plugin(name="filt1", type=PluginType.FILTER, path=Path("/filt1.py")),
            Plugin(name="look1", type=PluginType.LOOKUP, path=Path("/look1.py")),
        ]
        
        catalog = PluginCatalog(plugins=plugins)
        grouped = catalog.group_by_type()
        
        assert PluginType.MODULE in grouped
        assert PluginType.FILTER in grouped
        assert PluginType.LOOKUP in grouped
        
        assert len(grouped[PluginType.MODULE]) == 2
        assert len(grouped[PluginType.FILTER]) == 1
        assert len(grouped[PluginType.LOOKUP]) == 1
    
    def test_catalog_with_empty_plugins_list(self) -> None:
        """Test PluginCatalog with no plugins."""
        catalog = PluginCatalog(plugins=[])
        grouped = catalog.group_by_type()
        
        assert grouped == {}
        assert catalog.list_all_names() == []
    
    def test_catalog_lists_all_plugin_names(self) -> None:
        """Test list_all_names() returns all plugin names."""
        plugins = [
            Plugin(name="plugin_a", type=PluginType.MODULE, path=Path("/a.py")),
            Plugin(name="plugin_b", type=PluginType.FILTER, path=Path("/b.py")),
            Plugin(name="plugin_c", type=PluginType.LOOKUP, path=Path("/c.py")),
        ]
        
        catalog = PluginCatalog(plugins=plugins)
        names = catalog.list_all_names()
        
        assert len(names) == 3
        assert "plugin_a" in names
        assert "plugin_b" in names
        assert "plugin_c" in names
    
    def test_catalog_lists_names_by_type_modules(self) -> None:
        """Test list_names_by_type() returns plugins of specific type."""
        plugins = [
            Plugin(name="mod1", type=PluginType.MODULE, path=Path("/mod1.py")),
            Plugin(name="mod2", type=PluginType.MODULE, path=Path("/mod2.py")),
            Plugin(name="filt1", type=PluginType.FILTER, path=Path("/filt1.py")),
        ]
        
        catalog = PluginCatalog(plugins=plugins)
        module_names = catalog.list_names_by_type(PluginType.MODULE)
        
        assert len(module_names) == 2
        assert "mod1" in module_names
        assert "mod2" in module_names
        assert "filt1" not in module_names
    
    def test_catalog_lists_names_by_type_filters(self) -> None:
        """Test list_names_by_type() for filters."""
        plugins = [
            Plugin(name="mod1", type=PluginType.MODULE, path=Path("/mod1.py")),
            Plugin(name="filt1", type=PluginType.FILTER, path=Path("/filt1.py")),
            Plugin(name="filt2", type=PluginType.FILTER, path=Path("/filt2.py")),
        ]
        
        catalog = PluginCatalog(plugins=plugins)
        filter_names = catalog.list_names_by_type(PluginType.FILTER)
        
        assert len(filter_names) == 2
        assert "filt1" in filter_names
        assert "filt2" in filter_names
    
    def test_catalog_lists_names_by_type_empty(self) -> None:
        """Test list_names_by_type() returns empty list for missing type."""
        plugins = [
            Plugin(name="mod1", type=PluginType.MODULE, path=Path("/mod1.py")),
        ]
        
        catalog = PluginCatalog(plugins=plugins)
        lookup_names = catalog.list_names_by_type(PluginType.LOOKUP)
        
        assert lookup_names == []
    
    def test_catalog_count_total_plugins(self) -> None:
        """Test counting total plugins in catalog."""
        plugins = [
            Plugin(name="p1", type=PluginType.MODULE, path=Path("/p1.py")),
            Plugin(name="p2", type=PluginType.FILTER, path=Path("/p2.py")),
            Plugin(name="p3", type=PluginType.LOOKUP, path=Path("/p3.py")),
        ]
        
        catalog = PluginCatalog(plugins=plugins)
        
        assert catalog.count() == 3
    
    def test_catalog_count_by_type(self) -> None:
        """Test counting plugins by specific type."""
        plugins = [
            Plugin(name="mod1", type=PluginType.MODULE, path=Path("/mod1.py")),
            Plugin(name="mod2", type=PluginType.MODULE, path=Path("/mod2.py")),
            Plugin(name="filt1", type=PluginType.FILTER, path=Path("/filt1.py")),
        ]
        
        catalog = PluginCatalog(plugins=plugins)
        
        assert catalog.count_by_type(PluginType.MODULE) == 2
        assert catalog.count_by_type(PluginType.FILTER) == 1
        assert catalog.count_by_type(PluginType.LOOKUP) == 0
