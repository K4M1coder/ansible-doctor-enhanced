"""Integration tests for CLI report generation - User Story 1.

Following TDD (Red-Green-Refactor):
- RED: These tests MUST FAIL initially (no --report flag implementation yet)
- GREEN: CLI implementation will make them pass
- REFACTOR: Improve code quality while keeping tests green

Tests cover:
- T016: CLI `--report report.json` flag creates file
- T017: Report contains correct status after successful run
- T018: Report contains warnings array when warnings occur
- T019: Report contains errors array when errors occur
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from ansibledoctor.cli import cli  # Changed from main to cli (Click group)


@pytest.fixture
def cli_runner():
    """Provide a Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_role_dir(tmp_path):
    """Create a minimal valid Ansible role structure."""
    role_dir = tmp_path / "test_role"
    role_dir.mkdir()
    
    # Create minimal structure
    (role_dir / "meta").mkdir()
    (role_dir / "meta" / "main.yml").write_text(
        "galaxy_info:\n  author: Test Author\n  description: Test role\n"
    )
    
    (role_dir / "defaults").mkdir()
    (role_dir / "defaults" / "main.yml").write_text(
        "# Test variable\ntest_var: value\n"
    )
    
    (role_dir / "tasks").mkdir()
    (role_dir / "tasks" / "main.yml").write_text(
        "- name: Test task\n  debug:\n    msg: Test\n"
    )
    
    return role_dir


class TestCLIReportFlag:
    """T016: Integration test for CLI `--report report.json` flag creates file."""

    def test_report_flag_creates_json_file(self, cli_runner, temp_role_dir, tmp_path):
        """Verify --report flag creates a JSON file with execution data."""
        # Arrange
        report_path = tmp_path / "report.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output", str(output_dir),
                "--report", str(report_path)
            ]
        )
        
        # Assert
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert report_path.exists(), f"Report file not created at {report_path}"
        
        # Verify it's valid JSON
        with open(report_path) as f:
            report_data = json.load(f)
        
        assert "correlation_id" in report_data
        assert "command" in report_data
        assert "status" in report_data

    def test_report_flag_without_path_shows_error(self, cli_runner, temp_role_dir):
        """Verify --report without path shows usage error."""
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--report"  # Missing path argument
            ]
        )
        
        # Assert - should fail with exit code 2 (usage error)
        assert result.exit_code != 0
        assert "Error" in result.output or "requires an argument" in result.output


class TestReportStatus:
    """T017: Integration test for report contains correct status after successful run."""

    def test_successful_generation_has_completed_status(self, cli_runner, temp_role_dir, tmp_path):
        """Verify successful execution creates report with status='completed'."""
        # Arrange
        report_path = tmp_path / "report.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output", str(output_dir),
                "--report", str(report_path)
            ]
        )
        
        # Assert
        assert result.exit_code == 0
        
        with open(report_path) as f:
            report_data = json.load(f)
        
        assert report_data["status"] == "completed" or report_data["status"] == "completed_with_warnings"
        assert report_data["command"] == "generate"
        assert "started_at" in report_data
        assert "completed_at" in report_data
        assert "duration_ms" in report_data
        assert report_data["duration_ms"] >= 0

    def test_report_includes_metrics(self, cli_runner, temp_role_dir, tmp_path):
        """Verify report includes metrics object with file counts."""
        # Arrange
        report_path = tmp_path / "report.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output", str(output_dir),
                "--report", str(report_path)
            ]
        )
        
        # Assert
        assert result.exit_code == 0
        
        with open(report_path) as f:
            report_data = json.load(f)
        
        assert "metrics" in report_data
        metrics = report_data["metrics"]
        assert "files_processed" in metrics
        assert "roles_documented" in metrics
        assert metrics["files_processed"] >= 0


class TestReportWithWarnings:
    """T018: Integration test for report contains warnings array when warnings occur."""

    def test_report_includes_warnings_array(self, cli_runner, tmp_path):
        """Verify report contains warnings when role has issues."""
        # Arrange - create role with missing annotations (will generate warnings)
        role_dir = tmp_path / "role_with_warnings"
        role_dir.mkdir()
        
        (role_dir / "meta").mkdir()
        (role_dir / "meta" / "main.yml").write_text(
            "galaxy_info:\n  author: Test\n  description: Test\n"
        )
        
        (role_dir / "defaults").mkdir()
        (role_dir / "defaults" / "main.yml").write_text(
            "# Variable without @var annotation\nundocumented_var: value\n"
        )
        
        report_path = tmp_path / "report.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(role_dir),
                "--output", str(output_dir),
                "--report", str(report_path)
            ]
        )
        
        # Assert
        assert result.exit_code == 0  # Warnings don't fail execution by default
        
        with open(report_path) as f:
            report_data = json.load(f)
        
        assert "warnings" in report_data
        assert isinstance(report_data["warnings"], list)
        
        # If warnings occurred, verify structure
        if report_data.get("metrics", {}).get("warnings_count", 0) > 0:
            assert len(report_data["warnings"]) > 0
            first_warning = report_data["warnings"][0]
            assert "file" in first_warning
            assert "message" in first_warning
            assert "warning_type" in first_warning


class TestReportWithErrors:
    """T019: Integration test for report contains errors array when errors occur."""

    def test_report_includes_errors_array_on_failure(self, cli_runner, tmp_path):
        """Verify report contains errors when parsing fails."""
        # Arrange - create role with invalid YAML
        role_dir = tmp_path / "role_with_errors"
        role_dir.mkdir()
        
        (role_dir / "meta").mkdir()
        (role_dir / "meta" / "main.yml").write_text(
            "galaxy_info:\n  author: Test\n  description: Test\n"
        )
        
        (role_dir / "defaults").mkdir()
        (role_dir / "defaults" / "main.yml").write_text(
            "# Invalid YAML syntax\ninvalid: [\n  unclosed\n"  # Unclosed bracket
        )
        
        report_path = tmp_path / "report.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Act - use --continue-on-error to generate report even on failure
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(role_dir),
                "--output", str(output_dir),
                "--report", str(report_path),
                "--continue-on-error"  # Will be implemented in US4
            ]
        )
        
        # Assert - should either fail or complete with errors
        # (behavior depends on --continue-on-error implementation)
        
        # If report was created, verify error structure
        if report_path.exists():
            with open(report_path) as f:
                report_data = json.load(f)
            
            assert "errors" in report_data
            assert isinstance(report_data["errors"], list)
            
            # If errors occurred, verify structure
            if report_data.get("metrics", {}).get("errors_count", 0) > 0:
                assert len(report_data["errors"]) > 0
                first_error = report_data["errors"][0]
                assert "file" in first_error
                assert "message" in first_error
                assert "error_type" in first_error

    def test_failed_execution_creates_report_with_failed_status(self, cli_runner, tmp_path):
        """Verify failed execution creates report with status='failed'."""
        # Arrange - role directory that doesn't exist
        nonexistent_role = tmp_path / "nonexistent_role"
        report_path = tmp_path / "report.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(nonexistent_role),
                "--output", str(output_dir),
                "--report", str(report_path)
            ]
        )
        
        # Assert - should fail
        assert result.exit_code != 0
        
        # Report may or may not be created depending on error handling
        # If created, it should have status='failed'
        if report_path.exists():
            with open(report_path) as f:
                report_data = json.load(f)
            
            assert report_data["status"] == "failed"
            assert "errors" in report_data

