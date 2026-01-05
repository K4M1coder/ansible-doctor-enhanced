"""
Exception hierarchy for Ansible Doctor Enhanced.

Following Constitution Article on Error Handling: all exceptions include
clear error messages, contextual information, and actionable recovery suggestions.

Exit Codes (for CLI integration):
- 0: Success
- 1: Fatal error (parsing failure, validation error, exception)
- 2: Warnings present (only with --fail-on-warnings flag)
- 3: Invalid usage (bad arguments, missing required flags)

Error Codes (Spec 010):
- E1xx: Parsing errors (YAML, annotations, etc.)
- E2xx: Validation errors (schema, requirements, etc.)
- E3xx: Generation errors (template rendering, output writing, etc.)
- E4xx: I/O errors (file system, permissions, etc.)
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
        error_code: Error code for categorization (Spec 010)
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        exit_code: int = 1,
        error_code: str = "E000",
    ) -> None:
        """
        Initialize base exception with message, context, and recovery suggestion.

        Args:
            message: Clear description of what went wrong
            context: Contextual information (e.g., {"file_path": "...", "line_number": 42})
            suggestion: Actionable suggestion (e.g., "Check YAML syntax in defaults/main.yml")
            exit_code: Exit code for CLI (default: 1)
            error_code: Error code for categorization (default: E000)
        """
        self.message = message
        self.context = context or {}
        self.suggestion = suggestion
        self.exit_code = exit_code
        self.error_code = error_code

        # Build full error message with context
        full_message = f"[{error_code}] {message}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            full_message = f"{full_message} (context: {context_str})"
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
    
    Default error code: E100 (Parsing generic)
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        error_code: str = "E100",
    ) -> None:
        """Initialize with default parsing error code."""
        super().__init__(message, context, suggestion, exit_code=1, error_code=error_code)


class ValidationError(AnsibleDoctorError):
    """
    Raised when data validation fails.

    Examples:
        - Missing required metadata fields
        - Invalid variable types
        - Constraint violations in Pydantic models
    
    Default error code: E200 (Validation generic)
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        error_code: str = "E200",
    ) -> None:
        """Initialize with default validation error code."""
        super().__init__(message, context, suggestion, exit_code=1, error_code=error_code)


class ConfigError(AnsibleDoctorError):
    """
    Raised when configuration is invalid or missing.

    Examples:
        - Missing required configuration options
        - Invalid configuration file syntax
        - Conflicting configuration values
    
    Exit code: 3 (invalid usage)
    Default error code: E203 (Invalid field value)
    """
    
    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        error_code: str = "E203",
    ) -> None:
        """Initialize with exit code 3 for configuration errors."""
        super().__init__(message, context, suggestion, exit_code=3, error_code=error_code)


class TemplateError(AnsibleDoctorError):
    """
    Raised when template rendering fails.

    Examples:
        - Template syntax errors
        - Missing template variables
        - Template file not found
    
    Default error code: E300 (Generation generic)
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        error_code: str = "E300",
    ) -> None:
        """Initialize with default generation error code."""
        super().__init__(message, context, suggestion, exit_code=1, error_code=error_code)
