"""Unit tests for error and warning aggregation in reporting.

Tests for User Story 4: Aggregated Error Summary
TDD Phase: RED - Tests written first, expect failures
Spec: 009-execution-reports-and-logs.md Phase 6 (T058-T060)
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone

from ansibledoctor.models.execution_report import (
    ExecutionReport,
    ExecutionMetrics,
    ExecutionWarning,
    ExecutionError,
)
from ansibledoctor.reporting.serializers import serialize_to_summary


class TestErrorAggregationByFile:
    """T058: Unit test for error aggregation by file."""

    def test_errors_grouped_by_file(self):
        """Errors from same file should be grouped together in aggregation."""
        # Arrange
        error1 = ExecutionError(
            file=Path("tasks/main.yml"),
            line=10,
            error_type="yaml_error",
            message="Invalid YAML syntax",
        )
        error2 = ExecutionError(
            file=Path("tasks/main.yml"),
            line=25,
            error_type="parsing_error",
            message="Missing required field",
        )
        error3 = ExecutionError(
            file=Path("defaults/main.yml"),
            line=5,
            error_type="validation_error",
            message="Invalid variable name",
        )

        report = ExecutionReport(
            correlation_id="test-123",
            command="generate",
            status="failed",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=1000,
            metrics=ExecutionMetrics(
                files_processed=3,
                roles_documented=1,
                errors_count=3,
            ),
            errors=[error1, error2, error3],
        )

        # Act
        summary = serialize_to_summary(report)

        # Assert - Should show grouped errors by file
        assert "tasks/main.yml" in summary
        assert "defaults/main.yml" in summary
        assert "2 errors" in summary or "tasks/main.yml (2)" in summary  # 2 errors in tasks/main.yml
        assert "3 errors" in summary or "Total: 3" in summary  # Total count

    def test_multiple_errors_same_file_shows_count(self):
        """Multiple errors in same file should show count in summary."""
        # Arrange
        errors = [
            ExecutionError(
                file=Path("vars/main.yml"),
                line=i,
                error_type="validation_error",
                message=f"Error {i}",
            )
            for i in range(1, 6)  # 5 errors
        ]

        report = ExecutionReport(
            correlation_id="test-456",
            command="parse",
            status="failed",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=500,
            metrics=ExecutionMetrics(
                files_processed=1,
                roles_documented=0,
                errors_count=5,
            ),
            errors=errors,
        )

        # Act
        summary = serialize_to_summary(report)

        # Assert
        assert "vars/main.yml" in summary
        assert "5" in summary  # Should show count of 5
        

class TestWarningAggregationByFile:
    """T059: Unit test for warning aggregation by file."""

    def test_warnings_grouped_by_file(self):
        """Warnings from same file should be grouped together."""
        # Arrange
        warning1 = ExecutionWarning(
            file=Path("tasks/install.yml"),
            line=12,
            message="Missing @todo annotation",
            warning_type="missing_annotation",
        )
        warning2 = ExecutionWarning(
            file=Path("tasks/install.yml"),
            line=45,
            message="Deprecated syntax usage",
            warning_type="deprecated_syntax",
        )
        warning3 = ExecutionWarning(
            file=Path("handlers/main.yml"),
            line=8,
            message="Missing handler description",
            warning_type="missing_description",
        )

        report = ExecutionReport(
            correlation_id="test-789",
            command="generate",
            status="completed_with_warnings",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=2000,
            metrics=ExecutionMetrics(
                files_processed=2,
                roles_documented=1,
                warnings_count=3,
            ),
            warnings=[warning1, warning2, warning3],
        )

        # Act
        summary = serialize_to_summary(report)

        # Assert - Should show grouped warnings by file
        assert "tasks/install.yml" in summary
        assert "handlers/main.yml" in summary
        assert "2 warnings" in summary or "tasks/install.yml (2)" in summary
        assert "3 warnings" in summary or "Total: 3" in summary

    def test_mixed_warnings_and_errors_both_displayed(self):
        """Summary should show both warnings and errors when present."""
        # Arrange
        warning = ExecutionWarning(
            file=Path("meta/main.yml"),
            line=3,
            message="Missing galaxy_info",
            warning_type="missing_metadata",
        )
        error = ExecutionError(
            file=Path("tasks/main.yml"),
            line=20,
            error_type="yaml_error",
            message="Invalid YAML",
        )

        report = ExecutionReport(
            correlation_id="test-mixed",
            command="generate",
            status="failed",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=1500,
            metrics=ExecutionMetrics(
                files_processed=2,
                roles_documented=1,
                warnings_count=1,
                errors_count=1,
            ),
            warnings=[warning],
            errors=[error],
        )

        # Act
        summary = serialize_to_summary(report)

        # Assert
        assert "1 warning" in summary or "warnings: 1" in summary
        assert "1 error" in summary or "errors: 1" in summary
        assert "meta/main.yml" in summary
        assert "tasks/main.yml" in summary


class TestSummaryTextFormatting:
    """T060: Unit test for summary text formatting."""

    def test_summary_includes_file_paths(self):
        """Summary should include file paths where errors occurred."""
        # Arrange
        error = ExecutionError(
            file=Path("roles/webserver/tasks/main.yml"),
            line=42,
            error_type="parsing_error",
            message="Failed to parse task",
        )

        report = ExecutionReport(
            correlation_id="test-paths",
            command="generate",
            status="failed",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=800,
            metrics=ExecutionMetrics(
                files_processed=1,
                roles_documented=1,
                errors_count=1,
            ),
            errors=[error],
        )

        # Act
        summary = serialize_to_summary(report)

        # Assert - File path should be present
        assert "roles/webserver/tasks/main.yml" in summary or "tasks/main.yml" in summary

    def test_summary_includes_error_types(self):
        """Summary should include error types for categorization."""
        # Arrange
        errors = [
            ExecutionError(
                file=Path("tasks/main.yml"),
                line=10,
                error_type="yaml_parsing_error",
                message="Invalid YAML",
            ),
            ExecutionError(
                file=Path("vars/main.yml"),
                line=5,
                error_type="validation_error",
                message="Invalid variable",
            ),
        ]

        report = ExecutionReport(
            correlation_id="test-types",
            command="parse",
            status="failed",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=600,
            metrics=ExecutionMetrics(
                files_processed=2,
                roles_documented=0,
                errors_count=2,
            ),
            errors=errors,
        )

        # Act
        summary = serialize_to_summary(report)

        # Assert - Error types should be identifiable
        assert "yaml_parsing_error" in summary or "yaml" in summary.lower()
        assert "validation_error" in summary or "validation" in summary.lower()

    def test_summary_table_format_for_readability(self):
        """Summary should use table format for multiple errors/warnings."""
        # Arrange
        errors = [
            ExecutionError(
                file=Path(f"file{i}.yml"),
                line=i,
                error_type="error_type",
                message=f"Error {i}",
            )
            for i in range(1, 4)
        ]

        report = ExecutionReport(
            correlation_id="test-table",
            command="generate",
            status="failed",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_ms=1200,
            metrics=ExecutionMetrics(
                files_processed=3,
                roles_documented=1,
                errors_count=3,
            ),
            errors=errors,
        )

        # Act
        summary = serialize_to_summary(report)

        # Assert - Should use structured format (table, list, or aligned columns)
        # Check for multiple file entries (implies table/list structure)
        assert "file1.yml" in summary
        assert "file2.yml" in summary
        assert "file3.yml" in summary
        # Check for alignment characters (table borders or list markers)
        assert ("-" in summary or "*" in summary or "│" in summary or "\n  " in summary)
