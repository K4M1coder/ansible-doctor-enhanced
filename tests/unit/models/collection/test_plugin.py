"""Unit tests for Plugin model and PluginType enum.

Following Constitution Article III (TDD): Write tests FIRST (RED phase).
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from ansibledoctor.models.plugin import Plugin, PluginType


class TestPluginType:
    """Tests for PluginType enum."""

    def test_all_six_plugin_types_exist(self) -> None:
        """Test that all 6 Ansible plugin types are defined."""
        expected_types = {
            PluginType.MODULE,
            PluginType.FILTER,
            PluginType.LOOKUP,
            PluginType.TEST,
            PluginType.INVENTORY,
            PluginType.CALLBACK,
        }

        assert len(expected_types) == 6
        assert len(list(PluginType)) == 6

    def test_plugin_type_string_values(self) -> None:
        """Test that plugin types have correct string values."""
        assert PluginType.MODULE.value == "module"
        assert PluginType.FILTER.value == "filter"
        assert PluginType.LOOKUP.value == "lookup"
        assert PluginType.TEST.value == "test"
        assert PluginType.INVENTORY.value == "inventory"
        assert PluginType.CALLBACK.value == "callback"

    def test_from_directory_name_modules(self) -> None:
        """Test detecting MODULE type from 'modules' directory."""
        assert PluginType.from_directory_name("modules") == PluginType.MODULE

    def test_from_directory_name_filters(self) -> None:
        """Test detecting FILTER type from 'filters' directory."""
        assert PluginType.from_directory_name("filters") == PluginType.FILTER

    def test_from_directory_name_lookups(self) -> None:
        """Test detecting LOOKUP type from 'lookups' directory."""
        assert PluginType.from_directory_name("lookups") == PluginType.LOOKUP

    def test_from_directory_name_tests(self) -> None:
        """Test detecting TEST type from 'tests' directory."""
        assert PluginType.from_directory_name("tests") == PluginType.TEST

    def test_from_directory_name_inventory(self) -> None:
        """Test detecting INVENTORY type from 'inventory' directory."""
        assert PluginType.from_directory_name("inventory") == PluginType.INVENTORY

    def test_from_directory_name_callbacks(self) -> None:
        """Test detecting CALLBACK type from 'callbacks' directory."""
        assert PluginType.from_directory_name("callbacks") == PluginType.CALLBACK

    def test_from_directory_name_invalid_raises_error(self) -> None:
        """Test that invalid directory name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            PluginType.from_directory_name("invalid_dir")

        assert "Unknown plugin directory" in str(exc_info.value)
        assert "invalid_dir" in str(exc_info.value)


class TestPlugin:
    """Tests for Plugin model."""

    def test_plugin_with_all_fields(self) -> None:
        """Test creating Plugin with name, type, path, and description."""
        plugin = Plugin(
            name="my_module",
            type=PluginType.MODULE,
            path=Path("/path/to/plugins/modules/my_module.py"),
            short_description="A test module for testing purposes",
        )

        assert plugin.name == "my_module"
        assert plugin.type == PluginType.MODULE
        assert plugin.path == Path("/path/to/plugins/modules/my_module.py")
        assert plugin.short_description == "A test module for testing purposes"

    def test_plugin_with_minimal_required_fields(self) -> None:
        """Test creating Plugin with only required fields (name, type, path)."""
        plugin = Plugin(
            name="simple_filter",
            type=PluginType.FILTER,
            path=Path("/path/to/plugins/filters/simple_filter.py"),
        )

        assert plugin.name == "simple_filter"
        assert plugin.type == PluginType.FILTER
        assert plugin.path == Path("/path/to/plugins/filters/simple_filter.py")
        assert plugin.short_description is None

    def test_plugin_missing_required_name_raises_error(self) -> None:
        """Test that Plugin without name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Plugin(
                type=PluginType.MODULE,
                path=Path("/path/to/module.py"),
            )

        errors = exc_info.value.errors()
        assert any("name" in str(e).lower() for e in errors)

    def test_plugin_missing_required_type_raises_error(self) -> None:
        """Test that Plugin without type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Plugin(
                name="test_plugin",
                path=Path("/path/to/plugin.py"),
            )

        errors = exc_info.value.errors()
        assert any("type" in str(e).lower() for e in errors)

    def test_plugin_missing_required_path_raises_error(self) -> None:
        """Test that Plugin without path raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Plugin(
                name="test_plugin",
                type=PluginType.MODULE,
            )

        errors = exc_info.value.errors()
        assert any("path" in str(e).lower() for e in errors)

    def test_plugin_is_immutable(self) -> None:
        """Test that Plugin is frozen (immutable)."""
        plugin = Plugin(
            name="immutable_plugin",
            type=PluginType.LOOKUP,
            path=Path("/path/to/plugin.py"),
        )

        # Attempt to modify name
        with pytest.raises(ValidationError):
            plugin.name = "different_name"  # type: ignore

        # Attempt to modify type
        with pytest.raises(ValidationError):
            plugin.type = PluginType.FILTER  # type: ignore

    def test_plugin_str_contains_name_and_type(self) -> None:
        """Test that __str__ includes plugin name and type."""
        plugin = Plugin(
            name="my_module",
            type=PluginType.MODULE,
            path=Path("/path/to/module.py"),
        )

        str_repr = str(plugin)
        assert "my_module" in str_repr
        assert "module" in str_repr.lower()

    def test_plugin_repr_contains_name(self) -> None:
        """Test that __repr__ includes plugin name."""
        plugin = Plugin(
            name="test_filter",
            type=PluginType.FILTER,
            path=Path("/path/to/filter.py"),
        )

        repr_str = repr(plugin)
        assert "test_filter" in repr_str
        assert "Plugin" in repr_str
