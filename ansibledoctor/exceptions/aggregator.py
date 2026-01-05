"""Error aggregation and collection.

This module provides ErrorAggregator for collecting and deduplicating errors
during multi-file processing.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set
import hashlib

from ansibledoctor.exceptions.codes import ErrorCode, get_category, get_severity
from ansibledoctor.exceptions.recovery import RecoverySuggestionProvider
from ansibledoctor.models.error_report import ErrorEntry, ErrorReport


class ErrorAggregator:
    """Aggregates errors and warnings during processing with deduplication.
    
    Features:
    - Deduplicates identical errors using content hashing
    - Enforces memory bounds (max 1000 errors)
    - Groups errors by file for organized reporting
    - Tracks warnings separately from errors
    - Tracks file processing for partial success reporting (Phase 5)
    - Error code suppression with ignore_codes (Phase 6, T058)
    """
    
    def __init__(self, max_errors: int = 1000, ignore_codes: Optional[List[str]] = None):
        """Initialize error aggregator.
        
        Args:
            max_errors: Maximum number of errors to store (default: 1000)
            ignore_codes: List of error codes to suppress (e.g., ["E101", "W103"])
        """
        self.max_errors = max_errors
        self.errors: List[ErrorEntry] = []
        self.warnings: List[ErrorEntry] = []
        self._seen_hashes: Set[str] = set()
        self._error_count = 0
        self._warning_count = 0
        self._max_errors_reached = False
        self._recovery_provider = RecoverySuggestionProvider()
        
        # Phase 6: Error suppression (T058)
        self._ignore_codes = set(code.upper() for code in (ignore_codes or []))
        self.suppressed_count = 0
        
        # Phase 5: File tracking for partial success reporting (T046)
        self._total_files = 0
        self._successful_files = 0
        self._failed_files = 0
        self._processed_files: Set[str] = set()  # Track which files have been processed
    
    def add_error(
        self,
        code: str,
        message: str,
        file_path: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        recovery_suggestion: Optional[str] = None,
        doc_url: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> None:
        """Add an error to the aggregator.
        
        Args:
            code: Error code (e.g., "E101")
            message: Error message
            file_path: Path to file where error occurred
            line: Line number where error occurred
            column: Column number where error occurred
            recovery_suggestion: Suggested fix (auto-fetched if None)
            doc_url: Documentation URL (auto-fetched if None)
            severity: Override severity ("error" or "warning"), auto-detected if None
        """
        # Phase 6 T058: Check if error code should be suppressed
        if code.upper() in self._ignore_codes:
            self.suppressed_count += 1
            return  # Suppress this error
        
        if severity is None:
            severity = get_severity(code)
        category = get_category(code).value
        
        # Auto-fetch recovery suggestion if not provided
        if recovery_suggestion is None:
            recovery_suggestion = self._recovery_provider.get_suggestion(code)
        
        # Auto-fetch documentation URL if not provided
        if doc_url is None:
            doc_url = self._recovery_provider.get_doc_url(code)
        
        entry = ErrorEntry(
            code=code,
            severity=severity,
            category=category,
            message=message,
            file_path=file_path,
            line=line,
            column=column,
            recovery_suggestion=recovery_suggestion,
            doc_url=doc_url,
        )
        
        # Deduplicate using hash
        entry_hash = self._hash_entry(entry)
        if entry_hash in self._seen_hashes:
            return  # Duplicate, skip
        
        self._seen_hashes.add(entry_hash)
        
        if severity == "warning":
            self._warning_count += 1
            if len(self.warnings) < self.max_errors:
                self.warnings.append(entry)
        else:
            self._error_count += 1
            if len(self.errors) < self.max_errors:
                self.errors.append(entry)
            elif not self._max_errors_reached:
                self._max_errors_reached = True
    
    def add_warning(
        self,
        code: str,
        message: str,
        file_path: str = None,
        line: int = None,
        column: int = None,
        recovery_suggestion: str = None,
    ) -> None:
        """Add a warning to the aggregator.
        
        This is a convenience method that ensures severity is "warning".
        
        Args:
            code: Warning code (e.g., "W101")
            message: Warning message
            file_path: Path to file where warning occurred
            line: Line number where warning occurred
            column: Column number where warning occurred
            recovery_suggestion: Suggested fix for the warning
        """
        # Force code to start with 'W' if it doesn't
        if not code.startswith('W'):
            code = f"W{code[1:]}" if code.startswith('E') else f"W{code}"
        
        self.add_error(code, message, file_path, line, column, recovery_suggestion)
    
    def get_report(self, correlation_id: str, partial_success: bool = False) -> ErrorReport:
        """Generate an error report from collected errors.
        
        Args:
            correlation_id: Correlation ID linking to ExecutionReport
            partial_success: True if some files processed successfully
        
        Returns:
            ErrorReport instance with file tracking (T047) and suppressed count (T059)
        """
        return ErrorReport(
            correlation_id=correlation_id,
            errors=self.errors,
            warnings=self.warnings,
            error_count=self._error_count,
            warning_count=self._warning_count,
            suppressed_count=self.suppressed_count,  # Phase 6 T059
            max_errors_reached=self._max_errors_reached,
            partial_success=partial_success,
            total_files=self._total_files,
            successful_files=self._successful_files,
            failed_files=self._failed_files,
        )
    
    def has_errors(self) -> bool:
        """Check if any errors were collected.
        
        Returns:
            True if errors exist, False otherwise
        """
        return self._error_count > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings were collected.
        
        Returns:
            True if warnings exist, False otherwise
        """
        return self._warning_count > 0
    
    def get_errors_by_file(self) -> Dict[str, List[ErrorEntry]]:
        """Group errors by file path.
        
        Returns:
            Dictionary mapping file paths to error lists
        """
        grouped: Dict[str, List[ErrorEntry]] = defaultdict(list)
        for error in self.errors:
            key = error.file_path or "(unknown file)"
            grouped[key].append(error)
        return dict(grouped)
    
    def get_warnings_by_file(self) -> Dict[str, List[ErrorEntry]]:
        """Group warnings by file path.
        
        Returns:
            Dictionary mapping file paths to warning lists
        """
        grouped: Dict[str, List[ErrorEntry]] = defaultdict(list)
        for warning in self.warnings:
            key = warning.file_path or "(unknown file)"
            grouped[key].append(warning)
        return dict(grouped)
    
    def clear(self) -> None:
        """Clear all collected errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
        self._seen_hashes.clear()
        self._error_count = 0
        self._warning_count = 0
        self.suppressed_count = 0  # Phase 6 T059
        self._max_errors_reached = False
        self._total_files = 0
        self._successful_files = 0
        self._failed_files = 0
        self._processed_files.clear()
    
    def mark_file_start(self, file_path: str) -> None:
        """Mark the start of processing a file (Phase 5 - T046).
        
        Args:
            file_path: Path to file being processed
        """
        if file_path not in self._processed_files:
            self._total_files += 1
            self._processed_files.add(file_path)
    
    def mark_file_success(self, file_path: str) -> None:
        """Mark a file as successfully processed (Phase 5 - T046).
        
        Args:
            file_path: Path to file that succeeded
        """
        self.mark_file_start(file_path)  # Ensure file is counted
        self._successful_files += 1
    
    def mark_file_failure(self, file_path: str) -> None:
        """Mark a file as failed during processing (Phase 5 - T046).
        
        Args:
            file_path: Path to file that failed
        """
        self.mark_file_start(file_path)  # Ensure file is counted
        self._failed_files += 1
    
    @staticmethod
    def _hash_entry(entry: ErrorEntry) -> str:
        """Generate hash for error entry deduplication.
        
        Args:
            entry: ErrorEntry to hash
        
        Returns:
            SHA256 hash of entry content
        """
        content = f"{entry.code}:{entry.message}:{entry.file_path}:{entry.line}:{entry.column}"
        return hashlib.sha256(content.encode()).hexdigest()
