"""Unit tests for SARIF 2.1.0 formatter.

Phase 7 - User Story 5: IDE-Friendly Error Output
Tests: T061, T062
"""

from pathlib import Path

from ansibledoctor.models.error_report import ErrorEntry, ErrorReport
from ansibledoctor.utils.sarif import SARIFFormatter


class TestSARIFSchemaValidation:
    """Test SARIF 2.1.0 schema compliance (T061)."""

    def test_sarif_document_has_required_fields(self):
        """Test SARIF document contains required top-level fields."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-123",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="YAML syntax error",
                    file_path="test.yml",
                    line=10,
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)

        # Required top-level fields
        assert "$schema" in sarif
        assert (
            sarif["$schema"]
            == "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
        )
        assert "version" in sarif
        assert sarif["version"] == "2.1.0"
        assert "runs" in sarif
        assert isinstance(sarif["runs"], list)
        assert len(sarif["runs"]) == 1

    def test_sarif_run_has_tool_and_results(self):
        """Test SARIF run contains tool and results."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-456",
            errors=[
                ErrorEntry(
                    code="E200",
                    severity="error",
                    category="validation",
                    message="Invalid role structure",
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)
        run = sarif["runs"][0]

        # Required run fields
        assert "tool" in run
        assert "driver" in run["tool"]
        assert "results" in run
        assert isinstance(run["results"], list)

    def test_sarif_tool_driver_metadata(self):
        """Test SARIF tool driver contains required metadata."""
        formatter = SARIFFormatter(tool_name="ansible-doctor-test", tool_version="1.2.3")

        report = ErrorReport(
            correlation_id="test-789",
            errors=[],
            error_count=0,
        )

        sarif = formatter.format(report)
        driver = sarif["runs"][0]["tool"]["driver"]

        # Tool metadata
        assert driver["name"] == "ansible-doctor-test"
        assert driver["version"] == "1.2.3"
        assert "informationUri" in driver
        assert "rules" in driver

    def test_sarif_rules_from_error_codes(self):
        """Test SARIF rules are generated from unique error codes."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-abc",
            errors=[
                ErrorEntry(code="E101", severity="error", category="parsing", message="Error 1"),
                ErrorEntry(code="E101", severity="error", category="parsing", message="Error 2"),
                ErrorEntry(code="E200", severity="error", category="validation", message="Error 3"),
            ],
            warnings=[
                ErrorEntry(
                    code="W100", severity="warning", category="parsing", message="Warning 1"
                ),
            ],
            error_count=3,
            warning_count=1,
        )

        sarif = formatter.format(report)
        rules = sarif["runs"][0]["tool"]["driver"]["rules"]

        # Should have 3 unique rules (E101, E200, W100)
        assert len(rules) == 3
        rule_ids = {rule["id"] for rule in rules}
        assert rule_ids == {"E101", "E200", "W100"}

        # Each rule should have required fields
        for rule in rules:
            assert "id" in rule
            assert "name" in rule
            assert "shortDescription" in rule
            assert "text" in rule["shortDescription"]
            assert "fullDescription" in rule
            assert "defaultConfiguration" in rule
            assert "level" in rule["defaultConfiguration"]

    def test_sarif_result_structure(self):
        """Test SARIF result objects have correct structure."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-def",
            errors=[
                ErrorEntry(
                    code="E300",
                    severity="error",
                    category="generation",
                    message="Template rendering failed",
                    file_path="templates/main.j2",
                    line=25,
                    column=10,
                    recovery_suggestion="Check template syntax",
                    doc_url="https://docs.example.com/E300",
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)
        result = sarif["runs"][0]["results"][0]

        # Required result fields
        assert "ruleId" in result
        assert result["ruleId"] == "E300"
        assert "level" in result
        assert result["level"] == "error"
        assert "message" in result
        assert "text" in result["message"]
        assert result["message"]["text"] == "Template rendering failed"

        # Location with file path
        assert "locations" in result
        assert len(result["locations"]) == 1
        location = result["locations"][0]
        assert "physicalLocation" in location

        # Fix suggestion
        assert "fixes" in result
        assert len(result["fixes"]) == 1
        assert result["fixes"][0]["description"]["text"] == "Check template syntax"


class TestFileLineColumnFormat:
    """Test file:line:column format generation (T062)."""

    def test_physical_location_with_file_path(self):
        """Test SARIF physical location includes file URI."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-123",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="Parse error",
                    file_path="roles/web/tasks/main.yml",
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report, working_dir=Path("/project"))
        result = sarif["runs"][0]["results"][0]

        assert "locations" in result
        physical_location = result["locations"][0]["physicalLocation"]
        assert "artifactLocation" in physical_location
        assert "uri" in physical_location["artifactLocation"]

    def test_region_with_line_number(self):
        """Test SARIF region includes line number."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-456",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="Parse error",
                    file_path="test.yml",
                    line=42,
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)
        result = sarif["runs"][0]["results"][0]

        region = result["locations"][0]["physicalLocation"]["region"]
        assert "startLine" in region
        assert region["startLine"] == 42

    def test_region_with_line_and_column(self):
        """Test SARIF region includes line and column numbers."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-789",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="Parse error",
                    file_path="test.yml",
                    line=15,
                    column=8,
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)
        result = sarif["runs"][0]["results"][0]

        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startLine"] == 15
        assert region["startColumn"] == 8

    def test_no_location_when_file_path_missing(self):
        """Test SARIF result has no location when file path is missing."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-abc",
            errors=[
                ErrorEntry(
                    code="E400",
                    severity="error",
                    category="io",
                    message="Generic error without file",
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)
        result = sarif["runs"][0]["results"][0]

        assert "locations" not in result or len(result.get("locations", [])) == 0


class TestSARIFInvocationMetadata:
    """Test SARIF invocation metadata (T061)."""

    def test_invocation_success_status(self):
        """Test invocation records execution success status."""
        formatter = SARIFFormatter()

        # Successful execution (no errors)
        report_success = ErrorReport(
            correlation_id="test-success",
            errors=[],
            error_count=0,
        )

        sarif = formatter.format(report_success)
        invocation = sarif["runs"][0]["invocations"][0]
        assert invocation["executionSuccessful"] is True

        # Failed execution (with errors)
        report_fail = ErrorReport(
            correlation_id="test-fail",
            errors=[ErrorEntry(code="E101", severity="error", category="parsing", message="Error")],
            error_count=1,
        )

        sarif = formatter.format(report_fail)
        invocation = sarif["runs"][0]["invocations"][0]
        assert invocation["executionSuccessful"] is False

    def test_invocation_includes_correlation_id(self):
        """Test invocation properties include correlation ID."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-correlation-123",
            errors=[],
            error_count=0,
        )

        sarif = formatter.format(report)
        properties = sarif["runs"][0]["invocations"][0]["properties"]

        assert "correlationId" in properties
        assert properties["correlationId"] == "test-correlation-123"

    def test_invocation_includes_error_counts(self):
        """Test invocation properties include error and warning counts."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-counts",
            errors=[
                ErrorEntry(code="E101", severity="error", category="parsing", message="E1"),
                ErrorEntry(code="E102", severity="error", category="parsing", message="E2"),
            ],
            warnings=[
                ErrorEntry(code="W100", severity="warning", category="parsing", message="W1"),
            ],
            error_count=2,
            warning_count=1,
        )

        sarif = formatter.format(report)
        properties = sarif["runs"][0]["invocations"][0]["properties"]

        assert properties["errorCount"] == 2
        assert properties["warningCount"] == 1
        assert properties["partialSuccess"] is False


class TestSARIFLevelMapping:
    """Test severity to SARIF level mapping (T061)."""

    def test_error_severity_maps_to_error_level(self):
        """Test 'error' severity maps to SARIF 'error' level."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-error",
            errors=[ErrorEntry(code="E101", severity="error", category="parsing", message="Error")],
            error_count=1,
        )

        sarif = formatter.format(report)
        result = sarif["runs"][0]["results"][0]

        assert result["level"] == "error"

    def test_warning_severity_maps_to_warning_level(self):
        """Test 'warning' severity maps to SARIF 'warning' level."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-warning",
            warnings=[
                ErrorEntry(code="W100", severity="warning", category="parsing", message="Warning")
            ],
            warning_count=1,
        )

        sarif = formatter.format(report)
        result = sarif["runs"][0]["results"][0]

        assert result["level"] == "warning"


class TestSARIFHelpUri:
    """Test documentation URL in SARIF rules (T061)."""

    def test_help_uri_from_doc_url(self):
        """Test rule includes helpUri when doc_url is present."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-doc",
            errors=[
                ErrorEntry(
                    code="E101",
                    severity="error",
                    category="parsing",
                    message="Error",
                    doc_url="https://docs.ansible-doctor.com/errors/E101",
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)
        rule = sarif["runs"][0]["tool"]["driver"]["rules"][0]

        assert "helpUri" in rule
        assert rule["helpUri"] == "https://docs.ansible-doctor.com/errors/E101"

    def test_no_help_uri_when_doc_url_missing(self):
        """Test rule has no helpUri when doc_url is None."""
        formatter = SARIFFormatter()

        report = ErrorReport(
            correlation_id="test-no-doc",
            errors=[
                ErrorEntry(
                    code="E999",
                    severity="error",
                    category="parsing",
                    message="Error without docs",
                    doc_url=None,
                )
            ],
            error_count=1,
        )

        sarif = formatter.format(report)
        rule = sarif["runs"][0]["tool"]["driver"]["rules"][0]

        assert "helpUri" not in rule or rule.get("helpUri") is None
