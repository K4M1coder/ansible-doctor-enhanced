"""
Path utilities for Ansible role validation and file discovery.

Following Constitution Article X (DDD): Infrastructure concerns isolated
from domain logic, respecting .ansibledoctor-ignore patterns.
"""

from pathlib import Path
from typing import Optional

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from ansibledoctor.exceptions import ValidationError
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class RolePathValidator:
    """
    Validator for Ansible role directory structure.
    
    Ensures role paths meet expected structure conventions before parsing.
    """

    EXPECTED_DIRS = ["tasks", "defaults", "vars", "meta", "handlers", "templates", "files"]
    REQUIRED_DIRS = ["tasks"]  # At minimum, role must have tasks/

    @staticmethod
    def validate_role_structure(role_path: Path) -> bool:
        """
        Validate that path is a valid Ansible role directory.
        
        Args:
            role_path: Path to check
            
        Returns:
            True if valid role structure
            
        Raises:
            ValidationError: If path doesn't exist or isn't a valid role
        """
        if not role_path.exists():
            raise ValidationError(
                f"Role path does not exist: {role_path}",
                context={"role_path": str(role_path)},
                suggestion="Check the path and ensure the role directory exists",
            )

        if not role_path.is_dir():
            raise ValidationError(
                f"Role path is not a directory: {role_path}",
                context={"role_path": str(role_path)},
                suggestion="Provide a path to a directory, not a file",
            )

        # Check for at least one required directory
        has_required = any((role_path / req_dir).exists() for req_dir in RolePathValidator.REQUIRED_DIRS)
        
        if not has_required:
            logger.warning(
                "role_missing_required_directories",
                role_path=str(role_path),
                required=RolePathValidator.REQUIRED_DIRS,
            )
            raise ValidationError(
                f"Role directory missing required subdirectories: {RolePathValidator.REQUIRED_DIRS}",
                context={"role_path": str(role_path)},
                suggestion="Ensure role has at least a 'tasks/' directory with task definitions",
            )

        logger.info("role_structure_valid", role_path=str(role_path))
        return True

    @staticmethod
    def get_role_subdirs(role_path: Path) -> dict[str, Optional[Path]]:
        """
        Get paths to standard role subdirectories.
        
        Args:
            role_path: Root role directory
            
        Returns:
            Dictionary mapping subdir name to path (None if doesn't exist)
        """
        subdirs = {}
        for dir_name in RolePathValidator.EXPECTED_DIRS:
            subdir = role_path / dir_name
            subdirs[dir_name] = subdir if subdir.exists() else None
        
        return subdirs


class IgnorePatternMatcher:
    """
    Matcher for .ansibledoctor-ignore patterns.
    
    Uses gitignore-style patterns via pathspec library to exclude files
    from parsing.
    """

    def __init__(self, role_path: Path) -> None:
        """
        Initialize ignore pattern matcher.
        
        Args:
            role_path: Role directory to check for .ansibledoctor-ignore file
        """
        self.role_path = role_path
        self.spec: Optional[PathSpec] = None
        self._load_ignore_patterns()

    def _load_ignore_patterns(self) -> None:
        """Load patterns from .ansibledoctor-ignore if present."""
        ignore_file = self.role_path / ".ansibledoctor-ignore"
        
        if not ignore_file.exists():
            logger.debug("no_ignore_file", role_path=str(self.role_path))
            return

        try:
            with open(ignore_file, "r", encoding="utf-8") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
            
            self.spec = PathSpec.from_lines(GitWildMatchPattern, patterns)
            
            logger.info(
                "ignore_patterns_loaded",
                role_path=str(self.role_path),
                pattern_count=len(patterns),
            )
            
        except Exception as e:
            logger.warning(
                "ignore_file_read_failed",
                role_path=str(self.role_path),
                error=str(e),
            )

    def should_ignore(self, file_path: Path) -> bool:
        """
        Check if file should be ignored based on patterns.
        
        Args:
            file_path: File path to check (relative to role root)
            
        Returns:
            True if file matches ignore patterns, False otherwise
        """
        if self.spec is None:
            return False

        try:
            # Get path relative to role root
            rel_path = file_path.relative_to(self.role_path)
            result = self.spec.match_file(str(rel_path))
            
            if result:
                logger.debug("file_ignored", file_path=str(file_path))
            
            return result
            
        except ValueError:
            # File not relative to role_path
            return False


def find_yaml_files(directory: Path, pattern: str = "*.yml") -> list[Path]:
    """
    Find all YAML files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (default: *.yml)
        
    Returns:
        List of YAML file paths
    """
    if not directory.exists() or not directory.is_dir():
        return []

    files = sorted(directory.glob(pattern))
    
    logger.debug(
        "yaml_files_found",
        directory=str(directory),
        pattern=pattern,
        count=len(files),
    )
    
    return files


