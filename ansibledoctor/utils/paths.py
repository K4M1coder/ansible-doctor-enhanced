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
