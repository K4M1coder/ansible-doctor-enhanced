"""Unit tests for error code functionality and suppression.

Tests for User Story 4 (Error Classification & Codes):
- T050: Error code uniqueness validation
- T051: --ignore flag with error code suppression
"""

import pytest
from ansibledoctor.exceptions.codes import ErrorCode
from ansibledoctor.exceptions.aggregator import ErrorAggregator


class TestErrorCodeUniqueness:
    """T050: Unit test for error code uniqueness validation."""
    
    def test_all_error_codes_are_unique(self):
        """Verify all ErrorCode enum values are unique (no duplicates)."""
        all_codes = [code.value for code in ErrorCode]
        assert len(all_codes) == len(set(all_codes)), \
            f"Duplicate error codes found: {[code for code in all_codes if all_codes.count(code) > 1]}"
    
    def test_error_codes_follow_hierarchy(self):
        """Verify error codes follow E1xx/E2xx/E3xx/E4xx and W1xx/W2xx/W3xx/W4xx hierarchy."""
        for code_enum in ErrorCode:
            code = code_enum.value
            # Check format: E/W followed by 3 digits
            assert len(code) == 4, f"Error code {code} should be 4 characters (E/W + 3 digits)"
            assert code[0] in ['E', 'W'], f"Error code {code} should start with E or W"
            assert code[1:].isdigit(), f"Error code {code} should have 3 digits after E/W"
            
            # Check hierarchy: E1xx, E2xx, E3xx, E4xx or W1xx, W2xx, W3xx, W4xx
            category = int(code[1])  # First digit after E/W
            assert 1 <= category <= 4, f"Error code {code} should be in E1xx-E4xx or W1xx-W4xx range"
    
    def test_error_code_categories_defined(self):
        """Verify error code categories are properly defined."""
        # Check that generic error codes exist for each category
        assert ErrorCode.E100_PARSING_GENERIC.value == "E100"
        assert ErrorCode.E200_VALIDATION_GENERIC.value == "E200"
        assert ErrorCode.E300_GENERATION_GENERIC.value == "E300"
        assert ErrorCode.E400_IO_GENERIC.value == "E400"
        assert ErrorCode.W100_WARNING_GENERIC.value == "W100"
    
    def test_error_code_enum_names_match_values(self):
        """Verify enum names contain their error code values."""
        for code_enum in ErrorCode:
            # Enum name should contain the code (e.g., E101_YAML_SYNTAX contains "E101")
            assert code_enum.value in code_enum.name, \
                f"Enum name {code_enum.name} should contain code {code_enum.value}"


