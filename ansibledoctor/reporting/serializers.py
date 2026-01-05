"""Serializers for execution reports.

This module provides serialization functions for ExecutionReport instances
to various output formats (JSON, text, summary). Supports ISO 8601 datetime
formatting and configurable output styles for different use cases.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ansibledoctor.models.execution_report import ExecutionReport


def serialize_to_json(report: ExecutionReport) -> str:
    """Serialize ExecutionReport to JSON string.

    Converts all datetime fields to ISO 8601 format with timezone (Z suffix).
    Converts Path objects to strings for JSON compatibility.

    Args:
        report: ExecutionReport instance to serialize

    Returns:
        JSON string representation with indentation

    Example:
        >>> report = ExecutionReport(...)
        >>> json_str = serialize_to_json(report)
        >>> data = json.loads(json_str)
        >>> data["started_at"]
        '2025-12-02T10:30:00Z'
    """
    # Convert to dict using Pydantic's model_dump
    data = report.model_dump(mode="json")

    # Custom encoder for datetime and Path
    def json_encoder(obj: Any) -> Any:
        if isinstance(obj, datetime):
            # ISO 8601 format with Z suffix for UTC
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(obj, Path):
            return str(obj)
        return obj

    # Convert datetime strings back to ISO 8601 if needed
    if isinstance(data.get("started_at"), str):
        # Already formatted by Pydantic, ensure it ends with Z
        started = data["started_at"]
        if not started.endswith("Z") and "+" not in started:
            data["started_at"] = started.replace("+00:00", "Z")

    if isinstance(data.get("completed_at"), str):
        completed = data["completed_at"]
        if not completed.endswith("Z") and "+" not in completed:
            data["completed_at"] = completed.replace("+00:00", "Z")

    return json.dumps(data, indent=2, default=json_encoder)


def serialize_to_text(report: ExecutionReport) -> str:
    """Serialize ExecutionReport to human-readable text format.

    Creates a formatted text summary suitable for console output or text files.
    Includes status, timing, metrics, and lists of warnings/errors.

    Args:
        report: ExecutionReport instance to serialize

    Returns:
        Multi-line text string with formatted report

    Example:
        >>> report = ExecutionReport(...)
        >>> print(serialize_to_text(report))
        Execution Report
        ================
        Status: completed
        ...
    """
    lines = [
        "Execution Report",
        "=" * 80,
        f"Correlation ID: {report.correlation_id}",
        f"Command: {report.command}",
        f"Status: {report.status}",
        f"Started: {report.started_at.isoformat()}",
        f"Completed: {report.completed_at.isoformat()}",
        f"Duration: {report.duration_ms} ms",
        "",
        "Metrics",
        "-" * 80,
        f"Files Processed: {report.metrics.files_processed}",
        f"Roles Documented: {report.metrics.roles_documented}",
        f"Collections Documented: {report.metrics.collections_documented}",
        f"Projects Documented: {report.metrics.projects_documented}",
        f"Warnings: {report.metrics.warnings_count}",
        f"Errors: {report.metrics.errors_count}",
    ]

    # Add phase timing if available
    if report.metrics.phase_timing:
        lines.append("")
        lines.append("Phase Timing")
        lines.append("-" * 80)
        for phase, duration in report.metrics.phase_timing.items():
            lines.append(f"{phase}: {duration} ms")

    # Add warnings if present
    if report.warnings:
        lines.append("")
        lines.append(f"Warnings ({len(report.warnings)})")
        lines.append("-" * 80)
        for warning in report.warnings:
            location = f"{warning.file}"
            if warning.line:
                location += f":{warning.line}"
            lines.append(f"  [{warning.warning_type}] {location}")
            lines.append(f"    {warning.message}")

    # Add errors if present
    if report.errors:
        lines.append("")
        lines.append(f"Errors ({len(report.errors)})")
        lines.append("-" * 80)
        for error in report.errors:
            location = f"{error.file}"
            if error.line:
                location += f":{error.line}"
            lines.append(f"  [{error.error_type}] {location}")
            lines.append(f"    {error.message}")
            if error.suggestion:
                lines.append(f"    Suggestion: {error.suggestion}")

    # Add output files if present
    if report.output_files:
        lines.append("")
        lines.append(f"Output Files ({len(report.output_files)})")
        lines.append("-" * 80)
        for output_file in report.output_files:
            lines.append(f"  - {output_file}")

    lines.append("")
    return "\n".join(lines)


def serialize_to_summary(report: ExecutionReport) -> str:
    """Serialize ExecutionReport to brief summary format with aggregated errors/warnings.

    Creates a concise summary suitable for console output at command completion.
    Groups errors and warnings by file for easy troubleshooting.

    Args:
        report: ExecutionReport instance to serialize

    Returns:
        Multi-line summary string with aggregated error/warning details

    Example:
        >>> report = ExecutionReport(...)
        >>> print(serialize_to_summary(report))
        ✓ Completed in 5.2s
        15 files processed, 3 roles documented

        Errors (2):
          tasks/main.yml (2):
            - Line 10: yaml_parsing_error - Invalid YAML syntax
            - Line 25: parsing_error - Missing required field
    """
    duration_s = report.duration_ms / 1000

    # Status symbol
    status_symbol = {
        "completed": "✓",
        "completed_with_warnings": "⚠",
        "failed": "✗",
        "interrupted": "⊗",
    }.get(report.status, "?")

    lines = [
        f"{status_symbol} {report.status.replace('_', ' ').title()} in {duration_s:.1f}s",
        f"{report.metrics.files_processed} files processed, "
        f"{report.metrics.roles_documented} roles documented",
    ]

    # Aggregate warnings by file
    if report.warnings:
        lines.append("")  # Empty line for separation
        lines.append(f"Warnings ({len(report.warnings)}):")

        # Group warnings by file
        from collections import defaultdict

        warnings_by_file = defaultdict(list)
        for warning in report.warnings:
            # Normalize path to use forward slashes for consistency
            file_path = str(warning.file).replace("\\", "/")
            warnings_by_file[file_path].append(warning)

        # Format grouped warnings
        for file_path, file_warnings in sorted(warnings_by_file.items()):
            lines.append(f"  {file_path} ({len(file_warnings)}):")
            for warning in file_warnings:
                line_info = f"Line {warning.line}: " if warning.line else ""
                lines.append(f"    - {line_info}{warning.warning_type} - {warning.message}")

    # Aggregate errors by file
    if report.errors:
        lines.append("")  # Empty line for separation
        lines.append(f"Errors ({len(report.errors)}):")

        # Group errors by file
        from collections import defaultdict

        errors_by_file = defaultdict(list)
        for error in report.errors:
            # Normalize path to use forward slashes for consistency
            file_path = str(error.file).replace("\\", "/")
            errors_by_file[file_path].append(error)

        # Format grouped errors
        for file_path, file_errors in sorted(errors_by_file.items()):
            lines.append(f"  {file_path} ({len(file_errors)}):")
            for error in file_errors:
                line_info = f"Line {error.line}: " if error.line else ""
                lines.append(f"    - {line_info}{error.error_type} - {error.message}")

    # Add summary counts if no detailed errors/warnings
    if not report.warnings and not report.errors:
        if report.metrics.warnings_count or report.metrics.errors_count:
            lines.append(
                f"{report.metrics.warnings_count} warnings, "
                f"{report.metrics.errors_count} errors"
            )

    return "\n".join(lines)
