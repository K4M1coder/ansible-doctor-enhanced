"""Tests for ExecutionReport model - User Story 1.

Following TDD (Red-Green-Refactor):
- RED: These tests MUST FAIL initially (models exist but no serialization yet)
- GREEN: Implementation will make them pass
- REFACTOR: Improve code quality while keeping tests green

Tests cover:
- T012: ExecutionReport serialization to JSON
- T013: ExecutionReport model validation (required fields, status enum)
- T014: Report with warnings (status="completed_with_warnings")
- T015: Report with errors (status="failed")
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from ansibledoctor.models.execution_report import (
    ExecutionError,
    ExecutionMetrics,
    ExecutionReport,
    ExecutionWarning,
)


class TestExecutionReportSerialization:
    """T012: Unit test for ExecutionReport serialization to JSON."""

    def test_report_serializes_to_json_with_all_fields(self):
        """Verify ExecutionReport can be serialized to JSON format."""
        # Arrange
        started = datetime(2025, 12, 2, 10, 30, 0, tzinfo=timezone.utc)
        completed = datetime(2025, 12, 2, 10, 30, 5, tzinfo=timezone.utc)
        
        metrics = ExecutionMetrics(
            files_processed=15,
            roles_documented=3,
            warnings_count=1,
            errors_count=0,
            phase_timing={"parsing_ms": 1200, "rendering_ms": 800}
        )
        
        warning = ExecutionWarning(
            file=Path("defaults/main.yml"),
            line=42,
            message="Variable missing @var annotation",
            warning_type="missing_annotation"
        )
        
        report = ExecutionReport(
            correlation_id="abc-123-def",
            command="generate",
            status="completed_with_warnings",
            started_at=started,
            completed_at=completed,
            duration_ms=5234,
            metrics=metrics,
            warnings=[warning],
            errors=[],
            output_files=[Path("docs/README.md"), Path("docs/index.html")]
        )
        
        # Act
        json_data = report.model_dump(mode='json')
        
        # Assert
        assert json_data["correlation_id"] == "abc-123-def"
        assert json_data["command"] == "generate"
        assert json_data["status"] == "completed_with_warnings"
        assert json_data["duration_ms"] == 5234
        assert json_data["metrics"]["files_processed"] == 15
        assert json_data["metrics"]["roles_documented"] == 3
        assert len(json_data["warnings"]) == 1
        assert json_data["warnings"][0]["message"] == "Variable missing @var annotation"
        assert len(json_data["output_files"]) == 2

    def test_report_serializes_datetime_to_iso8601(self):
        """Verify datetime fields are serialized to ISO 8601 format."""
        # Arrange
        started = datetime(2025, 12, 2, 10, 30, 0, tzinfo=timezone.utc)
        completed = datetime(2025, 12, 2, 10, 30, 5, tzinfo=timezone.utc)
        
        report = ExecutionReport(
            correlation_id="test-123",
            command="generate",
            status="completed",
            started_at=started,
            completed_at=completed,
            duration_ms=5000,
            metrics=ExecutionMetrics(),
            warnings=[],
            errors=[],
            output_files=[]
        )
        
        # Act
        json_data = report.model_dump(mode='json')
        
        # Assert - ISO 8601 format with timezone
        assert json_data["started_at"] == "2025-12-02T10:30:00Z"
        assert json_data["completed_at"] == "2025-12-02T10:30:05Z"


class TestExecutionReportValidation:
    """T013: Unit test for ExecutionReport model validation."""

    def test_report_requires_all_mandatory_fields(self):
        """Verify ExecutionReport validation fails when required fields are missing."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ExecutionReport(
                correlation_id="test-123",
                # Missing: command, status, started_at, completed_at, duration_ms, metrics
            )
        
        # Verify multiple fields are reported as missing
        errors = exc_info.value.errors()
        missing_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        assert "command" in missing_fields
        assert "status" in missing_fields
        assert "started_at" in missing_fields

    def test_report_status_must_be_valid_enum(self):
        """Verify status field only accepts valid enum values."""
        # Arrange
        started = datetime(2025, 12, 2, 10, 30, 0, tzinfo=timezone.utc)
        completed = datetime(2025, 12, 2, 10, 30, 5, tzinfo=timezone.utc)
        
        # Act & Assert - invalid status should fail
        with pytest.raises(ValidationError) as exc_info:
            ExecutionReport(
                correlation_id="test-123",
                command="generate",
                status="invalid_status",  # Not in Literal["completed", "completed_with_warnings", "failed", "interrupted"]
                started_at=started,
                completed_at=completed,
                duration_ms=5000,
                metrics=ExecutionMetrics()
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "status" for error in errors)

    def test_report_duration_must_be_non_negative(self):
        """Verify duration_ms cannot be negative."""
        # Arrange
        started = datetime(2025, 12, 2, 10, 30, 0, tzinfo=timezone.utc)
        completed = datetime(2025, 12, 2, 10, 30, 5, tzinfo=timezone.utc)
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ExecutionReport(
                correlation_id="test-123",
                command="generate",
                status="completed",
                started_at=started,
                completed_at=completed,
                duration_ms=-100,  # Invalid: negative duration
                metrics=ExecutionMetrics()
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "duration_ms" for error in errors)