class TestIgnoreFlagSuppression:
    """T051: Unit test for --ignore flag with error code suppression."""
    
    def test_ignore_single_error_code(self):
        """Test that ErrorAggregator can suppress a single error code."""
        aggregator = ErrorAggregator(ignore_codes=["E101"])
        
        # Add an error with ignored code - should be suppressed
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml")
        
        # Add an error with non-ignored code - should be recorded
        aggregator.add_error("E102", "YAML structure error", file_path="test.yml")
        
        report = aggregator.get_report(correlation_id="test-001")
        
        # Only E102 should be in the error report
        assert len(report.errors) == 1
        assert report.errors[0].code == "E102"
        
        # Suppressed count should be 1
        assert aggregator.suppressed_count == 1
    
    def test_ignore_multiple_error_codes(self):
        """Test that ErrorAggregator can suppress multiple error codes."""
        aggregator = ErrorAggregator(ignore_codes=["E101", "E102", "W103"])
        
        # Add errors with ignored codes
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml")
        aggregator.add_error("E102", "YAML structure error", file_path="test.yml")
        aggregator.add_error("W103", "Undocumented variable", file_path="defaults/main.yml")
        
        # Add an error with non-ignored code
        aggregator.add_error("E201", "Required file missing", file_path="meta/main.yml")
        
        report = aggregator.get_report(correlation_id="test-002")
        
        # Only E201 should be in the error report
        assert len(report.errors) == 1
        assert report.errors[0].code == "E201"
        
        # Suppressed count should be 3
        assert aggregator.suppressed_count == 3
    
    def test_ignore_with_empty_list(self):
        """Test that empty ignore list doesn't suppress any errors."""
        aggregator = ErrorAggregator(ignore_codes=[])
        
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml")
        aggregator.add_error("E102", "YAML structure error", file_path="test.yml")
        
        report = aggregator.get_report(correlation_id="test-003")
        
        # Both errors should be recorded
        assert len(report.errors) == 2
        assert aggregator.suppressed_count == 0
    
    def test_ignore_with_none(self):
        """Test that None ignore_codes doesn't suppress any errors."""
        aggregator = ErrorAggregator(ignore_codes=None)
        
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml")
        aggregator.add_error("E102", "YAML structure error", file_path="test.yml")
        
        report = aggregator.get_report(correlation_id="test-004")
        
        # Both errors should be recorded
        assert len(report.errors) == 2
        assert aggregator.suppressed_count == 0
    
    def test_ignore_codes_case_insensitive(self):
        """Test that error code suppression is case-insensitive."""
        aggregator = ErrorAggregator(ignore_codes=["e101", "w103"])
        
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml")
        aggregator.add_error("W103", "Undocumented variable", file_path="defaults/main.yml")
        aggregator.add_error("E102", "YAML structure error", file_path="test.yml")
        
        report = aggregator.get_report(correlation_id="test-005")
        
        # Only E102 should be in the error report (E101 and W103 suppressed)
        assert len(report.errors) == 1
        assert report.errors[0].code == "E102"
        assert aggregator.suppressed_count == 2
    
    def test_suppressed_errors_not_in_report(self):
        """Test that suppressed errors don't appear in error report at all."""
        aggregator = ErrorAggregator(ignore_codes=["E101"])
        
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml", line=10)
        
        report = aggregator.get_report(correlation_id="test-006")
        
        # No errors in report
        assert len(report.errors) == 0
        
        # But suppressed count should be tracked
        assert aggregator.suppressed_count == 1
    
    def test_ignore_codes_with_warnings(self):
        """Test that ignore_codes can suppress warnings as well as errors."""
        aggregator = ErrorAggregator(ignore_codes=["W102", "W103"])
        
        aggregator.add_error("W102", "Missing documentation", file_path="README.md", severity="warning")
        aggregator.add_error("W103", "Undocumented variable", file_path="defaults/main.yml", severity="warning")
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml", severity="error")
        
        report = aggregator.get_report(correlation_id="test-007")
        
        # Only E101 should be in the report
        assert len(report.errors) == 1
        assert report.errors[0].code == "E101"
        
        # Two warnings should be suppressed
        assert aggregator.suppressed_count == 2


class TestSuppressedCountTracking:
    """T053: Unit test for suppressed error count tracking."""
    
    def test_suppressed_count_initially_zero(self):
        """Test that suppressed_count starts at 0."""
        aggregator = ErrorAggregator()
        assert aggregator.suppressed_count == 0
    
    def test_suppressed_count_increments_correctly(self):
        """Test that suppressed_count increments for each suppressed error."""
        aggregator = ErrorAggregator(ignore_codes=["E101"])
        
        assert aggregator.suppressed_count == 0
        
        aggregator.add_error("E101", "Error 1", file_path="test1.yml")
        assert aggregator.suppressed_count == 1
        
        aggregator.add_error("E101", "Error 2", file_path="test2.yml")
        assert aggregator.suppressed_count == 2
        
        aggregator.add_error("E101", "Error 3", file_path="test3.yml")
        assert aggregator.suppressed_count == 3
    
    def test_suppressed_count_not_affected_by_non_suppressed_errors(self):
        """Test that non-suppressed errors don't affect suppressed_count."""
        aggregator = ErrorAggregator(ignore_codes=["E101"])
        
        aggregator.add_error("E102", "Not suppressed", file_path="test.yml")
        assert aggregator.suppressed_count == 0
        
        aggregator.add_error("E101", "Suppressed", file_path="test.yml")
        assert aggregator.suppressed_count == 1
        
        aggregator.add_error("E103", "Not suppressed", file_path="test.yml")
        assert aggregator.suppressed_count == 1
    
    def test_suppressed_count_with_mixed_errors(self):
        """Test suppressed_count with mix of suppressed and non-suppressed errors."""
        aggregator = ErrorAggregator(ignore_codes=["E101", "E102"])
        
        aggregator.add_error("E101", "Suppressed 1", file_path="test.yml")
        aggregator.add_error("E103", "Not suppressed", file_path="test.yml")
        aggregator.add_error("E102", "Suppressed 2", file_path="test.yml")
        aggregator.add_error("E104", "Not suppressed", file_path="test.yml")
        aggregator.add_error("E101", "Suppressed 3", file_path="test.yml")
        
        assert aggregator.suppressed_count == 3
        
        report = aggregator.get_report(correlation_id="test-008")
        assert len(report.errors) == 2  # Only E103 and E104
