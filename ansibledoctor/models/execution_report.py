"""Execution report models for ansible-doctor.

This module contains Pydantic models for execution reporting:
- ExecutionMetrics: Performance metrics (timing, counts)
- ExecutionWarning: Warning information with file location
- ExecutionError: Error information with suggestions
- ExecutionReport: Primary aggregate model combining all report data

These models provide structured, validated data for execution reports
that can be serialized to JSON or formatted as human-readable text.
"""

from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExecutionMetrics(BaseModel):
    """Performance metrics for an execution.

    Tracks file counts, entity counts (roles/collections/projects),
    warning/error counts, and phase timing measurements.
    """

    files_processed: int = Field(default=0, ge=0, description="Total files processed")
    roles_documented: int = Field(default=0, ge=0, description="Roles documented")
    collections_documented: int = Field(default=0, ge=0, description="Collections documented")
    projects_documented: int = Field(default=0, ge=0, description="Projects documented")
    warnings_count: int = Field(default=0, ge=0, description="Total warnings")
    errors_count: int = Field(default=0, ge=0, description="Total errors")
    phase_timing: dict[str, int] = Field(
        default_factory=dict,
        description="Phase timing in milliseconds (e.g., parsing_ms, rendering_ms)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "files_processed": 15,
                "roles_documented": 3,
                "collections_documented": 0,
                "projects_documented": 0,
                "warnings_count": 2,
                "errors_count": 0,
                "phase_timing": {"parsing_ms": 1200, "rendering_ms": 800, "writing_ms": 300},
            }
        }
    )


class ExecutionWarning(BaseModel):
    """Warning information with file location.

    Captures warnings that occur during execution with optional
    line number for precise location identification.
    """

    file: Path = Field(description="File path where warning occurred")
    line: Optional[int] = Field(default=None, ge=1, description="Line number (1-indexed)")
    message: str = Field(description="Warning message")
    warning_type: str = Field(description="Warning type (e.g., missing_annotation)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file": "defaults/main.yml",
                "line": 42,
                "message": "Variable missing @var annotation",
                "warning_type": "missing_annotation",
            }
        }
    )


class ExecutionError(BaseModel):
    """Error information with suggestions.

    Captures errors that occur during execution with optional
    recovery suggestions and stack traces for debugging.
    """

    file: Path = Field(description="File path where error occurred")
    line: Optional[int] = Field(default=None, ge=1, description="Line number (1-indexed)")
    error_type: str = Field(description="Error type (e.g., parsing_error, validation_error)")
    message: str = Field(description="Error message")
    suggestion: Optional[str] = Field(default=None, description="Recovery suggestion")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace for debugging")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file": "tasks/main.yml",
                "line": 15,
                "error_type": "yaml_parsing_error",
                "message": "Invalid YAML syntax: expected <block end>",
                "suggestion": "Check for proper indentation and closing brackets",
                "stack_trace": None,
            }
        }
    )


class ExecutionReport(BaseModel):
    """Primary aggregate model for execution reports.

    Combines all execution data including status, timing, metrics,
    warnings, errors, and output files. Can be serialized to JSON
    or formatted as human-readable text for CI/CD integration.
    """

    correlation_id: str = Field(description="Unique correlation ID for tracing")
    command: str = Field(description="Command executed (generate, parse, watch)")
    status: Literal["completed", "completed_with_warnings", "failed", "interrupted"] = Field(
        description="Execution status"
    )
    started_at: datetime = Field(description="Execution start time (ISO 8601)")
    completed_at: datetime = Field(description="Execution completion time (ISO 8601)")
    duration_ms: int = Field(ge=0, description="Total execution duration in milliseconds")
    metrics: ExecutionMetrics = Field(description="Performance metrics")
    warnings: list[ExecutionWarning] = Field(default_factory=list, description="List of warnings")
    errors: list[ExecutionError] = Field(default_factory=list, description="List of errors")
    output_files: list[Path] = Field(
        default_factory=list, description="List of generated output files"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "correlation_id": "abc-123-def",
                "command": "generate",
                "status": "completed_with_warnings",
                "started_at": "2025-12-02T10:30:00Z",
                "completed_at": "2025-12-02T10:30:05Z",
                "duration_ms": 5234,
                "metrics": {
                    "files_processed": 15,
                    "roles_documented": 3,
                    "warnings_count": 2,
                    "errors_count": 0,
                },
                "warnings": [
                    {
                        "file": "defaults/main.yml",
                        "line": 42,
                        "message": "Variable missing @var annotation",
                        "warning_type": "missing_annotation",
                    }
                ],
                "errors": [],
                "output_files": ["docs/README.md", "docs/index.html"],
            }
        }
    )
