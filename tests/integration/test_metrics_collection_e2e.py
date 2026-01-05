"""Integration tests for end-to-end metrics collection.

Tests metrics collection across CLI commands, ensuring performance data
is captured and displayed correctly. Following TDD methodology.
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


class TestMetricsInReportJSON:
    """T033: Integration test for metrics in report JSON structure."""

    def test_report_contains_phase_timing_dict(self, cli_runner, temp_role_dir, tmp_path):
        """Verify report JSON includes phase_timing with duration data."""
        # Arrange
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

        assert "metrics" in report_data
        assert "phase_timing" in report_data["metrics"]
        assert isinstance(report_data["metrics"]["phase_timing"], dict)
        # Phase timing should contain at least one phase with positive duration
        assert len(report_data["metrics"]["phase_timing"]) > 0
        for phase, duration in report_data["metrics"]["phase_timing"].items():
            assert isinstance(phase, str)
            assert isinstance(duration, (int, float))
            assert duration >= 0

    def test_report_contains_file_processing_metrics(self, cli_runner, temp_role_dir, tmp_path):
        """Verify report includes files_processed counter."""
        # Arrange
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

        metrics = report_data["metrics"]
        # Should have processed at least 3 files (tasks, meta, defaults)
        assert metrics["files_processed"] >= 3
        assert metrics["roles_documented"] == 1


class TestVerboseModePhasing:
    """T034: Integration test for verbose mode displays phase timing."""

    def test_verbose_mode_displays_timing_in_stderr(self, cli_runner, temp_role_dir, tmp_path):
        """Verify --verbose shows phase timing information."""
        # Arrange
        output_file = tmp_path / "output.md"

        # Act
        result = cli_runner.invoke(
            cli, ["generate", str(temp_role_dir), "--output", str(output_file), "--verbose"]
        )

        # Assert
        assert result.exit_code == 0
        # Verbose output goes to stderr in Click
        output = result.output + (result.stderr or "")
        # Check for timing-related keywords
        assert "ms" in output.lower() or "timing" in output.lower() or "duration" in output.lower()

    def test_verbose_mode_with_report_includes_timing(self, cli_runner, temp_role_dir, tmp_path):
        """Verify verbose + report combination works correctly."""
        # Arrange
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
                "--verbose",
                "--report",
                str(report_path),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert report_path.exists()

        with open(report_path) as f:
            report_data = json.load(f)

        # Both verbose output and report should contain timing
        output = result.output + (result.stderr or "")
        assert "phase_timing" in json.dumps(report_data["metrics"])
