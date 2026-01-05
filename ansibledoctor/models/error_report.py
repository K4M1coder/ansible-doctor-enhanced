"""Error report data models for structured error collection and reporting."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorEntry(BaseModel):
    """Single error or warning with full context.
    
    Attributes:
        code: Error code (E101, W201, etc.)
        severity: Error severity level ("error" or "warning")
        category: Error category (parsing, validation, generation, io)
        message: Human-readable error message
        file_path: Path to file where error occurred (optional)
        line: Line number where error occurred (optional)
        column: Column number where error occurred (optional)
        recovery_suggestion: Suggested fix for the error (optional)
        doc_url: URL to error documentation (optional)
    """
    
    code: str = Field(pattern=r"^[EW]\d{3}$", description="Error code")
    severity: str = Field(description="Error severity: error or warning")
    category: str = Field(description="Error category")
    message: str = Field(description="Error message")
    file_path: Optional[str] = Field(default=None, description="File path where error occurred")
    line: Optional[int] = Field(default=None, ge=1, description="Line number")
    column: Optional[int] = Field(default=None, ge=1, description="Column number")
    recovery_suggestion: Optional[str] = Field(default=None, description="Recovery suggestion")
    doc_url: Optional[str] = Field(default=None, description="Documentation URL")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "code": "E101",
                "severity": "error",
                "category": "parsing",
                "message": "YAML syntax error: expected <block end>, but found ':'",
                "file_path": "roles/web/tasks/main.yml",
                "line": 15,
                "column": 3,
                "recovery_suggestion": "Check indentation and YAML syntax at line 15",
                "doc_url": "https://docs.ansible-doctor.com/errors/E101"
            }
        }


class ErrorReport(BaseModel):
    """Aggregated error report for a single execution run.
    
    Attributes:
        correlation_id: Links to ExecutionReport from Spec 009
        timestamp: When report was generated
        errors: All collected errors
        warnings: All collected warnings
        error_count: Total error count (including suppressed)
        warning_count: Total warning count
        suppressed_count: Number of errors suppressed via ignore codes (Phase 6 T059)
        max_errors_reached: True if error cap (1000) was reached
        partial_success: True if some files processed successfully despite errors
        total_files: Total number of files attempted to process
        successful_files: Number of files processed successfully
        failed_files: Number of files that failed processing
    """
    
    correlation_id: str = Field(description="Correlation ID linking to ExecutionReport")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    errors: List[ErrorEntry] = Field(default_factory=list, description="Collected errors")
    warnings: List[ErrorEntry] = Field(default_factory=list, description="Collected warnings")
    error_count: int = Field(default=0, ge=0, description="Total error count")
    warning_count: int = Field(default=0, ge=0, description="Total warning count")
    suppressed_count: int = Field(default=0, ge=0, description="Suppressed error count (Phase 6)")
    max_errors_reached: bool = Field(default=False, description="Error cap reached flag")
    partial_success: bool = Field(default=False, description="Partial success flag")
    total_files: int = Field(default=0, ge=0, description="Total files attempted")
    successful_files: int = Field(default=0, ge=0, description="Files processed successfully")
    failed_files: int = Field(default=0, ge=0, description="Files that failed processing")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "correlation_id": "01HXYZ123ABC456789",
                "timestamp": "2025-12-03T10:30:00Z",
                "errors": [
                    {
                        "code": "E101",
                        "severity": "error",
                        "category": "parsing",
                        "message": "YAML syntax error",
                        "file_path": "roles/web/tasks/main.yml",
                        "line": 15
                    }
                ],
                "warnings": [],
                "error_count": 1,
                "warning_count": 0,
                "max_errors_reached": False,
                "partial_success": False
            }
        }
    
    def to_text(self) -> str:
        """Format report as human-readable text for terminal.
        
        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 80)
        lines.append("ERROR REPORT")
        lines.append("=" * 80)
        lines.append(f"Correlation ID: {self.correlation_id}")
        lines.append(f"Timestamp: {self.timestamp.isoformat()}")
        lines.append(f"Errors: {self.error_count} | Warnings: {self.warning_count}")
        
        # Phase 6 T059: Show suppressed error count
        if self.suppressed_count > 0:
            lines.append(f"Suppressed: {self.suppressed_count} error(s) via ignore codes")
        
        # Show file processing summary if tracking files (T048)
        if self.total_files > 0:
            lines.append(f"Files Processed: {self.successful_files} of {self.total_files} successful")
        
        if self.max_errors_reached:
            lines.append("⚠️  Error limit reached (1000). Some errors may not be shown.")
        
        if self.partial_success:
            lines.append("✓ Partial success: Some files processed successfully")
        
        lines.append("")
        
        # Group errors by file
        if self.errors:
            lines.append("ERRORS:")
            lines.append("-" * 80)
            errors_by_file: Dict[str, List[ErrorEntry]] = {}
            for error in self.errors:
                file_key = error.file_path or "(unknown file)"
                if file_key not in errors_by_file:
                    errors_by_file[file_key] = []
                errors_by_file[file_key].append(error)
            
            for file_path, file_errors in errors_by_file.items():
                lines.append(f"\n{file_path}:")
                for error in file_errors:
                    location = ""
                    if error.line:
                        location = f" [line {error.line}"
                        if error.column:
                            location += f", col {error.column}"
                        location += "]"
                    
                    lines.append(f"  [{error.code}] {error.message}{location}")
                    if error.recovery_suggestion:
                        lines.append(f"      💡 {error.recovery_suggestion}")
                    if error.doc_url:
                        lines.append(f"      📖 {error.doc_url}")
        
        # Group warnings by file
        if self.warnings:
            lines.append("")
            lines.append("WARNINGS:")
            lines.append("-" * 80)
            warnings_by_file: Dict[str, List[ErrorEntry]] = {}
            for warning in self.warnings:
                file_key = warning.file_path or "(unknown file)"
                if file_key not in warnings_by_file:
                    warnings_by_file[file_key] = []
                warnings_by_file[file_key].append(warning)
            
            for file_path, file_warnings in warnings_by_file.items():
                lines.append(f"\n{file_path}:")
                for warning in file_warnings:
                    location = ""
                    if warning.line:
                        location = f" [line {warning.line}"
                        if warning.column:
                            location += f", col {warning.column}"
                        location += "]"
                    
                    lines.append(f"  [{warning.code}] {warning.message}{location}")
                    if warning.recovery_suggestion:
                        lines.append(f"      💡 {warning.recovery_suggestion}")
        
        lines.append("")
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Serialize report to JSON.
        
        Returns:
            JSON string representation
        """
        return self.model_dump_json(indent=2)
    
    def to_dict(self) -> dict:
        """Convert report to dictionary.
        
        Returns:
            Dictionary representation
        """
        return self.model_dump()
