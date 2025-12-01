"""Custom exceptions for documentation generator."""

from typing import Any


class GeneratorError(Exception):
    """Base exception for all generator errors."""

    pass


class TemplateError(GeneratorError):
    """Base exception for template-related errors."""

    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a template cannot be found in any search path."""

    def __init__(self, template_name: str, search_paths: list[str] | None = None):
        """Initialize with template name and optional search paths.

        Args:
            template_name: Name of the template that was not found
            search_paths: List of paths that were searched
        """
        self.template_name = template_name
        self.search_paths = search_paths or []

        message = f"Template not found: '{template_name}'"
        if search_paths:
            paths_str = "\n  - ".join(search_paths)
            message += f"\n\nSearched in:\n  - {paths_str}"

        super().__init__(message)


class TemplateValidationError(TemplateError):
    """Raised when a template has syntax errors or is invalid."""

    def __init__(self, template_name: str, error_details: str):
        """Initialize with template name and error details.

        Args:
            template_name: Name of the invalid template
            error_details: Detailed error message from validation
        """
        self.template_name = template_name
        self.error_details = error_details

        message = f"Template validation failed: '{template_name}'\n" f"Error: {error_details}"

        super().__init__(message)


class RenderError(GeneratorError):
    """Raised when rendering fails."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        """Initialize with error message and optional context.

        Args:
            message: Error description
            context: Optional context data that caused the error
        """
        self.context = context or {}

        error_msg = f"Rendering failed: {message}"
        if context:
            error_msg += f"\n\nContext keys: {', '.join(context.keys())}"

        super().__init__(error_msg)
