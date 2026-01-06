"""Unit tests for schema models.

Tests for ValidationError, ValidationResult, and SchemaModel classes.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.schemas import SchemaModel, Severity, ValidationError, ValidationResult


class TestValidationError:
    """Tests for ValidationError model."""

    def test_formatted_message_with_location(self):
        """Test formatted_message includes line and column numbers."""
        error = ValidationError(
            path="config.output_format",
            message="Invalid enum value",
            validator="enum",
            severity=Severity.ERROR,
            expected="markdown, html, rst",
            actual="pdf",
            line_number=5,
            column_number=18,
        )

        message = error.formatted_message
        assert "Line 5" in message
        assert "Col 18" in message
        assert "config.output_format" in message
        assert "Invalid enum value" in message
        assert "Expected: markdown, html, rst" in message
        assert "Actual: pdf" in message

    def test_formatted_message_with_suggestion(self):
        """Test formatted_message includes suggestion."""
        error = ValidationError(
            path="config.verbose",
            message="Type mismatch",
            validator="type",
            severity=Severity.ERROR,
            expected="boolean",
            actual="string",
            suggestion="Use 'true' or 'false' without quotes",
        )

        message = error.formatted_message
        assert "💡 Suggestion: Use 'true' or 'false' without quotes" in message

    def test_formatted_message_minimal(self):
        """Test formatted_message with minimal fields."""
        error = ValidationError(
            path="config.unknown_field",
            message="Unknown property",
            validator="additionalProperties",
            severity=Severity.WARNING,
        )

        message = error.formatted_message
        assert "config.unknown_field" in message
        assert "Unknown property" in message

    def test_severity_property(self):
        """Test severity enum values."""
        error_err = ValidationError(
            path="test", message="test", validator="test", severity=Severity.ERROR
        )
        error_warn = ValidationError(
            path="test", message="test", validator="test", severity=Severity.WARNING
        )
        error_info = ValidationError(
            path="test", message="test", validator="test", severity=Severity.INFO
        )

        assert error_err.severity == Severity.ERROR
        assert error_warn.severity == Severity.WARNING
        assert error_info.severity == Severity.INFO


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_error_count(self):
        """Test error_count property."""
        result = ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(path="a", message="error1", validator="test"),
                ValidationError(path="b", message="error2", validator="test"),
            ],
        )
        assert result.error_count == 2

    def test_warning_count(self):
        """Test warning_count property."""
        result = ValidationResult(
            is_valid=True,
            warnings=[
                ValidationError(
                    path="a", message="warn1", validator="test", severity=Severity.WARNING
                ),
                ValidationError(
                    path="b", message="warn2", validator="test", severity=Severity.WARNING
                ),
                ValidationError(
                    path="c", message="warn3", validator="test", severity=Severity.WARNING
                ),
            ],
        )
        assert result.warning_count == 3

    def test_format_report_valid(self):
        """Test format_report for valid result."""
        result = ValidationResult(is_valid=True, file_path=Path("config.yml"))

        report = result.format_report()
        assert "✅ Validation passed!" in report
        assert "config.yml" in report

    def test_format_report_invalid(self):
        """Test format_report for invalid result with errors."""
        result = ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(path="config.format", message="Invalid value", validator="enum"),
            ],
            warnings=[
                ValidationError(
                    path="config.extra",
                    message="Unknown field",
                    validator="additionalProperties",
                    severity=Severity.WARNING,
                ),
            ],
            file_path=Path("config.yml"),
        )

        report = result.format_report()
        assert "❌ Validation failed with 1 error(s)" in report
        assert "⚠️  1 warning(s)" in report
        assert "ERRORS:" in report
        assert "WARNINGS:" in report
        assert "config.format" in report
        assert "config.extra" in report

    def test_format_report_verbose(self):
        """Test format_report in verbose mode."""
        result = ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    path="config.format",
                    message="Invalid value",
                    validator="enum",
                    expected="markdown",
                    actual="pdf",
                    suggestion="Use one of: markdown, html, rst",
                ),
            ],
        )

        report = result.format_report(verbose=True)
        assert "Expected: markdown" in report
        assert "Actual: pdf" in report
        assert "💡 Suggestion" in report

    def test_raise_if_invalid_with_errors(self):
        """Test raise_if_invalid raises ValueError for errors."""
        result = ValidationResult(
            is_valid=False,
            errors=[ValidationError(path="test", message="error", validator="test")],
        )

        with pytest.raises(ValueError, match="Validation failed with 1 error"):
            result.raise_if_invalid()

    def test_raise_if_invalid_with_warnings_strict(self):
        """Test raise_if_invalid raises ValueError for warnings in strict mode."""
        result = ValidationResult(
            is_valid=True,
            warnings=[
                ValidationError(
                    path="test", message="warning", validator="test", severity=Severity.WARNING
                )
            ],
        )

        # Should not raise in non-strict mode
        result.raise_if_invalid(strict=False)

        # Should raise in strict mode
        with pytest.raises(ValueError, match="Validation failed in strict mode with 1 warning"):
            result.raise_if_invalid(strict=True)

    def test_raise_if_invalid_valid(self):
        """Test raise_if_invalid does not raise for valid result."""
        result = ValidationResult(is_valid=True)
        result.raise_if_invalid()  # Should not raise


class TestSchemaModel:
    """Tests for SchemaModel base class."""

    def test_schema_version_field(self):
        """Test schema_version field."""
        schema = SchemaModel(schema_version="1.0.0", id="https://example.com/schema")
        assert schema.schema_version == "1.0.0"

    def test_id_field(self):
        """Test id field."""
        schema = SchemaModel(schema_version="1.0.0", id="https://example.com/schema")
        assert schema.id == "https://example.com/schema"

    def test_to_json_schema(self):
        """Test to_json_schema conversion."""
        schema = SchemaModel(
            schema_version="1.0.0",
            id="https://example.com/config",
            schema_uri="https://json-schema.org/draft/2020-12/schema",
        )

        json_schema = schema.to_json_schema()
        assert json_schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert json_schema["$id"] == "https://example.com/config"
        assert json_schema["version"] == "1.0.0"

    def test_to_json_schema_default_uri(self):
        """Test to_json_schema with default $schema URI."""
        schema = SchemaModel(schema_version="1.0.0", id="https://example.com/config")

        json_schema = schema.to_json_schema()
        assert json_schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
