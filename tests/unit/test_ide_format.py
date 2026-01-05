"""Unit tests for IDE-friendly error format.

Phase 7 - User Story 5: IDE-Friendly Error Output
Test: T071
"""

import pytest

from ansibledoctor.models.error_report import ErrorEntry, ErrorReport


class TestIDEFormat:
    """Test file:line:column: error[CODE]: message format (T071)."""
    
    def test_ide_format_with_full_location(self):
        """Test IDE format with file, line, and column."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="YAML syntax error",
                    file_path="roles/web/tasks/main.yml",
                    line=15,
                    column=3,
                )
            ],
            error_count=1,
        )
        
        output = report.to_ide_format()
        
        # Should match format: file:line:column: error[CODE]: message
        assert "roles/web/tasks/main.yml:15:3: error[E101]: YAML syntax error" in output
    
    def test_ide_format_with_file_and_line_only(self):
        """Test IDE format without column number."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(
                    code="E200",
                    severity="error",
                    category="validation",
                    message="Invalid role structure",
                    file_path="roles/web/meta/main.yml",
                    line=10,
                )
            ],
            error_count=1,
        )
        
        output = report.to_ide_format()
        
        assert "roles/web/meta/main.yml:10: error[E200]: Invalid role structure" in output
    
    def test_ide_format_with_file_only(self):
        """Test IDE format with only file path."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(
                    code="E300",
                    severity="error",
                    category="generation",
                    message="Template not found",
                    file_path="templates/main.j2",
                )
            ],
            error_count=1,
        )
        
        output = report.to_ide_format()
        
        assert "templates/main.j2: error[E300]: Template not found" in output
    
    def test_ide_format_without_location(self):
        """Test IDE format for errors without file path."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(
                    code="E400",
                    severity="error",
                    category="io",
                    message="Generic error",
                )
            ],
            error_count=1,
        )
        
        output = report.to_ide_format()
        
        assert "(unknown): error[E400]: Generic error" in output
    
    def test_ide_format_with_warnings(self):
        """Test IDE format distinguishes errors and warnings."""
        report = ErrorReport(
            correlation_id="test-ide",
            warnings=[
                ErrorEntry(
                    code="W100",
                    severity="warning",
                    category="parsing",
                    message="Deprecated syntax",
                    file_path="test.yml",
                    line=5,
                )
            ],
            warning_count=1,
        )
        
        output = report.to_ide_format()
        
        assert "test.yml:5: warning[W100]: Deprecated syntax" in output
    
    def test_ide_format_includes_recovery_hints(self):
        """Test IDE format includes recovery suggestions as hints."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="YAML syntax error",
                    file_path="test.yml",
                    line=10,
                    recovery_suggestion="Check indentation at line 10",
                )
            ],
            error_count=1,
        )
        
        output = report.to_ide_format()
        
        assert "test.yml:10: error[E101]: YAML syntax error" in output
        assert "  hint: Check indentation at line 10" in output
    
    def test_ide_format_summary(self):
        """Test IDE format includes summary line."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(code="E101", severity="error", category="parsing", message="Error 1"),
                ErrorEntry(code="E102", severity="error", category="parsing", message="Error 2"),
            ],
            warnings=[
                ErrorEntry(code="W100", severity="warning", category="parsing", message="Warning 1"),
            ],
            error_count=2,
            warning_count=1,
        )
        
        output = report.to_ide_format()
        
        assert "Found 2 error(s), 1 warning(s)" in output
    
    def test_ide_format_includes_suppressed_count(self):
        """Test IDE format shows suppressed count when > 0."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(code="E101", severity="error", category="parsing", message="Error"),
            ],
            error_count=1,
            suppressed_count=3,
        )
        
        output = report.to_ide_format()
        
        assert "Found 1 error(s), 0 warning(s), 3 suppressed" in output
    
    def test_ide_format_multiple_errors_sorted(self):
        """Test IDE format preserves error sorting."""
        report = ErrorReport(
            correlation_id="test-ide",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="First error",
                    file_path="a.yml",
                    line=10,
                ),
                ErrorEntry(
                    code="E102",
                    severity="error",
                    category="parsing",
                    message="Second error",
                    file_path="b.yml",
                    line=5,
                ),
            ],
            error_count=2,
        )
        
        output = report.to_ide_format()
        lines = output.split("\n")
        
        # First error should appear before second
        a_yml_line = next(i for i, line in enumerate(lines) if "a.yml" in line)
        b_yml_line = next(i for i, line in enumerate(lines) if "b.yml" in line)
        assert a_yml_line < b_yml_line
