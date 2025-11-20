"""Plugin discovery parser for Ansible collections (T121-T128).

This module discovers plugins within a collection's plugins/ directory,
detecting plugin types from directory structure and extracting plugin
metadata.

Following Constitution Article X (DDD): PluginDiscovery is a Service
within the Collection aggregate, responsible for discovering Plugin
value objects.
"""

import structlog
from pathlib import Path
from typing import List

from ansibledoctor.models.plugin import Plugin, PluginType

logger = structlog.get_logger(__name__)


class PluginDiscovery:
    """
    Service for discovering plugins in an Ansible collection.
    
    Scans the collection's plugins/ directory tree, identifies Python
    plugin files, extracts plugin names and types from file paths.
    
    Attributes:
        collection_path: Path to collection root directory
    
    Example:
        >>> discovery = PluginDiscovery(Path("/path/to/collection"))
        >>> plugins = discovery.discover_plugins()
        >>> print(f"Found {len(plugins)} plugins")
    """
    
    def __init__(self, collection_path: Path) -> None:
        """
        Initialize PluginDiscovery with collection path.
        
        Args:
            collection_path: Path to collection root directory
        """
        self.collection_path = collection_path
        self.plugins_root = collection_path / "plugins"
    
    def discover_plugins(self) -> List[Plugin]:
        """
        Discover all plugins in the collection's plugins/ directory.
        
        Scans plugins/ tree for Python files, detects plugin types from
        directory names, extracts plugin names from filenames. Per TC-002,
        all Python files are discovered; validation filtering happens later.
        
        Returns:
            List of discovered Plugin objects (empty if no plugins found)
        
        Example:
            >>> discovery = PluginDiscovery(Path("/collection"))
            >>> plugins = discovery.discover_plugins()
            >>> modules = [p for p in plugins if p.type == PluginType.MODULE]
        """
        # Check if plugins/ directory exists
        if not self.plugins_root.exists():
            logger.info(
                "no_plugins_directory",
                collection_path=str(self.collection_path),
                message="Collection has no plugins/ directory",
            )
            return []
        
        plugins: List[Plugin] = []
        
        # Scan all Python files recursively in plugins/
        for py_file in self.plugins_root.rglob("*.py"):
            try:
                plugin = self._create_plugin_from_file(py_file)
                plugins.append(plugin)
                logger.debug(
                    "plugin_discovered",
                    name=plugin.name,
                    type=plugin.type.value,
                    path=str(plugin.path),
                )
            except ValueError as e:
                # Skip files in invalid plugin directories
                logger.warning(
                    "invalid_plugin_directory",
                    file=str(py_file),
                    error=str(e),
                )
                continue
        
        logger.info(
            "plugin_discovery_complete",
            collection_path=str(self.collection_path),
            total_plugins=len(plugins),
        )
        
        return plugins
    
    def _create_plugin_from_file(self, file_path: Path) -> Plugin:
        """
        Create Plugin object from file path.
        
        Extracts plugin name from filename, detects type from directory
        structure. Per TC-002, all Python files are discovered; validation
        happens later.
        
        Args:
            file_path: Path to plugin file (.py)
            
        Returns:
            Plugin object
            
        Raises:
            ValueError: If plugin type cannot be determined from path
        
        Example:
            >>> discovery = PluginDiscovery(Path("/collection"))
            >>> plugin = discovery._create_plugin_from_file(
            ...     Path("/collection/plugins/modules/my_module.py")
            ... )
            >>> print(plugin.name)  # "my_module"
            >>> print(plugin.type)  # PluginType.MODULE
        """
        # Extract plugin name (filename without .py extension)
        plugin_name = file_path.stem
        
        # Detect plugin type from directory path
        plugin_type = self._detect_plugin_type(file_path)
        
        # Create Plugin object (short_description will be extracted later)
        plugin = Plugin(
            name=plugin_name,
            type=plugin_type,
            path=file_path,
            short_description=None,
        )
        
        return plugin
    
    def _detect_plugin_type(self, file_path: Path) -> PluginType:
        """
        Detect plugin type from file path directory structure.
        
        Searches up the directory tree from file_path to find the plugin
        type directory (modules/, filters/, lookups/, etc.). Uses
        PluginType.from_directory_name() for mapping.
        
        Args:
            file_path: Path to plugin file
            
        Returns:
            PluginType enum value
            
        Raises:
            ValueError: If plugin type directory not found in path
        
        Example:
            >>> discovery = PluginDiscovery(Path("/collection"))
            >>> file_path = Path("/collection/plugins/modules/network/cisco/ios.py")
            >>> plugin_type = discovery._detect_plugin_type(file_path)
            >>> print(plugin_type)  # PluginType.MODULE
        """
        # Walk up the directory tree to find plugin type directory
        for parent in file_path.parents:
            # Stop at plugins/ root
            if parent == self.plugins_root:
                break
            
            # Check if parent is a plugin type directory
            try:
                plugin_type = PluginType.from_directory_name(parent.name)
                return plugin_type
            except ValueError:
                # Not a plugin type directory, continue up the tree
                continue
        
        # If we reach here, no valid plugin type directory found
        raise ValueError(
            f"Cannot determine plugin type from path: {file_path}. "
            f"File must be under a valid plugin directory "
            f"(modules/, filters/, lookups/, tests/, inventory/, callbacks/)"
        )
