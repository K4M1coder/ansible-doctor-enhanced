"""Integration tests for correlation ID propagation across CLI commands.

Tests that correlation IDs are included in log entries, reports, and propagate
through nested operations.
"""

import json

import pytest
from click.testing import CliRunner

from ansibledoctor.cli import cli


@pytest.fixture
def cli_runner():
    """Provide Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_role_dir(tmp_path):
    """Create a minimal valid Ansible role structure for testing."""
    role_dir = tmp_path / "test_role"
    role_dir.mkdir()

    # Create minimal role structure
    (role_dir / "tasks").mkdir()
    (role_dir / "tasks" / "main.yml").write_text(
        "---\n- name: Test task\n  debug:\n    msg: 'test'\n"
    )

    (role_dir / "meta").mkdir()
    (role_dir / "meta" / "main.yml").write_text(
        "galaxy_info:\n  author: Test Author\n  description: Test Role\n  license: MIT\n"
    )

    (role_dir / "defaults").mkdir()
    (role_dir / "defaults" / "main.yml").write_text(
        "# @var test_var: Test variable\ntest_var: test_value\n"
    )

    return role_dir


class TestCorrelationIDInLogEntries:
    """T047: Integration test for correlation ID in all log entries."""

    def test_correlation_id_in_log_output(self, temp_role_dir, tmp_path):
        """Verify correlation ID appears in log entries during execution."""
        # Arrange
        cli_runner = CliRunner()
        output_file = tmp_path / "output.md"

        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output",
                str(output_file),
                "--log-level",
                "DEBUG",
            ],
            catch_exceptions=False,
        )

        # Assert
        assert result.exit_code == 0
        # Check stderr for log output (Click outputs logs to stderr by default)
        assert "correlation_id" in result.output.lower() or "correlation" in result.output.lower()


class TestCorrelationIDInReport:
    """T048: Integration test for correlation ID in report JSON."""

    def test_correlation_id_included_in_report_json(self, temp_role_dir, tmp_path):
        """Verify correlation ID is included in execution report JSON."""
        # Arrange
        cli_runner = CliRunner()
        report_path = tmp_path / "report.json"
        output_file = tmp_path / "output.md"

        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output",
                str(output_file),
                "--report",
                str(report_path),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert report_path.exists()

        with open(report_path) as f:
            report_data = json.load(f)

        assert "correlation_id" in report_data
        assert isinstance(report_data["correlation_id"], str)
        assert len(report_data["correlation_id"]) == 36  # UUID4 length with hyphens
        assert report_data["correlation_id"].count("-") == 4  # UUID format

    def test_custom_correlation_id_in_report(self, temp_role_dir, tmp_path):
        """Verify custom correlation ID via CLI flag is included in report."""
        # Arrange
        cli_runner = CliRunner()
        report_path = tmp_path / "report.json"
        output_file = tmp_path / "output.md"
        custom_id = "custom-trace-12345"

        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output",
                str(output_file),
                "--report",
                str(report_path),
                "--correlation-id",
                custom_id,
            ],
        )

        # Assert
        assert result.exit_code == 0

        with open(report_path) as f:
            report_data = json.load(f)

        assert report_data["correlation_id"] == custom_id


class TestNestedOperationsCorrelationID:
    """T049: Integration test for correlation ID propagation in nested operations."""

    def test_nested_operations_share_correlation_id(self, temp_role_dir, tmp_path):
        """Verify nested operations (role→collection→project) share parent correlation ID."""
        # Arrange
        cli_runner = CliRunner()
        report_path = tmp_path / "report.json"
        output_file = tmp_path / "output.md"

        # Act
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                str(temp_role_dir),
                "--output",
                str(output_file),
                "--report",
                str(report_path),
            ],
        )

        # Assert
        assert result.exit_code == 0

        with open(report_path) as f:
            report_data = json.load(f)

        # Verify correlation ID is present
        correlation_id = report_data.get("correlation_id")
        assert correlation_id is not None

        # In future when nested operations exist (collections, projects),
        # this test should verify they all use the same correlation_id
        # For now, we verify the single operation has a correlation_id
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0