def get_role_name(role_path: Path) -> str:
    """
    Extract role name from directory path.
    
    Args:
        role_path: Path to role directory
        
    Returns:
        Role name (directory name)
    """
    return role_path.name


class CollectionPathResolver:
    """
    Path resolver for Ansible collection directory structures.
    
    Handles collection path resolution for:
    - Local filesystem collections
    - Galaxy-installed collections
    - Git repository collections
    
    Performance optimization (T082): Caches resolved paths to avoid
    repeated filesystem operations for the same collection.
    
    Following Constitution Article X (DDD): Infrastructure layer utility
    for collection path operations.
    """
    
    def __init__(self) -> None:
        """Initialize resolver with empty cache for performance optimization."""
        self._path_cache: dict[str, Path] = {}
        self._roles_cache: dict[str, Path | None] = {}
        self._plugins_cache: dict[str, Path | None] = {}
    
    def resolve_collection_path(self, collection_path: str | Path) -> Path:
        """
        Resolve collection path to absolute Path object.
        
        Caches resolved paths for performance (T082).
        
        Args:
            collection_path: Path to collection (string or Path)
            
        Returns:
            Resolved absolute Path
            
        Raises:
            ValidationError: If path doesn't exist
            
        Example:
            >>> resolver = CollectionPathResolver()
            >>> resolver.resolve_collection_path("./my_namespace.my_collection")
            PosixPath('/absolute/path/to/my_namespace.my_collection')
        """
        cache_key = str(collection_path)
        
        # Return cached result if available
        if cache_key in self._path_cache:
            logger.debug("collection_path_cache_hit", path=cache_key)
            return self._path_cache[cache_key]
        
        path = Path(collection_path).resolve()
        
        if not path.exists():
            raise ValidationError(
                f"Collection path does not exist: {collection_path}",
                context={"collection_path": str(collection_path)},
                suggestion="Check the path and ensure the collection directory exists",
            )
        
        if not path.is_dir():
            raise ValidationError(
                f"Collection path is not a directory: {collection_path}",
                context={"collection_path": str(collection_path)},
                suggestion="Provide a path to a collection directory, not a file",
            )
        
        # Cache the resolved path
        self._path_cache[cache_key] = path
        logger.debug("collection_path_resolved", original=str(collection_path), resolved=str(path))
        return path
    
    def get_galaxy_yml_path(self, collection_path: Path) -> Path:
        """
        Get path to galaxy.yml file in collection.
        
        Args:
            collection_path: Collection root directory
            
        Returns:
            Path to galaxy.yml
            
        Raises:
            ValidationError: If galaxy.yml doesn't exist
        """
        galaxy_yml = collection_path / "galaxy.yml"
        
        if not galaxy_yml.exists():
            raise ValidationError(
                f"galaxy.yml not found in collection: {collection_path}",
                context={"collection_path": str(collection_path)},
                suggestion="Ensure this is a valid Ansible collection with a galaxy.yml file",
            )
        
        return galaxy_yml
    
    def get_roles_directory(self, collection_path: Path) -> Path | None:
        """
        Get roles/ directory path if it exists.
        
        Caches results for performance (T082).
        
        Args:
            collection_path: Collection root directory
            
        Returns:
            Path to roles/ directory, or None if not found
        """
        cache_key = str(collection_path)
        
        if cache_key in self._roles_cache:
            return self._roles_cache[cache_key]
        
        roles_dir = collection_path / "roles"
        result = roles_dir if roles_dir.exists() and roles_dir.is_dir() else None
        self._roles_cache[cache_key] = result
        return result
    
    def get_plugins_directory(self, collection_path: Path) -> Path | None:
        """
        Get plugins/ directory path if it exists.
        
        Caches results for performance (T082).
        
        Args:
            collection_path: Collection root directory
            
        Returns:
            Path to plugins/ directory, or None if not found
        """
        cache_key = str(collection_path)
        
        if cache_key in self._plugins_cache:
            return self._plugins_cache[cache_key]
        
        plugins_dir = collection_path / "plugins"
        result = plugins_dir if plugins_dir.exists() and plugins_dir.is_dir() else None
        self._plugins_cache[cache_key] = result
        return result
    
    @staticmethod
    def extract_fqcn_from_path(collection_path: Path) -> tuple[str, str] | None:
        """
        Extract FQCN (namespace.name) from collection directory name.
        
        Args:
            collection_path: Collection directory path
            
        Returns:
            Tuple of (namespace, name) if path follows convention, else None
            
        Example:
            >>> CollectionPathResolver.extract_fqcn_from_path(Path("community.general"))
            ('community', 'general')
        """
        dirname = collection_path.name
        
        if "." in dirname:
            parts = dirname.split(".", 1)
            if len(parts) == 2:
                return (parts[0], parts[1])
        
        return None
