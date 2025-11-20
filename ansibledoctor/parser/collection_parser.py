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
from typing import Union

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.parser.collection_walker import CollectionStructureWalker
from ansibledoctor.parser.galaxy_parser import GalaxyMetadataParser
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
            
            # Discover plugins
            plugins_dir = self._path_resolver.get_plugins_directory(collection_path)
            plugins = {}
            if plugins_dir and plugins_dir.exists():
                plugins_paths = self._structure_walker.discover_plugins(plugins_dir)
                # Convert Path objects to strings (plugin filenames without extension)
                plugins = {
                    plugin_type: [path.stem for path in paths]
                    for plugin_type, paths in plugins_paths.items()
                }
                total_plugins = sum(len(plugin_list) for plugin_list in plugins.values())
                logger.debug(f"Discovered {total_plugins} plugins across {len(plugins)} types")
            else:
                logger.debug("No plugins directory found")
            
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
            # Re-raise ParsingErrors as-is
            raise
        except Exception as e:
            # Wrap other exceptions in ParsingError with context
            error_msg = (f"Failed to parse collection at {collection_path}: {e}")
            logger.error(error_msg, exc_info=True)
            raise ParsingError(error_msg) from e

    def _validate_collection_path(self, collection_path: Path) -> None:
        """Validate that the collection path exists and is a directory.
        
        Args:
            collection_path: Path to validate
        
        Raises:
            ParsingError: If path doesn't exist or is not a directory
        """
        if not collection_path.exists():
            raise ParsingError(
                f"Collection directory does not exist: {collection_path}\n"
                f"Please ensure the path is correct and the collection is properly installed."
            )
        
        if not collection_path.is_dir():
            raise ParsingError(
                f"Path must be a directory, not a file: {collection_path}\n"
                f"Please provide a path to a collection directory."
            )
