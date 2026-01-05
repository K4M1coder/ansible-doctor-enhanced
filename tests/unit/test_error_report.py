"""Unit tests for ErrorReport model."""

import json
import pytest
from datetime import datetime
from ansibledoctor.models.error_report import ErrorEntry, ErrorReport


class TestErrorEntry:
    """Test ErrorEntry model."""
    
    def test_create_error_entry(self):
        """Test creating error entry."""
        entry = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="YAML syntax error",
            file_path="test.yml",
            line=15,
            column=3,
        )
        
        assert entry.code == "E101"
        assert entry.severity == "error"
        assert entry.category == "parsing"
        assert entry.message == "YAML syntax error"
        assert entry.file_path == "test.yml"
        assert entry.line == 15
        assert entry.column == 3
    
    def test_error_entry_optional_fields(self):
        """Test error entry with optional fields."""
        entry = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="Error"
        )
        
        assert entry.file_path is None
        assert entry.line is None
        assert entry.column is None
        assert entry.recovery_suggestion is None


class TestErrorReportModel:
    """Test ErrorReport model."""
    
    def test_create_error_report(self):
        """Test creating error report."""
        report = ErrorReport(
            correlation_id="test-123",
            errors=[],
            warnings=[],
            error_count=0,
            warning_count=0,
        )
        
        assert report.correlation_id == "test-123"
        assert len(report.errors) == 0
        assert len(report.warnings) == 0
        assert report.error_count == 0
        assert report.warning_count == 0
        assert not report.max_errors_reached
        assert not report.partial_success
    
    def test_error_report_with_errors(self):
        """Test error report with errors."""
        error = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="YAML syntax error"
        )
        
        report = ErrorReport(
            correlation_id="test-123",
            errors=[error],
            error_count=1,
        )
        
        assert len(report.errors) == 1
        assert report.error_count == 1


class TestErrorReportToText:
    """Test ErrorReport.to_text() formatting."""
    
    def test_to_text_no_errors(self):
        """Test text formatting with no errors."""
        report = ErrorReport(
            correlation_id="test-123",
            errors=[],
            warnings=[],
            error_count=0,
            warning_count=0,
        )
        
        text = report.to_text()
        
        assert "ERROR REPORT" in text
        assert "Correlation ID: test-123" in text
        assert "Errors: 0 | Warnings: 0" in text
    
    def test_to_text_with_errors(self):
        """Test text formatting with errors."""
        error = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="YAML syntax error",
            file_path="test.yml",
            line=15,
        )
        
        report = ErrorReport(
            correlation_id="test-123",
            errors=[error],
            error_count=1,
        )
        
        text = report.to_text()
        
        assert "[E101]" in text
        assert "YAML syntax error" in text
        assert "test.yml" in text
        assert "[line 15]" in text
    
    def test_to_text_with_recovery_suggestion(self):
        """Test text formatting includes recovery suggestions."""
        error = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="YAML syntax error",
            recovery_suggestion="Check indentation"
        )
        
        report = ErrorReport(
            correlation_id="test-123",
            errors=[error],
            error_count=1,
        )
        
        text = report.to_text()
        
        assert "💡 Check indentation" in text
    
    def test_to_text_with_doc_url(self):
        """Test text formatting includes documentation URLs."""
        error = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="YAML syntax error",
            doc_url="https://docs.example.com/E101"
        )
        
        report = ErrorReport(
            correlation_id="test-123",
            errors=[error],
            error_count=1,
        )
        
        text = report.to_text()
        
        assert "📖 https://docs.example.com/E101" in text
    
    def test_to_text_groups_by_file(self):
        """Test text formatting groups errors by file."""
        error1 = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="Error 1",
            file_path="file1.yml"
        )
        error2 = ErrorEntry(
            code="E102",
            severity="error",
            category="parsing",
            message="Error 2",
            file_path="file1.yml"
        )
        error3 = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="Error 3",
            file_path="file2.yml"
        )
        
        report = ErrorReport(
            correlation_id="test-123",
            errors=[error1, error2, error3],
            error_count=3,
        )
        
        text = report.to_text()
        
        assert "file1.yml:" in text
        assert "file2.yml:" in text
    
    def test_to_text_with_warnings(self):
        """Test text formatting with warnings."""
        warning = ErrorEntry(
            code="W103",
            severity="warning",
            category="parsing",
            message="Undocumented variable",
        )
        
        report = ErrorReport(
            correlation_id="test-123",
            warnings=[warning],
            warning_count=1,
        )
        
        text = report.to_text()
        
        assert "WARNINGS:" in text
        assert "[W103]" in text
        assert "Undocumented variable" in text
    
    def test_to_text_partial_success(self):
        """Test text formatting shows partial success."""
        report = ErrorReport(
            correlation_id="test-123",
            error_count=1,
            partial_success=True,
        )
        
        text = report.to_text()
        
        assert "Partial success" in text
    
    def test_to_text_max_errors_reached(self):
        """Test text formatting shows max errors warning."""
        report = ErrorReport(
            correlation_id="test-123",
            error_count=1500,
            max_errors_reached=True,
        )
        
        text = report.to_text()
        
        assert "Error limit reached" in text


class TestErrorReportToJson:
    """Test ErrorReport.to_json() serialization."""
    
    def test_to_json_basic(self):
        """Test JSON serialization."""
        report = ErrorReport(
            correlation_id="test-123",
            errors=[],
            warnings=[],
            error_count=0,
            warning_count=0,
        )
        
        json_str = report.to_json()
        data = json.loads(json_str)
        
        assert data["correlation_id"] == "test-123"
        assert data["error_count"] == 0
        assert data["warning_count"] == 0
        assert isinstance(data["errors"], list)
        assert isinstance(data["warnings"], list)
    
    def test_to_json_with_errors(self):
        """Test JSON serialization with errors."""
        error = ErrorEntry(
            code="E101",
            severity="error",
            category="parsing",
            message="YAML syntax error",
            file_path="test.yml",
            line=15,
        )
        
        report = ErrorReport(
            correlation_id="test-123",
            errors=[error],
            error_count=1,
        )
        
        json_str = report.to_json()
        data = json.loads(json_str)
        
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "E101"
        assert data["errors"][0]["message"] == "YAML syntax error"
        assert data["errors"][0]["file_path"] == "test.yml"
        assert data["errors"][0]["line"] == 15
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        report = ErrorReport(
            correlation_id="test-123",
            error_count=0,
        )
        
        data = report.to_dict()
        
        assert isinstance(data, dict)
        assert data["correlation_id"] == "test-123"
