"""Base validator for common validation patterns.

This module provides reusable validation logic extracted from parsers to follow
the DRY principle and ensure consistent error handling.

Following Constitution Article X (DDD): Infrastructure validation utilities
that can be reused across different parsers.
"""

from pathlib import Path
from typing import Optional

from ansibledoctor.exceptions import ParsingError


class BaseValidator:
    """
    Base validator providing common validation patterns for parsers.
    
    Centralizes path validation, file existence checks, and directory validation
    to avoid duplication across GalaxyMetadataParser, CollectionParser, etc.
    """
    
    @staticmethod
    def validate_file_exists(
        file_path: Path,
        file_type: str = "file",
        suggestion: Optional[str] = None
    ) -> None:
        """
        Validate that a file exists and is readable.
        
        Args:
            file_path: Path to the file
            file_type: Description of file type for error messages (e.g., "galaxy.yml")
            suggestion: Optional suggestion for fixing the error
        
        Raises:
            ParsingError: If file doesn't exist
        
        Example:
            >>> BaseValidator.validate_file_exists(
            ...     Path("galaxy.yml"),
            ...     file_type="galaxy.yml",
            ...     suggestion="Ensure this is a valid Ansible collection"
            ... )
        """
        if not file_path.exists():
            default_suggestion = (
                f"Ensure the {file_type} exists at the expected location"
            )
            raise ParsingError(
                f"{file_type} not found: {file_path}",
                context={"file_path": str(file_path), "file_type": file_type},
                suggestion=suggestion or default_suggestion,
            )
    
    @staticmethod
    def validate_directory_exists(
        dir_path: Path,
        dir_type: str = "directory",
        suggestion: Optional[str] = None
    ) -> None:
        """
        Validate that a directory exists and is accessible.
        
        Args:
            dir_path: Path to the directory
            dir_type: Description of directory type for error messages
            suggestion: Optional suggestion for fixing the error
        
        Raises:
            ParsingError: If directory doesn't exist or is not a directory
        
        Example:
            >>> BaseValidator.validate_directory_exists(
            ...     Path("my_collection"),
            ...     dir_type="collection directory"
            ... )
        """
        if not dir_path.exists():
            default_suggestion = (
                f"Ensure the {dir_type} exists at the specified path. "
                f"Check for typos or verify the path is correct."
            )
            raise ParsingError(
                f"{dir_type} does not exist: {dir_path}",
                context={"directory_path": str(dir_path), "directory_type": dir_type},
                suggestion=suggestion or default_suggestion,
            )
        
        if not dir_path.is_dir():
            raise ParsingError(
                f"Path must be a directory, not a file: {dir_path}",
                context={"path": str(dir_path), "directory_type": dir_type},
                suggestion=f"Provide a path to a {dir_type}, not a file.",
            )
    
    @staticmethod
    def validate_path_is_directory(
        path: Path,
        path_type: str = "path"
    ) -> None:
        """
        Validate that a path is a directory (assumes path exists).
        
        Args:
            path: Path to validate
            path_type: Description of path type for error messages
        
        Raises:
            ParsingError: If path is not a directory
        """
        if not path.is_dir():
            raise ParsingError(
                f"{path_type} must be a directory, not a file: {path}",
                context={"path": str(path), "path_type": path_type},
                suggestion=f"Ensure {path} is a directory.",
            )
    
    @staticmethod
    def create_actionable_error(
        message: str,
        context: dict,
        suggestion: str,
        troubleshooting_steps: Optional[list[str]] = None
    ) -> ParsingError:
        """
        Create a ParsingError with actionable suggestions and troubleshooting steps.
        
        Args:
            message: Error message
            context: Context dictionary with error details
            suggestion: Primary suggestion for fixing the error
            troubleshooting_steps: Optional list of troubleshooting steps
        
        Returns:
            ParsingError with enhanced context
        
        Example:
            >>> error = BaseValidator.create_actionable_error(
            ...     message="Invalid YAML syntax",
            ...     context={"file": "galaxy.yml"},
            ...     suggestion="Check YAML syntax using 'yamllint'",
            ...     troubleshooting_steps=[
            ...         "Run 'yamllint galaxy.yml' to identify syntax errors",
            ...         "Ensure proper indentation (use spaces, not tabs)",
            ...         "Validate YAML at https://www.yamllint.com/"
            ...     ]
            ... )
        """
        if troubleshooting_steps:
            full_suggestion = f"{suggestion}\n\nTroubleshooting steps:\n"
            for i, step in enumerate(troubleshooting_steps, 1):
                full_suggestion += f"{i}. {step}\n"
            suggestion = full_suggestion.strip()
        
        return ParsingError(
            message=message,
            context=context,
            suggestion=suggestion
        )
