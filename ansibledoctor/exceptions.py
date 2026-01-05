"""
Exception hierarchy for Ansible Doctor Enhanced.

Following Constitution Article on Error Handling: all exceptions include
clear error messages, contextual information, and actionable recovery suggestions.

Exit Codes (for CLI integration):
- 0: Success
- 1: Fatal error (parsing failure, validation error, exception)
- 2: Warnings present (only with --fail-on-warnings flag)
- 3: Invalid usage (bad arguments, missing required flags)
"""

from typing import Any, Optional


# Exit code constants for CI/CD integration (User Story 5)
EXIT_SUCCESS = 0      # Operation completed successfully
EXIT_ERROR = 1        # Fatal error occurred (parsing, validation, exceptions)
EXIT_WARNING = 2      # Warnings treated as errors (with --fail-on-warnings)
EXIT_INVALID = 3      # Invalid command-line usage


class AnsibleDoctorError(Exception):
    """
    Base exception for all Ansible Doctor errors.

    All exceptions in this module extend this base class, providing a clear
    hierarchy for error handling and consistent error reporting.

    Attributes:
        message: Human-readable error description
        context: Dict containing contextual information (file_path, line_number, etc.)
        suggestion: Actionable recovery suggestion for the user
        exit_code: Exit code for CLI (default: 1 for errors)
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        exit_code: int = 1,
    ) -> None:
        """
        Initialize base exception with message, context, and recovery suggestion.

        Args:
            message: Clear description of what went wrong
            context: Contextual information (e.g., {"file_path": "...", "line_number": 42})
            suggestion: Actionable suggestion (e.g., "Check YAML syntax in defaults/main.yml")
            exit_code: Exit code for CLI (default: 1)
        """
        self.message = message
        self.context = context or {}
        self.suggestion = suggestion
        self.exit_code = exit_code

        # Build full error message with context
        full_message = message
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            full_message = f"{message} (context: {context_str})"
        if suggestion:
            full_message = f"{full_message}\nSuggestion: {suggestion}"

        super().__init__(full_message)


class ParsingError(AnsibleDoctorError):
    """
    Raised when parsing Ansible role files fails.

    Examples:
        - YAML syntax errors
        - Malformed annotation syntax
        - Invalid role directory structure
        - Circular dependency detection
    """

    pass


class ValidationError(AnsibleDoctorError):
    """
    Raised when data validation fails.

    Examples:
        - Missing required metadata fields
        - Invalid variable types
        - Constraint violations in Pydantic models
    """

    pass


class ConfigError(AnsibleDoctorError):
    """
    Raised when configuration is invalid or missing.

    Examples:
        - Missing required configuration options
        - Invalid configuration file syntax
        - Conflicting configuration values
    
    Exit code: 3 (invalid usage)
    """
    
    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize with exit code 3 for configuration errors."""
        super().__init__(message, context, suggestion, exit_code=3)


class TemplateError(AnsibleDoctorError):
    """
    Raised when template rendering fails.

    Examples:
        - Template syntax errors
        - Missing template variables
        - Template file not found
    """

    pass