class TestReportWithWarnings:
    """T014: Unit test for report with warnings (status='completed_with_warnings')."""

    def test_report_with_warnings_has_correct_status(self):
        """Verify report with warnings has status 'completed_with_warnings'."""
        # Arrange
        started = datetime(2025, 12, 2, 10, 30, 0, tzinfo=timezone.utc)
        completed = datetime(2025, 12, 2, 10, 30, 5, tzinfo=timezone.utc)
        
        warnings = [
            ExecutionWarning(
                file=Path("defaults/main.yml"),
                line=42,
                message="Variable missing @var annotation",
                warning_type="missing_annotation"
            ),
            ExecutionWarning(
                file=Path("tasks/main.yml"),
                line=10,
                message="Deprecated syntax",
                warning_type="deprecated_syntax"
            )
        ]
        
        metrics = ExecutionMetrics(warnings_count=2)
        
        # Act
        report = ExecutionReport(
            correlation_id="test-warnings",
            command="generate",
            status="completed_with_warnings",
            started_at=started,
            completed_at=completed,
            duration_ms=5000,
            metrics=metrics,
            warnings=warnings,
            errors=[],
            output_files=[]
        )
        
        # Assert
        assert report.status == "completed_with_warnings"
        assert len(report.warnings) == 2
        assert report.metrics.warnings_count == 2
        assert report.warnings[0].warning_type == "missing_annotation"
        assert report.warnings[1].warning_type == "deprecated_syntax"


class TestReportWithErrors:
    """T015: Unit test for report with errors (status='failed')."""

    def test_report_with_errors_has_failed_status(self):
        """Verify report with errors has status 'failed'."""
        # Arrange
        started = datetime(2025, 12, 2, 10, 30, 0, tzinfo=timezone.utc)
        completed = datetime(2025, 12, 2, 10, 30, 1, tzinfo=timezone.utc)
        
        errors = [
            ExecutionError(
                file=Path("tasks/main.yml"),
                line=15,
                error_type="yaml_parsing_error",
                message="Invalid YAML syntax: expected <block end>",
                suggestion="Check for proper indentation and closing brackets"
            )
        ]
        
        metrics = ExecutionMetrics(errors_count=1)
        
        # Act
        report = ExecutionReport(
            correlation_id="test-errors",
            command="generate",
            status="failed",
            started_at=started,
            completed_at=completed,
            duration_ms=1000,
            metrics=metrics,
            warnings=[],
            errors=errors,
            output_files=[]
        )
        
        # Assert
        assert report.status == "failed"
        assert len(report.errors) == 1
        assert report.metrics.errors_count == 1
        assert report.errors[0].error_type == "yaml_parsing_error"
        assert report.errors[0].suggestion is not None
        assert "indentation" in report.errors[0].suggestion

    def test_report_error_includes_suggestion(self):
        """Verify ExecutionError includes actionable suggestion."""
        # Arrange
        error = ExecutionError(
            file=Path("meta/main.yml"),
            line=5,
            error_type="validation_error",
            message="Missing required field: galaxy_info.author",
            suggestion="Add 'author' field to galaxy_info section in meta/main.yml"
        )
        
        # Assert
        assert error.suggestion is not None
        assert "Add 'author' field" in error.suggestion
        assert error.file == Path("meta/main.yml")
        assert error.line == 5
