"""Collection structure discovery walker.

This module walks collection directory structure to discover roles and
plugins. Follows the no-exclusions policy: parses all Python files,
lets validation filtering handle invalid plugins.

Following Constitution Article X (DDD): Infrastructure layer for
collection structure discovery.
"""

from pathlib import Path
from typing import Dict, List

from ansibledoctor.models.plugin import PluginType
from ansibledoctor.utils.fs_walker import FileSystemWalker
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class CollectionStructureWalker:
    """
    Walker for discovering Ansible collection structure.

    Discovers:
    - Roles in roles/ directory
    - Plugins in plugins/ subdirectories

    Delegates to FileSystemWalker for low-level file system operations.
    """

    def __init__(self) -> None:
        """Initialize walker with file system utilities."""
        self.fs_walker = FileSystemWalker()

    def discover_roles(self, roles_directory: Path) -> List[str]:
        """
        Discover role names in roles/ directory.

        Args:
            roles_directory: Path to collection's roles/ directory

        Returns:
            List of role names (subdirectory names)

        Example:
            >>> walker = CollectionStructureWalker()
            >>> walker.discover_roles(Path("./roles"))
            ['web_server', 'database']
        """
        logger.debug("discovering_roles", roles_directory=str(roles_directory))

        role_names = self.fs_walker.discover_roles(roles_directory)

        logger.info(
            "roles_discovered",
            roles_directory=str(roles_directory),
            count=len(role_names),
        )

        return role_names

    def discover_plugins(self, plugins_directory: Path) -> Dict[PluginType, List[Path]]:
        """
        Discover plugins in plugins/ subdirectories.

        Follows no-exclusions policy: Discovers ALL Python files in plugin
        directories. Validation filtering happens at parser layer.

        Args:
            plugins_directory: Path to collection's plugins/ directory

        Returns:
            Dictionary mapping PluginType to list of plugin file paths

        Example:
            >>> walker = CollectionStructureWalker()
            >>> plugins = walker.discover_plugins(Path("./plugins"))
            >>> PluginType.MODULE in plugins
            True
        """
        logger.debug("discovering_plugins", plugins_directory=str(plugins_directory))

        discovered = self.fs_walker.discover_plugins(plugins_directory)

        total_count = sum(len(files) for files in discovered.values())
        logger.info(
            "plugins_discovered",
            plugins_directory=str(plugins_directory),
            plugin_types=len(discovered),
            total_plugins=total_count,
        )

        return discovered
