"""Main entry point for parsing Ansible collections.

This module provides the CollectionParser class, which orchestrates the parsing
of galaxy.yml metadata and collection structure discovery to build a complete
AnsibleCollection model.

Architecture:
    - Coordinates GalaxyMetadataParser and CollectionStructureWalker
    - Validates collection directory paths
    - Builds and returns AnsibleCollection aggregate root
    - Provides comprehensive error handling with actionable messages

Example:
    >>> from pathlib import Path
    >>> parser = CollectionParser()
    >>> collection = parser.parse(Path("my_namespace.my_collection"))
    >>> print(collection.metadata.fqcn)
    my_namespace.my_collection
"""

import logging
from pathlib import Path
from typing import Dict, List, Union

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.plugin import PluginType
from ansibledoctor.parser.base_validator import BaseValidator
from ansibledoctor.parser.collection_walker import CollectionStructureWalker
from ansibledoctor.parser.galaxy_parser import GalaxyMetadataParser
from ansibledoctor.parser.plugin_discovery import PluginDiscovery
from ansibledoctor.utils.paths import CollectionPathResolver

logger = logging.getLogger(__name__)


class CollectionParser:
    """Parser for Ansible collections.

    Orchestrates parsing of galaxy.yml and collection structure to build
    a complete AnsibleCollection model. This is the main entry point for
    collection parsing operations.

    Attributes:
        _galaxy_parser: Parser for galaxy.yml files
        _structure_walker: Walker for discovering roles and plugins
        _path_resolver: Resolver for collection paths

    Example:
        >>> parser = CollectionParser()
        >>> collection = parser.parse(Path("community.general"))
        >>> print(f"Parsed {collection.metadata.fqcn} v{collection.metadata.version}")
        Parsed community.general v5.0.0
    """

    def __init__(self) -> None:
        """Initialize the CollectionParser with required components."""
        self._galaxy_parser = GalaxyMetadataParser()
        self._structure_walker = CollectionStructureWalker()
        self._path_resolver = CollectionPathResolver()
        self._plugin_discovery: PluginDiscovery | None = None
        logger.debug("CollectionParser initialized")

    def parse(self, collection_path: Union[str, Path]) -> AnsibleCollection:
        """Parse a collection directory and return AnsibleCollection model.

        This method:
        1. Validates the collection path exists and is a directory
        2. Parses galaxy.yml to extract metadata
        3. Discovers roles and plugins in the collection structure
        4. Builds and returns a complete AnsibleCollection model

        Args:
            collection_path: Path to the collection directory

        Returns:
            AnsibleCollection model with metadata, roles, and plugins

        Raises:
            ParsingError: If collection path is invalid, galaxy.yml is missing/invalid,
                         or parsing fails for any reason

        Example:
            >>> parser = CollectionParser()
            >>> collection = parser.parse("ansible.posix")
            >>> print(collection.roles)
            ['firewalld', 'selinux', 'mount']
        """
        collection_path = Path(collection_path)

        # Validate collection path
        self._validate_collection_path(collection_path)

        logger.info(f"Parsing collection at {collection_path}")

        try:
            # Parse galaxy.yml metadata
            galaxy_yml_path = self._path_resolver.get_galaxy_yml_path(collection_path)
            metadata = self._galaxy_parser.parse(galaxy_yml_path)
            logger.debug(f"Parsed galaxy.yml for {metadata.fqcn}")

            # Discover roles
            roles_dir = self._path_resolver.get_roles_directory(collection_path)
            roles = []
            if roles_dir and roles_dir.exists():
                roles = self._structure_walker.discover_roles(roles_dir)
                logger.debug(f"Discovered {len(roles)} roles")
            else:
                logger.debug("No roles directory found")

            # Discover plugins using PluginDiscovery
            self._plugin_discovery = PluginDiscovery(collection_path)
            discovered_plugins = self._plugin_discovery.discover_plugins()

            # Group plugins by type for the collection model
            plugins: Dict[PluginType, List[str]] = {}
            for plugin in discovered_plugins:
                if plugin.type not in plugins:
                    plugins[plugin.type] = []
                plugins[plugin.type].append(plugin.name)

            total_plugins = len(discovered_plugins)
            logger.debug(f"Discovered {total_plugins} plugins across {len(plugins)} types")

            # Build AnsibleCollection model
            collection = AnsibleCollection(
                metadata=metadata,
                roles=roles,
                plugins=plugins
            )

            logger.info(f"Successfully parsed collection {metadata.fqcn} "
                       f"({len(roles)} roles, {sum(len(p) for p in plugins.values())} plugins)")

            return collection

        except ParsingError:
            # Re-raise ParsingErrors as-is (already have context and suggestions)
            raise
        except Exception as e:
            # Wrap other exceptions with actionable error message
            logger.error(f"Unexpected error parsing collection: {e}", exc_info=True)
            raise BaseValidator.create_actionable_error(
                message=f"Failed to parse collection at {collection_path}: {e}",
                context={
                    "collection_path": str(collection_path),
                    "error_type": type(e).__name__,
                    "error": str(e)
                },
                suggestion="Check collection structure and file permissions",
                troubleshooting_steps=[
                    "Verify the collection has a valid galaxy.yml file",
                    "Ensure you have read permissions for the collection directory",
                    "Check that roles/ and plugins/ directories are accessible",
                    "Run 'ansible-galaxy collection list' to see installed collections",
                    f"Try: cd {collection_path} && ls -la"
                ]
            ) from e

    def _validate_collection_path(self, collection_path: Path) -> None:
        """Validate that the collection path exists and is a directory.

        Args:
            collection_path: Path to validate

        Raises:
            ParsingError: If path doesn't exist or is not a directory
        """
        BaseValidator.validate_directory_exists(
            collection_path,
            dir_type="collection directory",
            suggestion=(
                "Ensure the path points to a valid Ansible collection directory. "
                "Collections typically contain galaxy.yml, roles/, and/or plugins/ directories. "
                "If the collection is not installed, run 'ansible-galaxy collection install <fqcn>'."
            )
        )
