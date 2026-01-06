"""Schema models for validation and documentation.

This module defines core data structures for schema validation, error reporting,
and validation results.

Classes:
    ValidationError: Represents a single validation error with context
    ValidationResult: Aggregates validation errors and provides reporting
    SchemaModel: Base class for schema definitions
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class Severity(str, Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a validation error with detailed context.

    Attributes:
        path: JSONPath to the invalid field (e.g., "config.output.format")
        message: Human-readable error message
        validator: The validator that failed (e.g., "enum", "type", "required")
        severity: ERROR, WARNING, or INFO
        expected: Expected value or type
        actual: Actual value found
        suggestion: Actionable suggestion for fixing the error
        line_number: Line number in source file (if available)
        column_number: Column number in source file (if available)
    """

    path: str
    message: str
    validator: str
    severity: Severity = Severity.ERROR
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    suggestion: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None

    @property
    def formatted_message(self) -> str:
        """Format error message with location and suggestion."""
        parts = []

        # Location
        if self.line_number:
            location = f"Line {self.line_number}"
            if self.column_number:
                location += f", Col {self.column_number}"
            parts.append(location)

        # Path
        if self.path:
            parts.append(f"Path: {self.path}")

        # Message
        parts.append(self.message)

        # Expected vs Actual
        if self.expected is not None:
            parts.append(f"Expected: {self.expected}")
        if self.actual is not None:
            parts.append(f"Actual: {self.actual}")

        # Suggestion
        if self.suggestion:
            parts.append(f"💡 Suggestion: {self.suggestion}")

        return " | ".join(parts)


@dataclass
class ValidationResult:
    """Aggregates validation results with errors and warnings.

    Attributes:
        is_valid: True if validation passed with no errors
        errors: List of validation errors
        warnings: List of validation warnings
        file_path: Path to the validated file (if applicable)
    """

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    file_path: Optional[Path] = None

    @property
    def error_count(self) -> int:
        """Count of validation errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Count of validation warnings."""
        return len(self.warnings)

    def format_report(self, verbose: bool = False) -> str:
        """Format a human-readable validation report.

        Args:
            verbose: Include full details and suggestions

        Returns:
            Formatted report string
        """
        lines = []

        if self.file_path:
            lines.append(f"Validation Report: {self.file_path}")
        else:
            lines.append("Validation Report")

        lines.append("=" * 80)

        if self.is_valid:
            lines.append("✅ Validation passed!")
            if self.warnings:
                lines.append(f"⚠️  {self.warning_count} warning(s)")
        else:
            lines.append(f"❌ Validation failed with {self.error_count} error(s)")
            if self.warnings:
                lines.append(f"⚠️  {self.warning_count} warning(s)")

        lines.append("")

        # Errors
        if self.errors:
            lines.append("ERRORS:")
            lines.append("-" * 80)
            for err in self.errors:
                if verbose:
                    lines.append(err.formatted_message)
                else:
                    lines.append(f"{err.severity.value.upper()}: {err.path} - {err.message}")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("WARNINGS:")
            lines.append("-" * 80)
            for warn in self.warnings:
                if verbose:
                    lines.append(warn.formatted_message)
                else:
                    lines.append(f"{warn.severity.value.upper()}: {warn.path} - {warn.message}")
            lines.append("")

        return "\n".join(lines)

    def raise_if_invalid(self, strict: bool = False) -> None:
        """Raise ValueError if validation failed.

        Args:
            strict: If True, treat warnings as errors

        Raises:
            ValueError: If validation failed (or warnings exist in strict mode)
        """
        if not self.is_valid:
            raise ValueError(
                f"Validation failed with {self.error_count} error(s):\n{self.format_report()}"
            )

        if strict and self.warnings:
            raise ValueError(
                f"Validation failed in strict mode with {self.warning_count} warning(s):\n{self.format_report()}"
            )


@dataclass
class SchemaModel:
    """Base class for schema definitions.

    Attributes:
        schema_version: Schema version identifier (e.g., "2020-12", "1.0.0")
        id: Unique schema identifier URI
        schema_uri: URI to the schema specification
    """

    schema_version: str
    id: str
    schema_uri: Optional[str] = None

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema representation.

        Returns:
            JSON Schema dictionary
        """
        schema = {
            "$schema": self.schema_uri or "https://json-schema.org/draft/2020-12/schema",
            "$id": self.id,
            "version": self.schema_version,
        }
        return schema
