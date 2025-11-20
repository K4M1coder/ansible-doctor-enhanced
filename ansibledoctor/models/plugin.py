"""Plugin model for Ansible collection plugins.

This module defines the Plugin value object and PluginType enum for
representing Ansible plugins (modules, filters, lookups, tests, etc.).
"""

from enum import Enum


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
                f"Unknown plugin directory '{dirname}'. "
                f"Valid directories: {valid}"
            )
        
        return mapping[dirname]


# Plugin model will be implemented in US9 (T086-T090)
