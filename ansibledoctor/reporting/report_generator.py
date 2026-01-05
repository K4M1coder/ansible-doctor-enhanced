"""Report generator implementation.

This module provides the ReportGenerator class that creates ExecutionReport
instances from context dictionaries and writes them to files in various formats.
Implements atomic file writes to prevent corruption.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Literal

from ansibledoctor.models.execution_report import ExecutionReport
from ansibledoctor.reporting import serializers


class ReportGenerator:
    """Generates and writes execution reports.
    
    Implements the ReportGenerator protocol to create ExecutionReport instances
    from context dictionaries and serialize them to various formats.
    Uses atomic file writes (temp + rename) to prevent corruption.
    
    Example:
        >>> generator = ReportGenerator()
        >>> context = {
        ...     "correlation_id": "abc-123",
        ...     "command": "ansible-doctor role",
        ...     "status": "completed",
        ...     ...
        ... }
        >>> report = generator.generate(context)
        >>> generator.write_report(report, Path("report.json"), "json")
    """
    
    def generate(self, context: dict) -> ExecutionReport:
        """Generate ExecutionReport from context dictionary.
        
        Extracts execution data from context and creates a validated
        ExecutionReport instance. Handles datetime parsing and model validation.
        
        Args:
            context: Dictionary containing execution data with keys:
                - correlation_id: str
                - command: str
                - status: Literal["completed", "completed_with_warnings", "failed", "interrupted"]
                - started_at: datetime or ISO string
                - completed_at: datetime or ISO string
                - duration_ms: int
                - metrics: dict or ExecutionMetrics
                - warnings: list[dict] or list[ExecutionWarning]
                - errors: list[dict] or list[ExecutionError]
                - output_files: list[str] or list[Path]
        
        Returns:
            Validated ExecutionReport instance
        
        Raises:
            ValidationError: If context data is invalid
        """
        # Parse datetime strings if needed
        started_at = context["started_at"]
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        
        completed_at = context["completed_at"]
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        
        # Create report using Pydantic model validation
        return ExecutionReport(
            correlation_id=context["correlation_id"],
            command=context["command"],
            status=context["status"],
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=context["duration_ms"],
            metrics=context["metrics"],
            warnings=context.get("warnings", []),
            errors=context.get("errors", []),
            output_files=context.get("output_files", [])
        )
    
    def write_report(
        self,
        report: ExecutionReport,
        path: Path,
        format: Literal["json", "text", "summary"] = "json"
    ) -> None:
        """Write report to file in specified format.
        
        Uses atomic file write (temp + rename) to prevent corruption from
        interrupted writes. Creates parent directories if needed.
        
        Args:
            report: ExecutionReport instance to write
            path: Target file path
            format: Output format ("json", "text", or "summary")
        
        Raises:
            ValueError: If format is not supported
            OSError: If file write fails
        
        Example:
            >>> generator = ReportGenerator()
            >>> report = generator.generate(context)
            >>> generator.write_report(report, Path("out.json"), "json")
        """
        # Serialize based on format
        if format == "json":
            content = serializers.serialize_to_json(report)
        elif format == "text":
            content = serializers.serialize_to_text(report)
        elif format == "summary":
            content = serializers.serialize_to_summary(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write: temp file + rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp"
        )
        
        try:
            # Write to temp file
            with open(temp_fd, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Atomic rename
            Path(temp_path).replace(path)
        except Exception:
            # Clean up temp file on error
            Path(temp_path).unlink(missing_ok=True)
            raise
