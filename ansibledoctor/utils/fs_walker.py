"""File system walker for discovering collection structure.

This module provides utilities for walking collection directories to
discover roles and plugins. Follows the no-exclusions policy: parses
all Python files, lets validation filtering handle invalid plugins.

Following Constitution Article X (DDD): Infrastructure layer for
file system operations.
"""

from pathlib import Path
from typing import Dict, List

from ansibledoctor.models.plugin import PluginType
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class FileSystemWalker:
    """
    Walker for discovering collection directory structure.

    Implements collection-specific discovery:
    - Roles in roles/ directory
    - Plugins in plugins/ subdirectories
    - No file exclusions (validation filtering at parser layer)
    """

    @staticmethod
    def discover_roles(roles_directory: Path) -> List[str]:
        """
        Discover role names in roles/ directory.

        Args:
            roles_directory: Path to collection's roles/ directory

        Returns:
            List of role names (subdirectory names)

        Example:
            >>> walker = FileSystemWalker()
            >>> walker.discover_roles(Path("./roles"))
            ['web_server', 'database', 'cache']
        """
        if not roles_directory.exists() or not roles_directory.is_dir():
            logger.warning("roles_directory_not_found", path=str(roles_directory))
            return []

        # Get all subdirectories in roles/
        role_names = [
            subdir.name
            for subdir in roles_directory.iterdir()
            if subdir.is_dir() and not subdir.name.startswith(".")
        ]

        logger.info(
            "roles_discovered",
            roles_directory=str(roles_directory),
            count=len(role_names),
            roles=role_names,
        )

        return sorted(role_names)

    @staticmethod
    def discover_plugins(plugins_directory: Path) -> Dict[PluginType, List[Path]]:
        """
        Discover plugins in plugins/ subdirectories.

        Follows no-exclusions policy: Discovers ALL Python files in plugin
        directories. Validation filtering happens at parser layer to handle
        __init__.py, __pycache__, .pyc files, etc.

        Args:
            plugins_directory: Path to collection's plugins/ directory

        Returns:
            Dictionary mapping PluginType to list of plugin file paths

        Example:
            >>> walker = FileSystemWalker()
            >>> walker.discover_plugins(Path("./plugins"))
            {
                PluginType.MODULE: [Path('plugins/modules/my_module.py')],
                PluginType.FILTER: [Path('plugins/filters/my_filter.py')]
            }
        """
        if not plugins_directory.exists() or not plugins_directory.is_dir():
            logger.warning("plugins_directory_not_found", path=str(plugins_directory))
            return {}

        discovered: Dict[PluginType, List[Path]] = {}

        # Walk all subdirectories in plugins/
        for plugin_dir in plugins_directory.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
                continue

            # Detect plugin type from directory name
            try:
                plugin_type = PluginType.from_directory_name(plugin_dir.name)
            except ValueError as e:
                logger.debug(
                    "unknown_plugin_directory",
                    directory=plugin_dir.name,
                    error=str(e),
                )
                continue

            # Discover all Python files (no exclusions)
            python_files = list(plugin_dir.glob("*.py"))

            if python_files:
                discovered[plugin_type] = sorted(python_files)
                logger.debug(
                    "plugins_discovered",
                    plugin_type=str(plugin_type),
                    directory=str(plugin_dir),
                    count=len(python_files),
                )

        total_count = sum(len(files) for files in discovered.values())
        logger.info(
            "plugin_discovery_complete",
            plugins_directory=str(plugins_directory),
            plugin_types=len(discovered),
            total_plugins=total_count,
        )

        return discovered

    @staticmethod
    def list_subdirectories(directory: Path) -> List[Path]:
        """
        List all subdirectories in a directory.

        Args:
            directory: Parent directory to scan

        Returns:
            List of subdirectory paths
        """
        if not directory.exists() or not directory.is_dir():
            return []

        return sorted(
            [
                subdir
                for subdir in directory.iterdir()
                if subdir.is_dir() and not subdir.name.startswith(".")
            ]
        )
