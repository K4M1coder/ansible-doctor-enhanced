"""Plugin model for Ansible collection plugins.

This module defines the Plugin value object and PluginType enum for
representing Ansible plugins (modules, filters, lookups, tests, etc.).

Following Constitution Article X (DDD): Plugin is a Value Object within
the Collection aggregate. PluginCatalog is a Repository pattern for
grouping plugins by type.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class PluginType(str, Enum):
    """Ansible plugin types supported by collections.

    Based on Ansible Galaxy plugin directory structure:
    - plugins/modules/: Modules
    - plugins/filters/: Jinja2 filters
    - plugins/lookups/: Lookup plugins
    - plugins/tests/: Jinja2 tests
    - plugins/inventory/: Inventory plugins
    - plugins/callbacks/: Callback plugins
    """

    MODULE = "module"
    FILTER = "filter"
    LOOKUP = "lookup"
    TEST = "test"
    INVENTORY = "inventory"
    CALLBACK = "callback"

    def __str__(self) -> str:
        """Return human-readable plugin type."""
        return self.value

    @classmethod
    def from_directory_name(cls, dirname: str) -> "PluginType":
        """Detect plugin type from directory name.

        Args:
            dirname: Directory name (e.g., "modules", "filters")

        Returns:
            PluginType enum value

        Raises:
            ValueError: If directory name doesn't match any plugin type

        Example:
            >>> PluginType.from_directory_name("modules")
            <PluginType.MODULE: 'module'>
        """
        mapping = {
            "modules": cls.MODULE,
            "filters": cls.FILTER,
            "lookups": cls.LOOKUP,
            "tests": cls.TEST,
            "inventory": cls.INVENTORY,
            "callbacks": cls.CALLBACK,
        }

        if dirname not in mapping:
            valid = ", ".join(mapping.keys())
            raise ValueError(
                f"Unknown plugin directory '{dirname}'. " f"Valid directories: {valid}"
            )

        return mapping[dirname]


class Plugin(BaseModel):
    """
    Ansible plugin value object.

    Represents a single plugin file within a collection (module, filter,
    lookup, test, inventory, or callback). Immutable value object.

    Attributes:
        name: Plugin name (extracted from filename without .py extension)
        type: Plugin type (module, filter, lookup, etc.)
        path: Absolute path to the plugin file
        short_description: Optional brief description of plugin functionality

    Example:
        >>> plugin = Plugin(
        ...     name="my_module",
        ...     type=PluginType.MODULE,
        ...     path=Path("/collection/plugins/modules/my_module.py"),
        ...     short_description="Example module"
        ... )
        >>> plugin.name
        'my_module'
    """

    name: str = Field(..., description="Plugin name (filename without .py extension)")
    type: PluginType = Field(..., description="Plugin type (module, filter, lookup, etc.)")
    path: Path = Field(..., description="Absolute path to plugin file")
    short_description: Optional[str] = Field(
        None, description="Brief description of plugin functionality"
    )
    documentation: Dict[str, Any] = Field(
        default_factory=dict, description="Parsed DOCUMENTATION block"
    )
    examples: Optional[str] = Field(
        None, description="Parsed EXAMPLES block"
    )
    return_values: Dict[str, Any] = Field(
        default_factory=dict, description="Parsed RETURN block"
    )

    model_config = {"frozen": True}  # Immutable value object

    def __str__(self) -> str:
        """String representation with name and type."""
        return f"{self.name} ({self.type.value})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Plugin(name='{self.name}', type={self.type.value})"


class PluginCatalog:
    """
    Repository for organizing and querying plugins.

    Groups plugins by type and provides query methods for retrieving
    plugins by type or listing all plugin names.

    This follows the Repository pattern from DDD: encapsulates plugin
    collection logic separate from the domain models.

    Attributes:
        plugins: List of Plugin objects in the catalog

    Example:
        >>> plugins = [
        ...     Plugin(name="mod1", type=PluginType.MODULE, path=Path("/mod1.py")),
        ...     Plugin(name="filt1", type=PluginType.FILTER, path=Path("/filt1.py")),
        ... ]
        >>> catalog = PluginCatalog(plugins=plugins)
        >>> catalog.count()
        2
        >>> catalog.count_by_type(PluginType.MODULE)
        1
    """

    def __init__(self, plugins: List[Plugin]) -> None:
        """
        Initialize catalog with list of plugins.

        Args:
            plugins: List of Plugin objects
        """
        self.plugins = plugins

    def group_by_type(self) -> Dict[PluginType, List[Plugin]]:
        """
        Group plugins by their type.

        Returns:
            Dictionary mapping PluginType to list of Plugin objects

        Example:
            >>> catalog = PluginCatalog(plugins=[...])
            >>> grouped = catalog.group_by_type()
            >>> grouped[PluginType.MODULE]
            [Plugin(name='mod1', ...), Plugin(name='mod2', ...)]
        """
        grouped: Dict[PluginType, List[Plugin]] = {}

        for plugin in self.plugins:
            if plugin.type not in grouped:
                grouped[plugin.type] = []
            grouped[plugin.type].append(plugin)

        return grouped

    def list_all_names(self) -> List[str]:
        """
        Get list of all plugin names in catalog.

        Returns:
            List of plugin names (strings)

        Example:
            >>> catalog.list_all_names()
            ['my_module', 'my_filter', 'my_lookup']
        """
        return [plugin.name for plugin in self.plugins]

    def list_names_by_type(self, plugin_type: PluginType) -> List[str]:
        """
        Get list of plugin names for a specific type.

        Args:
            plugin_type: PluginType to filter by

        Returns:
            List of plugin names matching the type

        Example:
            >>> catalog.list_names_by_type(PluginType.MODULE)
            ['module1', 'module2']
        """
        return [plugin.name for plugin in self.plugins if plugin.type == plugin_type]

    def count(self) -> int:
        """
        Count total plugins in catalog.

        Returns:
            Total number of plugins
        """
        return len(self.plugins)

    def count_by_type(self, plugin_type: PluginType) -> int:
        """
        Count plugins of a specific type.

        Args:
            plugin_type: PluginType to count

        Returns:
            Number of plugins matching the type
        """
        return len(self.list_names_by_type(plugin_type))


# Plugin model will be implemented in US9 (T086-T090)
