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
    """
    
    def __init__(self, max_errors: int = 1000):
        """Initialize error aggregator.
        
        Args:
            max_errors: Maximum number of errors to store (default: 1000)
        """
        self.max_errors = max_errors
        self.errors: List[ErrorEntry] = []
        self.warnings: List[ErrorEntry] = []
        self._seen_hashes: Set[str] = set()
        self._error_count = 0
        self._warning_count = 0
        self._max_errors_reached = False
        self._recovery_provider = RecoverySuggestionProvider()
    
    def add_error(
        self,
        code: str,
        message: str,
        file_path: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        recovery_suggestion: Optional[str] = None,
        doc_url: Optional[str] = None,
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
        """
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
            ErrorReport instance
        """
        return ErrorReport(
            correlation_id=correlation_id,
            errors=self.errors,
            warnings=self.warnings,
            error_count=self._error_count,
            warning_count=self._warning_count,
            max_errors_reached=self._max_errors_reached,
            partial_success=partial_success,
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
        self._max_errors_reached = False
    
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
